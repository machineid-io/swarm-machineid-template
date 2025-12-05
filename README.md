# MachineID.io + OpenAI Swarm Starter Template

A minimal OpenAI Swarm starter that shows how to wrap your workers with MachineID.io device registration and validation.

Use this template to prevent runaway agents, enforce hard device limits, and ensure every Swarm worker checks in before doing work.  
The free org key supports up to 3 devices, with higher limits available on paid plans.


## What this repo gives you

- swarm_agent.py:
  - Reads MACHINEID_ORG_KEY from the environment
  - Uses a default deviceId of swarm-worker-01 (override with MACHINEID_DEVICE_ID)
  - Calls POST /api/v1/devices/register with x-org-key and a deviceId
  - Calls GET /api/v1/devices/validate before running Swarm
  - Prints clear status:
    - ok / exists / restored
    - limit_reached (free tier = 3 devices)
    - allowed / not allowed

- requirements.txt:
  - git+https://github.com/openai/swarm.git
  - requests

This mirrors the same register and validate flow as the machineid-python-starter, but wired into a real OpenAI Swarm agent.


## Quick start

1. Clone this repo or click "Use this template"

git clone https://github.com/machineid-io/swarm-machineid-template.git

cd swarm-machineid-template


2. Install dependencies

For Python 3.11 in a virtual environment:

python3.11 -m venv venv

source venv/bin/activate

pip install -r requirements.txt


3. Get a free org key (supports 3 devices)

Visit https://machineid.io  
Click "Generate free org key"  
Copy the key (it begins with org_)


4. Export your environment variables

export MACHINEID_ORG_KEY=org_your_org_key_here

export OPENAI_API_KEY=sk_your_openai_key_here

Optional:

export MACHINEID_DEVICE_ID=swarm-worker-01


5. Run the starter

python3.11 swarm_agent.py

You will see:

- A register call with plan and usage summary  
- A validate call  
- Either "not allowed / limit reached" or an OpenAI Swarm generated output  


## How the script works

1. Reads MACHINEID_ORG_KEY from the environment.  
2. Uses a default deviceId of swarm-worker-01.  
3. Calls /api/v1/devices/register:
   - ok → new device created
   - exists → device already registered
   - restored → previously revoked device restored
   - limit_reached → free tier cap hit
4. Calls /api/v1/devices/validate:
   - allowed: true → Swarm worker should run
   - allowed: false → Swarm worker should stop or pause

The script only runs the Swarm client when the device is allowed.  
This is the same control cycle used by real fleets.


## Using this in your own Swarm workers

To integrate with MachineID.io:

- Call register when your Swarm worker or process starts.  
- Call validate:
  - Before each Swarm run, or
  - Before each major task, or
  - On a time interval for long-running processes.  
- Only continue execution when allowed is true.  

This prevents accidental over-scaling, infinite agent spawning, and runaway cloud costs.


## Advanced: create orgs programmatically (optional)

Most humans generate a free org key from the dashboard.

Fully automated backends or meta-agents may instead call:

POST /api/v1/org/create

Example:

curl -s https://machineid.io/api/v1/org/create \
  -H "Content-Type: application/json" \
  -d '{}'

The response includes an orgApiKey that works exactly like dashboard-created keys.


## Files in this repo

- swarm_agent.py — Swarm starter with MachineID register and validate
- requirements.txt — Minimal dependencies
- LICENSE — MIT licensed


## Links

Dashboard → https://machineid.io/dashboard  
Generate free org key → https://machineid.io  
Docs → https://machineid.io/docs  
API → https://machineid.io/api  
Python starter template → https://github.com/machineid-io/machineid-python-starter  
CrewAI template → https://github.com/machineid-io/crewai-machineid-template  


## How plans work (quick overview)

- Plans are per org, each with its own orgApiKey.  
- Device limits apply to unique deviceId values registered through /api/v1/devices/register.  
- When you upgrade or change plans, limits update immediately — your agents do not need new code, and your Swarm workers continue running without modification.

MIT licensed · Built by MachineID.io
