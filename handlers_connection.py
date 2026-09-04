"""Connection lifecycle handlers for Cisco Webex Connector."""
from __future__ import annotations
import json
import uuid
from typing import Any, Dict, List
from imperal_sdk import ActionResult, ui
from app import ext, chat
import schemas as s
from webex_client import WebexClient

async def _load_connections(ctx) -> List[Dict[str, Any]]:
    raw = await ctx.store.get("connections")
    if not raw:
        return []
    try:
        return json.loads(raw)
    except Exception:
        return []

async def _save_connections(ctx, connections: List[Dict[str, Any]]) -> None:
    await ctx.store.set("connections", json.dumps(connections))

async def _get_client(ctx, connection_id: str = "") -> WebexClient:
    connections = await _load_connections(ctx)
    if not connections:
        raise ValueError("No Cisco Webex connections configured. Connect an account first.")
    if connection_id:
        for c in connections:
            if c.get("id") == connection_id:
                return WebexClient(access_token=c["access_token"])
        raise ValueError(f"Connection {connection_id} not found.")
    c = connections[0]
    return WebexClient(access_token=c["access_token"])

@chat.function(
    "connect_webex",
    "Connect your own Cisco Webex account by saving your Bearer Access Token.",
    action_type="write",
    chain_callable=True,
    event="cisco-webex-connector.connect_webex",
    effects=["create:connection"],
    data_model=s.ConnectWebexParams
)
async def connect_webex(params: s.ConnectWebexParams, ctx) -> ActionResult:
    """Connect a Cisco Webex account with Bearer Access Token."""
    label = params.label.strip() or "Cisco Webex Account"
    client = WebexClient(access_token=params.access_token)
    try:
        user_info = await client.get_me()
    except Exception as exc:
        return ActionResult.error(f"Failed to authenticate with Cisco Webex: {exc}")

    connections = await _load_connections(ctx)
    conn_id = f"webex_{uuid.uuid4().hex[:8]}"
    masked = f"...{params.access_token[-4:]}" if len(params.access_token) > 4 else "***"
    connections.append({
        "id": conn_id,
        "label": label,
        "access_token": params.access_token,
        "masked_key": masked,
        "user_name": user_info.get("displayName", ""),
        "email": user_info.get("emails", [""])[0] if user_info.get("emails") else ""
    })
    await _save_connections(ctx, connections)

    return ActionResult.ok(
        data={"connection_id": conn_id, "label": label, "user": user_info.get("displayName")},
        summary=f"Successfully connected Cisco Webex as {user_info.get('displayName', label)}."
    )

@chat.function(
    "list_connections",
    "List connected Cisco Webex accounts without exposing credentials.",
    action_type="read",
    chain_callable=True,
    effects=[],
    data_model=s.NoParams
)
async def list_connections(params: s.NoParams, ctx) -> ActionResult:
    """List connected Cisco Webex accounts."""
    connections = await _load_connections(ctx)
    safe = [
        {
            "id": c["id"],
            "label": c.get("label", ""),
            "masked_key": c.get("masked_key", "***"),
            "user_name": c.get("user_name", ""),
            "email": c.get("email", "")
        }
        for c in connections
    ]
    return ActionResult.ok(
        data={"connections": safe, "count": len(safe)},
        summary=f"Found {len(safe)} connected Cisco Webex account(s)."
    )

@chat.function(
    "disconnect_webex",
    "Disconnect a Cisco Webex account and remove stored credentials.",
    action_type="write",
    chain_callable=True,
    event="cisco-webex-connector.disconnect_webex",
    effects=["delete:connection"],
    data_model=s.DisconnectWebexParams
)
async def disconnect_webex(params: s.DisconnectWebexParams, ctx) -> ActionResult:
    """Disconnect a Cisco Webex account."""
    connections = await _load_connections(ctx)
    new_conns = [c for c in connections if c.get("id") != params.connection_id]
    if len(new_conns) == len(connections):
        return ActionResult.error(f"Connection {params.connection_id} not found.")
    await _save_connections(ctx, new_conns)
    return ActionResult.ok(
        data={"connection_id": params.connection_id},
        summary=f"Disconnected Cisco Webex account {params.connection_id}."
    )
