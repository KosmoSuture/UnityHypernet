---
ha: "0.1.docs.infra.linux-servers"
object_type: "research"
creator: "2.1.index"
human: "1.1"
created: "2026-03-04"
status: "active"
visibility: "internal"
flags: ["infrastructure", "deployment", "cost-analysis"]
---

# Linux Server Research — Hypernet Deployment

**Requested by:** Matt Schaeffer (1.1)
**Date:** March 4, 2026
**Purpose:** Find the most cost-effective way to run Hypernet code live with AI swarm

---

## Requirements

- Run Python 3.13 (FastAPI server + swarm orchestrator)
- 24/7 uptime for autonomous swarm operation
- AI instances can upload code updates and work on things live
- SSH access for Matt and the swarm
- Git for code deployment
- Enough RAM for 6 concurrent API-calling workers + FastAPI server
- Low cost (bootstrapping phase)

## Recommendation #1: Oracle Cloud Free Tier — $0/month

**Always Free ARM Instance (Ampere A1)**
- 4 OCPUs, 24 GB RAM, 200 GB block storage
- Ubuntu 22.04 or 24.04
- Truly free forever (not a trial)
- More than enough for swarm + server + monitoring

**Pros:**
- Zero cost, no credit card charges
- 24 GB RAM is massive overkill for current needs
- ARM is efficient, fast for Python workloads
- 200 GB storage handles the entire Hypernet Structure
- Always Free — not a trial that expires

**Cons:**
- Signup can be difficult (capacity limits, credit card verification issues)
- ARM architecture means some Python packages may need compilation
- Oracle Cloud UI is not intuitive
- "Always Free" instances can be reclaimed if idle (keep a cron heartbeat)

**Setup:**
1. Sign up at cloud.oracle.com
2. Create Always Free Ampere A1 Compute instance
3. Install Python 3.13, git, pip
4. Clone Hypernet repo, install dependencies
5. Set up systemd services for `hypernet serve` and `hypernet swarm --archive ../..`
6. Configure firewall for port 8000 (dashboard)

## Recommendation #2: Hetzner CX23 — $3.85/month

**Shared vCPU Cloud Server**
- 2 vCPUs, 4 GB RAM, 40 GB SSD
- Ubuntu 24.04
- Nuremberg/Falkenstein/Helsinki datacenter

**Pros:**
- Extremely cheap for a real cloud server
- Reliable, well-regarded provider
- Simple, clean UI
- x86 architecture — no compatibility issues
- Fast SSD storage

**Cons:**
- 4 GB RAM is tight if all 6 workers run simultaneously (fine for current API-calling workload, tight for local LLM)
- European datacenters add ~100ms latency to US API calls
- Not free

## Recommendation #3: Hetzner CAX11 (ARM) — $3.29/month

- 2 ARM vCPUs, 4 GB RAM, 40 GB SSD
- Same as CX23 but ARM — slightly cheaper
- Same tradeoffs as Oracle ARM but with paid reliability

## Other Options Considered

| Provider | Spec | Price | Notes |
|----------|------|-------|-------|
| AWS Free Tier | t2.micro, 1GB RAM | $0 (12 months) | Too small, expires |
| GCP Free Tier | e2-micro, 1GB RAM | $0 | Too small for swarm |
| DigitalOcean | 1GB droplet | $6/mo | More expensive, less RAM |
| Vultr | 1 vCPU, 1GB | $5/mo | Similar to DO |
| Linode | Nanode 1GB | $5/mo | Good but costs more |

## Deployment Plan

1. **Phase 1 (Now):** Oracle Cloud Free Tier — get the swarm running 24/7 at zero cost
2. **Phase 2 (If Oracle fails):** Hetzner CX23 at $3.85/mo — reliable paid fallback
3. **Phase 3 (Growth):** Hetzner dedicated server or Oracle paid tier when local LLM or more workers are needed

## For LM Studio Integration

If running a local LLM on the server (not just API calls):
- Need minimum 8 GB RAM for small models (Llama 3 8B)
- 16+ GB for medium models (Llama 3 70B quantized)
- Oracle Free Tier's 24 GB makes this feasible
- Hetzner 4 GB does NOT — would need CX32 (8 GB, ~$7.50/mo) or dedicated
