"""Settings panel for Cisco Webex Connector."""
from __future__ import annotations
from imperal_sdk import ui
from app import ext

@ext.panel("__cisco_webex_settings", slot="center")
async def settings_panel(ctx) -> ui.UINode:
    return ui.Stack(
        direction="v",
        gap=3,
        children=[
            ui.Text("Cisco Webex Settings", variant="heading"),
            ui.Text("Manage active Cisco Webex API connections and settings.", variant="body"),
            ui.Divider(),
            ui.Form(
                submit_label="Disconnect Account",
                action=ui.Call("disconnect_webex"),
                children=[
                    ui.Input(
                        param_name="connection_id",
                        placeholder="Connection ID to remove"
                    )
                ]
            )
        ]
    )
