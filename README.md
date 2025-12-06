# MachineID.io + OpenAI Swarm Starter Template
### Add device limits to Swarm workers with one small register/validate block.

A minimal OpenAI Swarm starter showing how to wrap your workers with MachineID.io device registration and validation.

Use this template to prevent runaway agents, enforce hard device limits, and ensure every Swarm worker checks in before doing work.  
The free org key supports **3 devices**, with higher limits available on paid plans.

---

## What this repo gives you

- `swarm_agent.py`:
  - Reads `MACHINEID_ORG_KEY` from the environment  
  - Uses a default `deviceId` of `swarm-worker-01` (override with `MACHINEID_DEVICE_ID`)  
  - Calls **POST** `/api/v1/devices/register` with `x-org-key` and a `deviceId`  
  - Calls **GET** `/api/v1/devices/validate` before running Swarm  
  - Prints clear status:
    - `ok` / `exists` / `restored`  
    - `limit_reached` (free tier = 3 devices)  
    - `allowed` / `not allowed`

- `requirements.txt`:
  - `git+https://github.com/openai/swarm.git`  
  - `requests`

This mirrors the same register + validate pattern used in the Python, LangChain, and CrewAI templates — but wired into a real OpenAI Swarm worker.

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
export MACHINEID_DEVICE_ID=swarm-worker-01   # optional override
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
- A validate call  
- Either **“not allowed / limit reached”** or an OpenAI Swarm-generated output  

---

## How the script works

1. Reads `MACHINEID_ORG_KEY` from the environment  
2. Uses a default `deviceId` of `swarm-worker-01`  
3. Calls `/api/v1/devices/register`:
   - `ok` → new device created  
   - `exists` → device already registered  
   - `restored` → previously revoked device restored  
   - `limit_reached` → free tier cap hit  
4. Calls `/api/v1/devices/validate`:
   - `allowed: true` → worker should run  
   - `allowed: false` → worker should pause or exit  

This ensures each worker checks in before running and keeps scaling safely controlled.

---

## Using this in your own Swarm workers

To integrate MachineID.io:

- Call **register** when your Swarm worker or process starts  
- Call **validate**:
  - Before each Swarm run, or  
  - Before major tasks, or  
  - Periodically for long-running processes  
- Only continue execution when `allowed == true`  

This prevents accidental over-scaling, infinite worker spawning, and runaway cloud costs.

**Drop the same register/validate block into any Swarm worker, background process, or agent.**  
This is all you need to enforce simple device limits across your entire Swarm fleet.

---

## Optional: fully automated org creation

Most users generate a free org key from the dashboard.

If you are building meta-agents or automated back-ends that need to bootstrap from zero, you can create an org + key programmatically:

```bash
curl -X POST https://machineid.io/api/v1/org/create \
  -H "Content-Type: application/json" \
  -d '{}'
```

The response contains a ready-to-use `orgApiKey`.

(This pattern will get its own dedicated template/repo in the future.)

---

## Files in this repo

- `swarm_agent.py` — Swarm starter with MachineID register + validate  
- `requirements.txt` — Minimal dependencies  
- `LICENSE` — MIT licensed  

---

## Links

Dashboard → https://machineid.io/dashboard  
Generate free org key → https://machineid.io  
Docs → https://machineid.io/docs  
API → https://machineid.io/api  

---

## Other templates

→ Python starter: https://github.com/machineid-io/machineid-python-starter  
→ LangChain:      https://github.com/machineid-io/langchain-machineid-template  
→ CrewAI:         https://github.com/machineid-io/crewai-machineid-template  

---

## How plans work (quick overview)

- Plans are per **org**, each with its own `orgApiKey`  
- Device limits apply to unique `deviceId` values registered through `/api/v1/devices/register`  
- When you upgrade or change plans, limits update immediately — your Swarm workers do **not** need new code  

MIT licensed · Built by MachineID.io
