"""Panel UI for Cisco Webex Connector following UI_INTERFACE_STANDARD.md."""
from __future__ import annotations
from imperal_sdk import ui
from app import ext
import handlers_connection as h

def _settings_button() -> ui.UINode:
    return ui.Button(
        "App settings",
        variant="secondary",
        size="sm",
        icon="settings",
        on_click=ui.Call("__cisco_webex_settings")
    )

def _help_modal() -> ui.UINode:
    return ui.Modal(
        trigger=ui.Button("How do I set this up?", variant="ghost", size="sm"),
        title="Connecting Cisco Webex",
        children=[
            ui.Text(
                "1. Log in to Webex for Developers (developer.webex.com).\n"
                "2. Create a Bot or Integration to obtain your Bearer Access Token.\n"
                "3. Paste your token below and click Connect Webex.",
                variant="body"
            )
        ]
    )

@ext.panel("cisco_webex_sidebar", slot="left")
async def webex_sidebar(ctx, **kwargs) -> ui.UINode:
    connections = await h._load_connections(ctx)
    conn_items = [
        ui.Text(c.get("label") or "Webex Account", variant="body")
        for c in connections
    ] if connections else [ui.Text("No Cisco Webex accounts connected yet.", variant="caption")]

    return ui.Stack(
        direction="v",
        gap=3,
        children=[
            ui.Text("Cisco Webex", variant="heading"),
            ui.Stack(direction="v", gap=1, children=conn_items),
            ui.Divider(),
            ui.Form(
                submit_label="Connect Webex",
                action=ui.Call("connect_webex"),
                children=[
                    ui.Stack(
                        direction="v",
                        gap=2,
                        children=[
                            ui.Input(
                                param_name="label",
                                placeholder="Connection label (e.g. Acme Webex)"
                            ),
                            ui.Input(
                                param_name="access_token",
                                placeholder="Bearer Access Token"
                            )
                        ]
                    )
                ]
            ),
            ui.Divider(),
            _help_modal(),
            _settings_button()
        ]
    )
