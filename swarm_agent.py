import os
import sys
import time
from typing import Any, Dict

import requests
from swarm import Agent, Swarm

BASE_URL = "https://machineid.io"
REGISTER_URL = f"{BASE_URL}/api/v1/devices/register"
VALIDATE_URL = f"{BASE_URL}/api/v1/devices/validate"


def get_org_key() -> str:
    org_key = os.getenv("MACHINEID_ORG_KEY")
    if not org_key:
        raise RuntimeError(
            "Missing MACHINEID_ORG_KEY. Set it in your environment or via a .env file.\n"
            "Example:\n"
            "  export MACHINEID_ORG_KEY=org_your_key_here\n"
        )
    return org_key.strip()


def get_device_id() -> str:
    return os.getenv("MACHINEID_DEVICE_ID", "swarm-worker-01")


def register_device(org_key: str, device_id: str) -> Dict[str, Any]:
    headers = {
        "x-org-key": org_key,
        "Content-Type": "application/json",
    }
    payload = {
        "deviceId": device_id,
    }

    print(f"→ Registering device '{device_id}' via {REGISTER_URL} ...")
    resp = requests.post(REGISTER_URL, headers=headers, json=payload, timeout=10)
    try:
        data = resp.json()
    except Exception:
        print("❌ Could not parse JSON from register response.")
        print("Status code:", resp.status_code)
        print("Body:", resp.text)
        raise

    status = data.get("status")
    handler = data.get("handler")
    plan_tier = data.get("planTier")
    limit = data.get("limit")
    devices_used = data.get("devicesUsed")
    remaining = data.get("remaining")

    print(f"✔ register response: status={status}, handler={handler}")
    print("Registration summary:")
    if plan_tier is not None:
        print("  planTier    :", plan_tier)
    if limit is not None:
        print("  limit       :", limit)
    if devices_used is not None:
        print("  devicesUsed :", devices_used)
    if remaining is not None:
        print("  remaining   :", remaining)
    print()

    return data


def validate_device(org_key: str, device_id: str) -> Dict[str, Any]:
    headers = {
        "x-org-key": org_key,
    }
    params = {
        "deviceId": device_id,
    }

    print(f"→ Validating device '{device_id}' via {VALIDATE_URL} ...")
    resp = requests.get(VALIDATE_URL, headers=headers, params=params, timeout=10)
    try:
        data = resp.json()
    except Exception:
        print("❌ Could not parse JSON from validate response.")
        print("Status code:", resp.status_code)
        print("Body:", resp.text)
        raise

    status = data.get("status")
    handler = data.get("handler")
    allowed = bool(data.get("allowed", False))
    reason = data.get("reason", "unknown")
    print(f"✔ validate response: status={status}, handler={handler}, allowed={allowed}, reason={reason}")
    print()
    return data


def build_swarm_objects() -> tuple[Swarm, Agent]:
    """
    Build a minimal Swarm setup:
    - One agent
    - One Swarm client
    """
    client = Swarm()

    agent = Agent(
        name="Swarm Worker",
        instructions=(
            "You are a helpful AI agent that creates short, practical 3-step plans for developers "
            "using OpenAI Swarm together with MachineID.io. MachineID.io provides device-level "
            "gating for workers: each worker registers on startup and validates before running tasks, "
            "so teams can prevent runaway scaling and keep their agent fleets predictable and under control. "
            "Keep responses concise, accurate, and focused on how register + validate act as control points "
            "around Swarm workers."
        ),
    )

    return client, agent


def main() -> None:
    # 1) Load org key and device ID
    org_key = get_org_key()
    device_id = get_device_id()

    print("✔ MACHINEID_ORG_KEY loaded:", org_key[:12] + "...")
    print("Using deviceId:", device_id)
    print()

    # 2) Register device with MachineID.io
    reg = register_device(org_key, device_id)
    reg_status = reg.get("status")

    if reg_status == "limit_reached":
        print("🚫 Plan limit reached on register. Swarm run will NOT start.")
        sys.exit(0)

    # Optional small pause to mirror real startup behavior
    print("Waiting 2 seconds before validating...")
    time.sleep(2)

    # 3) Validate device before running Swarm
    val = validate_device(org_key, device_id)
    allowed = bool(val.get("allowed", False))
    reason = val.get("reason", "unknown")

    print("Validation summary:")
    print("  allowed :", allowed)
    print("  reason  :", reason)
    print()

    if not allowed:
        print("🚫 Device is NOT allowed. Swarm run will NOT start.")
        sys.exit(0)

    print("✅ Device is allowed. Building Swarm client and agent and starting the run...")
    print()

    # 4) Build and run the Swarm workflow
    client, agent = build_swarm_objects()

    try:
        response = client.run(
            agent=agent,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Give me a simple, accurate 3-step plan showing how to use OpenAI Swarm workers "
                        "with MachineID.io to ensure controlled scaling. Focus on how registering each "
                        "worker and validating before work prevents runaway spawning or exceeding plan limits."
                    ),
                }
            ],
        )
        last_message = response.messages[-1]["content"]
    except Exception as e:
        print("❌ Error while running Swarm:", str(e))
        sys.exit(1)

    print("✔ Swarm result:")
    print(last_message)
    print()
    print("Done. swarm_agent.py completed successfully.")


if __name__ == "__main__":
    main()
