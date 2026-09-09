"""Connection lifecycle handlers for Cisco Webex Connector."""
from __future__ import annotations
import json
import uuid
from typing import Any, Dict, List
from imperal_sdk import ActionResult, ui
from app import ext, chat
import schemas as s
from webex_client import WebexClient

SECRET_KEY = "webex_connections"

def _parse_connections_doc(raw) -> List[Dict[str, Any]]:
    if not raw:
        return []
    if isinstance(raw, str):
        try:
            val = json.loads(raw)
            if isinstance(val, dict) and "connections" in val:
                return val["connections"]
            if isinstance(val, list):
                return val
            return []
        except Exception:
            return []
    if isinstance(raw, dict):
        if "connections" in raw and isinstance(raw["connections"], list):
            return raw["connections"]
        return [raw]
    if isinstance(raw, list):
        return raw
    return []

async def _load_connections(ctx) -> List[Dict[str, Any]]:
    try:
        raw = await ctx.secrets.get(SECRET_KEY)
        if raw:
            return _parse_connections_doc(raw)
    except Exception:
        pass
    try:
        raw_store = await ctx.store.get("connections")
        if raw_store:
            data = raw_store.data if hasattr(raw_store, "data") else raw_store
            return _parse_connections_doc(data)
    except Exception:
        pass
    return []

async def _save_connections(ctx, connections: List[Dict[str, Any]]) -> None:
    try:
        await ctx.secrets.set(SECRET_KEY, json.dumps(connections))
    except Exception:
        pass
    try:
        await ctx.store.set("connections", {"connections": connections})
    except Exception:
        pass

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
    "list_connections",
    "List connected Cisco Webex accounts without exposing credentials.",
    action_type="read",
    chain_callable=True,
    event="cisco-webex-connector.list_connections",
    effects=[],
    data_model=s.NoParams
)
async def list_connections(ctx, params: s.NoParams) -> ActionResult:
    """List Cisco Webex connections."""
    connections = await _load_connections(ctx)
    result = []
    for c in connections:
        token = c.get("access_token", "")
        masked_token = f"***{token[-4:]}" if len(token) >= 4 else "***"
        result.append({
            "id": c.get("id"),
            "label": c.get("label", "Cisco Webex"),
            "status": "connected" if c.get("is_active", True) else "disconnected",
            "masked_token": masked_token
        })
    return ActionResult.success(
        data={"connections": result, "count": len(result)},
        summary=f"Found {len(result)} Cisco Webex connection(s)."
    )

@chat.function(
    "connect_webex",
    "Connect your own Cisco Webex account by saving your Bearer Access Token.",
    action_type="write",
    chain_callable=True,
    event="cisco-webex-connector.connect_webex",
    effects=["create:connection"],
    data_model=s.ConnectWebexParams
)
async def connect_webex(ctx, params: s.ConnectWebexParams) -> ActionResult:
    """Connect a Cisco Webex account."""
    label = params.label.strip() or "Cisco Webex"
    access_token = params.access_token.strip()
    
    client = WebexClient(access_token=access_token)
    try:
        await client.get_me()
    except Exception as e:
        return ActionResult.error(f"Failed to connect to Cisco Webex: {e}")
        
    conn_id = f"webex_{uuid.uuid4().hex[:8]}"
    connections = await _load_connections(ctx)
    connections.append({
        "id": conn_id,
        "label": label,
        "access_token": access_token,
        "is_active": True
    })
    await _save_connections(ctx, connections)
    
    return ActionResult.success(
        data={"id": conn_id, "label": label, "status": "connected"},
        summary=f"Connected Cisco Webex account '{label}'."
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
async def disconnect_webex(ctx, params: s.DisconnectWebexParams) -> ActionResult:
    """Disconnect a Cisco Webex account."""
    connections = await _load_connections(ctx)
    orig_len = len(connections)
    connections = [c for c in connections if c.get("id") != params.connection_id]
    if len(connections) == orig_len:
        return ActionResult.error(f"Connection {params.connection_id} not found.")
    await _save_connections(ctx, connections)
    return ActionResult.success(
        data={"id": params.connection_id, "status": "disconnected"},
        summary=f"Disconnected Cisco Webex account {params.connection_id}."
    )
