"""
Hypernet Work Coordinator

Self-organization layer for the AI swarm. Sits between the TaskQueue and the
Swarm orchestrator to add intelligence to task assignment:

  TaskDecomposer    — Break complex tasks into subtasks with dependencies
  CapabilityMatcher — Score worker-task affinity based on tags, history, load
  WorkCoordinator   — Combine decomposition + matching + conflict detection

This is what makes the swarm self-organizing rather than round-robin.

Usage:
    coordinator = WorkCoordinator(task_queue, workers)

    # Decompose a complex task
    subtasks = coordinator.decompose_task(complex_task, [
        {"title": "Design API", "tags": ["code", "architecture"], "priority": "high"},
        {"title": "Write tests", "tags": ["code", "testing"], "depends_on": [0]},
    ])

    # Find best worker for a task
    best = coordinator.match(task_node)

    # Detect collisions
    conflicts = coordinator.detect_conflicts()
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Any

from .address import HypernetAddress
from .node import Node
from .tasks import TaskQueue, TaskPriority, TaskStatus
from .identity import InstanceProfile

log = logging.getLogger(__name__)


@dataclass
class CapabilityProfile:
    """What a worker is good at — derived from tags, history, and explicit config."""
    name: str
    tags: list[str] = field(default_factory=list)       # e.g. ["code", "governance", "writing"]
    strengths: dict[str, float] = field(default_factory=dict)  # tag → affinity score 0-1
    tasks_completed: int = 0
    tasks_failed: int = 0
    current_load: int = 0  # Tasks currently assigned
    avg_duration_seconds: float = 0.0

    @property
    def success_rate(self) -> float:
        total = self.tasks_completed + self.tasks_failed
        if total == 0:
            return 1.0  # Assume perfect until proven otherwise
        return self.tasks_completed / total

    @property
    def is_idle(self) -> bool:
        return self.current_load == 0


@dataclass
class DecompositionPlan:
    """A plan for breaking a complex task into subtasks."""
    parent_task: Node
    subtasks: list[Node] = field(default_factory=list)
    dependency_map: dict[str, list[str]] = field(default_factory=dict)  # addr → [dep_addrs]


@dataclass
class ConflictReport:
    """Detected coordination conflict between workers."""
    conflict_type: str   # "file_collision", "task_overlap", "resource_contention"
    workers: list[str]
    task_addresses: list[str]
    description: str
    severity: str = "low"  # low, medium, high


class TaskDecomposer:
    """Break complex tasks into subtasks with dependency chains.

    Given a parent task and a list of subtask specifications, creates
    real task nodes in the queue with proper dependency links.
    """

    def __init__(self, task_queue: TaskQueue):
        self.task_queue = task_queue

    def decompose(
        self,
        parent_task: Node,
        subtask_specs: list[dict],
    ) -> DecompositionPlan:
        """Create subtasks from a decomposition plan.

        Args:
            parent_task: The complex task being decomposed
            subtask_specs: List of dicts, each with:
                - title (required)
                - description (optional)
                - tags (optional)
                - priority (optional, inherits from parent)
                - depends_on (optional): list of indices into subtask_specs

        Returns:
            DecompositionPlan with created subtask nodes
        """
        parent_priority = parent_task.data.get("priority", "normal")
        parent_tags = parent_task.data.get("tags", [])
        parent_addr = parent_task.address

        created: list[Node] = []
        addr_by_index: dict[int, HypernetAddress] = {}

        # First pass: create all subtasks (without deps)
        for i, spec in enumerate(subtask_specs):
            tags = spec.get("tags", [])
            # Inherit parent tags that aren't already present
            for t in parent_tags:
                if t not in tags:
                    tags.append(t)

            priority_str = spec.get("priority", parent_priority)
            try:
                priority = TaskPriority(priority_str)
            except ValueError:
                priority = TaskPriority.NORMAL

            task = self.task_queue.create_task(
                title=spec["title"],
                description=spec.get("description", ""),
                priority=priority,
                created_by=parent_addr,
                tags=tags,
            )
            created.append(task)
            addr_by_index[i] = task.address

        # Second pass: add dependency links
        dep_map = {}
        for i, spec in enumerate(subtask_specs):
            dep_indices = spec.get("depends_on", [])
            if dep_indices:
                dep_addrs = [addr_by_index[j] for j in dep_indices if j in addr_by_index]
                if dep_addrs:
                    # Recreate the task with dependencies
                    task_node = self.task_queue.store.get_node(addr_by_index[i])
                    for dep_addr in dep_addrs:
                        from .link import Link
                        self.task_queue.store.put_link(Link(
                            from_address=addr_by_index[i],
                            to_address=dep_addr,
                            link_type="0.6.3",
                            relationship="depends_on",
                        ))
                    # Mark as blocked
                    task_node.data["status"] = TaskStatus.BLOCKED.value
                    task_node.update_data()
                    self.task_queue.store.put_node(task_node)
                    dep_map[str(addr_by_index[i])] = [str(a) for a in dep_addrs]

        # Mark parent as decomposed
        parent_task.data["decomposed"] = True
        parent_task.data["subtask_count"] = len(created)
        parent_task.data["subtask_addresses"] = [str(t.address) for t in created]
        parent_task.update_data()
        self.task_queue.store.put_node(parent_task)

        plan = DecompositionPlan(
            parent_task=parent_task,
            subtasks=created,
            dependency_map=dep_map,
        )
        log.info(
            f"Decomposed '{parent_task.data.get('title')}' into "
            f"{len(created)} subtasks ({len(dep_map)} with dependencies)"
        )
        return plan

    def suggest_decomposition(self, task: Node) -> list[dict]:
        """Suggest a decomposition for a task based on its metadata.

        This is a heuristic-based decomposition. In live mode, the swarm
        could use an LLM to generate more intelligent decompositions.
        Returns a list of subtask specs suitable for decompose().
        """
        title = task.data.get("title", "")
        description = task.data.get("description", "")
        tags = task.data.get("tags", [])

        subtasks = []

        # If description mentions distinct phases, create subtasks for each
        if any(keyword in description.lower() for keyword in ["phase", "step", "stage"]):
            subtasks.append({
                "title": f"Plan: {title}",
                "description": f"Create a detailed plan for: {description}",
                "tags": tags + ["planning"],
                "priority": "high",
            })
            subtasks.append({
                "title": f"Implement: {title}",
                "description": f"Implement the plan for: {description}",
                "tags": tags + ["implementation"],
                "depends_on": [0],
            })
            subtasks.append({
                "title": f"Test: {title}",
                "description": f"Test the implementation of: {description}",
                "tags": tags + ["testing"],
                "depends_on": [1],
            })
        # Code tasks get plan → implement → test
        elif "code" in tags or "implementation" in tags:
            subtasks.append({
                "title": f"Design: {title}",
                "tags": tags + ["design"],
                "priority": "high",
            })
            subtasks.append({
                "title": f"Implement: {title}",
                "tags": tags + ["implementation"],
                "depends_on": [0],
            })
            subtasks.append({
                "title": f"Test: {title}",
                "tags": tags + ["testing"],
                "depends_on": [1],
            })
        # Documentation tasks
        elif "docs" in tags or "documentation" in tags:
            subtasks.append({
                "title": f"Draft: {title}",
                "tags": tags + ["draft"],
            })
            subtasks.append({
                "title": f"Review: {title}",
                "tags": tags + ["review"],
                "depends_on": [0],
            })
        # Default: just clone the task as-is (no decomposition needed)
        else:
            return []

        return subtasks


class CapabilityMatcher:
    """Match workers to tasks based on capability profiles.

    Scoring factors:
      1. Tag affinity — worker has matching tags/strengths
      2. Success rate — workers with higher success rates score higher
      3. Load balance — prefer idle workers
      4. Specialization — workers with narrow specialization score higher for matching tasks
    """

    def __init__(self):
        self.profiles: dict[str, CapabilityProfile] = {}

    def register_worker(self, profile: CapabilityProfile) -> None:
        """Register or update a worker's capability profile."""
        self.profiles[profile.name] = profile

    def build_profile_from_stats(
        self,
        name: str,
        identity: InstanceProfile,
        worker_stats: dict,
        current_task: Optional[str] = None,
    ) -> CapabilityProfile:
        """Build a CapabilityProfile from swarm worker statistics."""
        tags = list(identity.tags) if identity.tags else []
        # Infer capabilities from identity
        if identity.capabilities:
            tags.extend(identity.capabilities)

        completed = worker_stats.get("tasks_completed", 0)
        failed = worker_stats.get("tasks_failed", 0)
        duration = worker_stats.get("total_duration_seconds", 0.0)
        total = completed + failed
        avg_duration = duration / total if total > 0 else 0.0

        profile = CapabilityProfile(
            name=name,
            tags=tags,
            tasks_completed=completed,
            tasks_failed=failed,
            current_load=1 if current_task else 0,
            avg_duration_seconds=avg_duration,
        )
        self.profiles[name] = profile
        return profile

    def score_affinity(self, worker_name: str, task: Node) -> float:
        """Score how well a worker fits a task (0.0 to 1.0)."""
        profile = self.profiles.get(worker_name)
        if not profile:
            return 0.5  # Unknown worker gets neutral score

        task_tags = set(task.data.get("tags", []))
        worker_tags = set(profile.tags)
        score = 0.0

        # 1. Tag overlap (0-0.4)
        if task_tags and worker_tags:
            overlap = len(task_tags & worker_tags) / len(task_tags)
            score += overlap * 0.4
        elif not task_tags:
            score += 0.2  # No tags = any worker is fine

        # 2. Explicit strength scores (0-0.2)
        if profile.strengths and task_tags:
            strength_scores = [
                profile.strengths.get(tag, 0.0) for tag in task_tags
            ]
            if strength_scores:
                score += (sum(strength_scores) / len(strength_scores)) * 0.2

        # 3. Success rate (0-0.2)
        score += profile.success_rate * 0.2

        # 4. Load balance (0-0.2) — idle workers get full bonus
        if profile.is_idle:
            score += 0.2
        elif profile.current_load == 1:
            score += 0.1
        # Workers with 2+ tasks get no load bonus

        return min(1.0, score)

    def match(self, task: Node, worker_names: Optional[list[str]] = None) -> Optional[str]:
        """Find the best worker for a task.

        Args:
            task: The task node to match
            worker_names: Optional list of workers to consider (defaults to all registered)

        Returns:
            Name of the best-matching worker, or None if no workers available
        """
        candidates = worker_names or list(self.profiles.keys())
        if not candidates:
            return None

        scores = {name: self.score_affinity(name, task) for name in candidates}
        best = max(scores, key=scores.get)
        log.info(
            f"Matched task '{task.data.get('title', '?')}' → {best} "
            f"(score={scores[best]:.2f}, candidates={len(candidates)})"
        )
        return best

    def rank(self, task: Node, worker_names: Optional[list[str]] = None) -> list[tuple[str, float]]:
        """Rank all workers by affinity for a task.

        Returns list of (worker_name, score) sorted by score descending.
        """
        candidates = worker_names or list(self.profiles.keys())
        scores = [(name, self.score_affinity(name, task)) for name in candidates]
        return sorted(scores, key=lambda x: x[1], reverse=True)


class WorkCoordinator:
    """Top-level coordinator that combines decomposition, matching, and conflict detection.

    This is the main interface the swarm orchestrator uses for self-organization.
    """

    def __init__(self, task_queue: TaskQueue):
        self.task_queue = task_queue
        self.decomposer = TaskDecomposer(task_queue)
        self.matcher = CapabilityMatcher()

    def decompose_task(self, task: Node, subtask_specs: list[dict]) -> DecompositionPlan:
        """Decompose a complex task into subtasks."""
        return self.decomposer.decompose(task, subtask_specs)

    def suggest_decomposition(self, task: Node) -> list[dict]:
        """Get a suggested decomposition for a task."""
        return self.decomposer.suggest_decomposition(task)

    def match(self, task: Node, worker_names: Optional[list[str]] = None) -> Optional[str]:
        """Find the best worker for a task."""
        return self.matcher.match(task, worker_names)

    def rank_workers(self, task: Node, worker_names: Optional[list[str]] = None) -> list[tuple[str, float]]:
        """Rank workers by affinity for a task."""
        return self.matcher.rank(task, worker_names)

    def detect_conflicts(self, worker_tasks: dict[str, list[str]]) -> list[ConflictReport]:
        """Detect coordination conflicts between workers.

        Args:
            worker_tasks: dict of worker_name → list of task addresses currently assigned

        Returns:
            List of ConflictReport for any detected issues
        """
        conflicts = []

        # Check for task overlap — same task assigned to multiple workers
        task_owners: dict[str, list[str]] = {}
        for worker, tasks in worker_tasks.items():
            for task_addr in tasks:
                task_owners.setdefault(task_addr, []).append(worker)

        for task_addr, owners in task_owners.items():
            if len(owners) > 1:
                conflicts.append(ConflictReport(
                    conflict_type="task_overlap",
                    workers=owners,
                    task_addresses=[task_addr],
                    description=f"Task {task_addr} assigned to multiple workers: {', '.join(owners)}",
                    severity="high",
                ))

        # Check for file collision — workers editing the same area
        # (This is a heuristic: if two tasks have overlapping tags suggesting
        # they touch the same module, flag it)
        worker_tag_sets: dict[str, set] = {}
        for worker, tasks in worker_tasks.items():
            tags = set()
            for task_addr in tasks:
                node = self.task_queue.store.get_node(HypernetAddress.parse(task_addr))
                if node:
                    tags.update(node.data.get("tags", []))
            worker_tag_sets[worker] = tags

        workers = list(worker_tag_sets.keys())
        for i in range(len(workers)):
            for j in range(i + 1, len(workers)):
                w1, w2 = workers[i], workers[j]
                overlap = worker_tag_sets[w1] & worker_tag_sets[w2]
                # Only flag if there's meaningful tag overlap (code modules, not generic tags)
                meaningful = overlap - {"test", "testing", "automated", "code", "docs"}
                if meaningful:
                    conflicts.append(ConflictReport(
                        conflict_type="resource_contention",
                        workers=[w1, w2],
                        task_addresses=worker_tasks[w1] + worker_tasks[w2],
                        description=(
                            f"Workers {w1} and {w2} have overlapping focus areas: "
                            f"{', '.join(meaningful)}"
                        ),
                        severity="medium",
                    ))

        return conflicts

    def suggest_rebalance(
        self,
        worker_loads: dict[str, int],
    ) -> list[dict]:
        """Suggest task reassignments for better load distribution.

        Args:
            worker_loads: dict of worker_name → number of tasks assigned

        Returns:
            List of rebalance suggestions, each a dict with from_worker, to_worker, reason
        """
        if not worker_loads:
            return []

        avg_load = sum(worker_loads.values()) / len(worker_loads)
        overloaded = [(w, l) for w, l in worker_loads.items() if l > avg_load + 1]
        underloaded = [(w, l) for w, l in worker_loads.items() if l < avg_load - 0.5]

        suggestions = []
        for over_w, over_l in overloaded:
            for under_w, under_l in underloaded:
                tasks_to_move = min(
                    over_l - int(avg_load),
                    int(avg_load) - under_l + 1,
                )
                if tasks_to_move > 0:
                    suggestions.append({
                        "from_worker": over_w,
                        "to_worker": under_w,
                        "tasks_to_move": tasks_to_move,
                        "reason": f"{over_w} has {over_l} tasks, {under_w} has {under_l}",
                    })

        return suggestions

    def stats(self) -> dict[str, Any]:
        """Coordinator statistics."""
        available = self.task_queue.get_available_tasks()
        profiles = self.matcher.profiles
        return {
            "registered_workers": len(profiles),
            "available_tasks": len(available),
            "worker_profiles": {
                name: {
                    "tags": p.tags,
                    "success_rate": round(p.success_rate, 2),
                    "completed": p.tasks_completed,
                    "failed": p.tasks_failed,
                    "load": p.current_load,
                }
                for name, p in profiles.items()
            },
        }
