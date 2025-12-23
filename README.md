# MachineID + OpenAI Swarm Starter Template
### Add hard device limits to Swarm workers with one small register/validate block.

A minimal OpenAI Swarm starter showing how to wrap your workers with MachineID device registration and validation.

Use this template to prevent runaway agents, enforce hard device limits, and ensure every Swarm worker checks in before doing work.  
The free org key supports **3 devices**, with higher limits available on paid plans.

---

## ⚠️ Python version note (important for Swarm users)

OpenAI Swarm and supporting libraries can depend on packages that do not support Python 3.13+ yet.

To avoid installation errors, the safest recommended environment is:

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Python **3.11** is the most stable choice for Swarm today.

---

## What this repo gives you

- `swarm_agent.py`:
  - Reads `MACHINEID_ORG_KEY` from the environment  
  - Uses a default `deviceId` of `swarm:worker-01` (override with `MACHINEID_DEVICE_ID`)  
  - Calls **POST** `/api/v1/devices/register` with `x-org-key` and a `deviceId`  
  - Calls **POST** `/api/v1/devices/validate` (canonical) before running Swarm  
  - Enforces a **hard gate**:
    - If `allowed == false`, execution stops immediately  
  - Prints stable decision metadata:
    - `allowed`
    - `code`
    - `request_id`

- `requirements.txt`:
  - `git+https://github.com/openai/swarm.git`  
  - `requests`

This mirrors the same register + validate pattern used in the Python, LangChain, and CrewAI templates.

---

## Quick start

### 1. Clone this repo or click **“Use this template.”**

```bash
git clone https://github.com/machineid-io/swarm-machineid-template.git
cd swarm-machineid-template
```

---

### 2. Install dependencies (Python 3.11 + venv recommended)

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 3. Get a free org key (supports 3 devices)

Visit https://machineid.io  
Click **“Generate free org key”**  
Copy the key (it begins with `org_`)

---

### 4. Export your environment variables

```bash
export MACHINEID_ORG_KEY=org_your_org_key_here
export OPENAI_API_KEY=sk_your_openai_key_here
```

Optional override:

```bash
export MACHINEID_DEVICE_ID=swarm:worker-01
```

**One-liner (run immediately):**

```bash
MACHINEID_ORG_KEY=org_xxx OPENAI_API_KEY=sk_xxx python3.11 swarm_agent.py
```

---

### 5. Run the starter

```bash
python3.11 swarm_agent.py
```

You will see:

- A register call with plan + usage summary  
- A validate decision (`allowed/code/request_id`)  
- Either an immediate stop (not allowed) or a Swarm-generated output  

---

## How the script works

1. The worker registers itself with MachineID (idempotent)  
2. It validates (POST, canonical) before running any work  
3. If `allowed == true`, it runs the Swarm workflow  
4. If `allowed == false`, it exits immediately (hard gate)  

This ensures every worker checks in before running and keeps scaling safely controlled.

---

## Using this in your own Swarm workers

To integrate MachineID:

- Call **register** when your worker starts  
- Call **validate**:
  - Before each Swarm run  
  - Before major tasks  
  - Or periodically for long-running agents  
- Stop execution immediately when `allowed == false`  

Drop the same register/validate block into any Swarm worker, agent, or background process.

---

## Files in this repo

- `swarm_agent.py` — Swarm starter with MachineID register + validate  
- `requirements.txt` — Dependencies  
- `LICENSE` — MIT licensed  

---

## Links

Dashboard → https://machineid.io/dashboard  
Generate free org key → https://machineid.io  
Docs → https://machineid.io/docs   

---

## Other templates

→ Python starter: https://github.com/machineid-io/machineid-python-starter  
→ LangChain:      https://github.com/machineid-io/langchain-machineid-template  
→ CrewAI:         https://github.com/machineid-io/crewai-machineid-template  

---

## How plans work (quick overview)

- Plans are per **org**, each with its own `orgApiKey`  
- Device limits apply to unique `deviceId` values registered via `/api/v1/devices/register`  
- Plan changes take effect immediately — workers do not need new code  

MIT licensed · Built by MachineID
