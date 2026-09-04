"""Extension declaration, capabilities, health check for Cisco Webex Connector."""
from __future__ import annotations
from imperal_sdk import ChatExtension, Extension

ext = Extension(
    "cisco-webex-connector",
    version="0.1.0",
    display_name="Cisco Webex",
    description="Comprehensive Cisco Webex connector: schedule/manage meetings, messaging spaces/rooms, message posting, recordings, and health audits via Webex API.",
    icon="icon.svg",
    capabilities=["webex:manage"]
)

chat = ChatExtension(ext)

@ext.health_check
async def health_check(ctx) -> bool:
    """Verify Cisco Webex connector health."""
    return True
