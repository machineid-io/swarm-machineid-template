#!/usr/bin/env python3

import os
import sys
import time
from typing import Any, Dict, Tuple

import requests
from swarm import Agent, Swarm

BASE_URL = os.getenv("MACHINEID_BASE_URL", "https://machineid.io").rstrip("/")
REGISTER_URL = f"{BASE_URL}/api/v1/devices/register"
VALIDATE_URL = f"{BASE_URL}/api/v1/devices/validate"


def env(name: str, default: str | None = None) -> str | None:
    v = os.getenv(name)
    if v is None:
        return default
    v = v.strip()
    return v if v else default


def must_env(name: str) -> str:
    v = env(name)
    if not v:
        raise RuntimeError(
            f"Missing {name}.\n"
            "Example:\n"
            "  export MACHINEID_ORG_KEY=org_your_key_here\n"
            "  export OPENAI_API_KEY=sk_your_openai_key_here\n"
        )
    return v


def get_org_key() -> str:
    return must_env("MACHINEID_ORG_KEY")


def get_device_id() -> str:
    # Stable, non-identifying default (no hostname / user info).
    return env("MACHINEID_DEVICE_ID", "swarm:worker-01") or "swarm:worker-01"


def post_json(url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout_s: int = 12) -> Dict[str, Any]:
    resp = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
    try:
        data = resp.json()
    except Exception:
        return {"status": "error", "error": f"Non-JSON response (HTTP {resp.status_code})", "http": resp.status_code, "body": resp.text}

    if resp.status_code >= 400:
        if isinstance(data, dict) and data.get("error"):
            return {"status": "error", "error": data.get("error"), "http": resp.status_code}
        return {"status": "error", "error": f"HTTP {resp.status_code}", "http": resp.status_code, "body": data}

    return data


def register_device(org_key: str, device_id: str) -> Dict[str, Any]:
    headers = {"x-org-key": org_key, "Content-Type": "application/json"}
    payload = {"deviceId": device_id}

    print(f"→ Registering device '{device_id}'")
    data = post_json(REGISTER_URL, headers, payload)

    print(f"✔ register status={data.get('status')}")
    # Treat only ok/exists as success.
    if data.get("status") not in ("ok", "exists"):
        if data.get("status") == "limit_reached":
            print("🚫 Plan limit reached on register. Swarm worker should NOT start.")
        else:
            print(f"🚫 Register failed: {data}")
    return data


def validate_device(org_key: str, device_id: str) -> Dict[str, Any]:
    headers = {"x-org-key": org_key, "Content-Type": "application/json"}
    payload = {"deviceId": device_id}

    print(f"→ Validating device '{device_id}' (POST canonical)")
    data = post_json(VALIDATE_URL, headers, payload)

    allowed = data.get("allowed")
    code = data.get("code")
    request_id = data.get("request_id")
    print(f"✔ decision allowed={allowed} code={code} request_id={request_id}")
    return data


def build_swarm_objects() -> Tuple[Swarm, Agent]:
    """
    Minimal Swarm setup:
    - One agent
    - One Swarm client
    """
    client = Swarm()

    agent = Agent(
        name="Swarm Worker",
        instructions=(
            "You create short, practical 3-step plans for developers using OpenAI Swarm together with MachineID. "
            "MachineID is a lightweight device-level gate: each worker has a deviceId, registers once, and validates "
            "before running tasks so teams can enforce simple device limits and prevent runaway scaling.\n\n"
            "Focus ONLY on:\n"
            "- assigning a deviceId per worker,\n"
            "- registering the worker,\n"
            "- validating before work, and\n"
            "- stopping workers when validation fails or limits are reached.\n\n"
            "Do NOT describe MachineID as monitoring, analytics, observability, or spend tracking."
        ),
    )

    return client, agent


def main() -> None:
    # Required env
    org_key = get_org_key()
    _ = must_env("OPENAI_API_KEY")  # Swarm/OpenAI provider requires it; fail fast with clear error.

    device_id = get_device_id()

    print("✔ MACHINEID_ORG_KEY loaded:", org_key[:12] + "...")
    print("Using base_url:", BASE_URL)
    print("Using device_id:", device_id)
    print()

    # 1) Register (idempotent). Only ok/exists is success.
    reg = register_device(org_key, device_id)
    if reg.get("status") not in ("ok", "exists"):
        sys.exit(1)

    # 2) Validate (hard gate)
    time.sleep(1)
    val = validate_device(org_key, device_id)

    allowed = bool(val.get("allowed", False))
    code = val.get("code")
    request_id = val.get("request_id")

    if not allowed:
        print("🚫 Execution denied (hard gate). Swarm run will NOT start.")
        print(f"   code={code} request_id={request_id}")
        sys.exit(0)

    print("✅ Execution allowed. Starting Swarm run.\n")

    # 3) Run Swarm workflow
    client, agent = build_swarm_objects()

    try:
        response = client.run(
            agent=agent,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Give me a simple, accurate 3-step plan showing how to use OpenAI Swarm workers with MachineID "
                        "to keep scaling under control. Focus ONLY on deviceId, register, validate, and stopping workers "
                        "when validation fails or limits are reached."
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
