"""Session Manager (sm) — bounded executor for AI session lifecycle.

Implements the bounded-executor half of Tally's Master Controller design
(2.7.28). v1 scope: roster + workers + commands queue + heartbeats +
fail-closed kill. Autonomous spawn loop deferred.
"""
__version__ = "0.1.0"
