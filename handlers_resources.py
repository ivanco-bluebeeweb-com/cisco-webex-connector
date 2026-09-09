"""Resource operation handlers for Cisco Webex Connector."""
from __future__ import annotations
from imperal_sdk import ActionResult
from app import chat
import schemas as s
from handlers_connection import _get_client

@chat.function(
    "list_meetings",
    "List Webex meetings with optional state filter.",
    action_type="read",
    chain_callable=True,
    effects=[],
    data_model=s.ListMeetingsParams
)
async def list_meetings(ctx, params: s.ListMeetingsParams) -> ActionResult:
    """List Webex meetings."""
    try:
        client = await _get_client(ctx, params.connection_id)
        meetings = await client.list_meetings(state=params.state, max_results=params.max_results)
        return ActionResult.success(
            data={"meetings": meetings, "count": len(meetings)},
            summary=f"Retrieved {len(meetings)} meeting(s) from Cisco Webex."
        )
    except Exception as exc:
        return ActionResult.error(f"Failed to list meetings: {exc}")

@chat.function(
    "get_meeting",
    "Get details of a specific Webex meeting by ID.",
    action_type="read",
    chain_callable=True,
    effects=[],
    data_model=s.GetMeetingParams
)
async def get_meeting(ctx, params: s.GetMeetingParams) -> ActionResult:
    """Get details of a specific Webex meeting."""
    try:
        client = await _get_client(ctx, params.connection_id)
        meeting = await client.get_meeting(meeting_id=params.meeting_id)
        return ActionResult.success(
            data={"meeting": meeting},
            summary=f"Retrieved meeting: {meeting.get('title', params.meeting_id)}."
        )
    except Exception as exc:
        return ActionResult.error(f"Failed to get meeting: {exc}")

@chat.function(
    "create_meeting",
    "Schedule a new Webex meeting.",
    action_type="write",
    chain_callable=True,
    effects=[],
    data_model=s.CreateMeetingParams
)
async def create_meeting(ctx, params: s.CreateMeetingParams) -> ActionResult:
    """Schedule a new Webex meeting."""
    try:
        client = await _get_client(ctx, params.connection_id)
        meeting = await client.create_meeting(
            title=params.title,
            start=params.start,
            end=params.end,
            password=params.password,
            invitees=params.invitees
        )
        return ActionResult.success(
            data={"meeting": meeting},
            summary=f"Scheduled Webex meeting '{params.title}' (ID: {meeting.get('id')})."
        )
    except Exception as exc:
        return ActionResult.error(f"Failed to schedule meeting: {exc}")

@chat.function(
    "delete_meeting",
    "Delete/cancel a scheduled Webex meeting.",
    action_type="write",
    chain_callable=True,
    effects=[],
    data_model=s.DeleteMeetingParams
)
async def delete_meeting(ctx, params: s.DeleteMeetingParams) -> ActionResult:
    """Delete a Webex meeting."""
    try:
        client = await _get_client(ctx, params.connection_id)
        success = await client.delete_meeting(meeting_id=params.meeting_id)
        if success:
            return ActionResult.success(
                data={"meeting_id": params.meeting_id},
                summary=f"Deleted Webex meeting {params.meeting_id}."
            )
        return ActionResult.error(f"Webex returned failure deleting meeting {params.meeting_id}.")
    except Exception as exc:
        return ActionResult.error(f"Failed to delete meeting: {exc}")

@chat.function(
    "list_rooms",
    "List Webex spaces/rooms with optional type filter.",
    action_type="read",
    chain_callable=True,
    effects=[],
    data_model=s.ListRoomsParams
)
async def list_rooms(ctx, params: s.ListRoomsParams) -> ActionResult:
    """List Webex spaces/rooms."""
    try:
        client = await _get_client(ctx, params.connection_id)
        rooms = await client.list_rooms(room_type=params.room_type, max_results=params.max_results)
        return ActionResult.success(
            data={"rooms": rooms, "count": len(rooms)},
            summary=f"Retrieved {len(rooms)} Webex space(s)/room(s)."
        )
    except Exception as exc:
        return ActionResult.error(f"Failed to list rooms: {exc}")

@chat.function(
    "create_room",
    "Create a new Webex space/room.",
    action_type="write",
    chain_callable=True,
    effects=[],
    data_model=s.CreateRoomParams
)
async def create_room(ctx, params: s.CreateRoomParams) -> ActionResult:
    """Create a new Webex space/room."""
    try:
        client = await _get_client(ctx, params.connection_id)
        room = await client.create_room(title=params.title)
        return ActionResult.success(
            data={"room": room},
            summary=f"Created Webex space '{params.title}' (ID: {room.get('id')})."
        )
    except Exception as exc:
        return ActionResult.error(f"Failed to create room: {exc}")

@chat.function(
    "post_message",
    "Post a message to a Webex space/room.",
    action_type="write",
    chain_callable=True,
    effects=[],
    data_model=s.PostMessageParams
)
async def post_message(ctx, params: s.PostMessageParams) -> ActionResult:
    """Post a message to a Webex space/room."""
    try:
        client = await _get_client(ctx, params.connection_id)
        msg = await client.post_message(room_id=params.room_id, text=params.text, markdown=params.markdown)
        return ActionResult.success(
            data={"message": msg},
            summary=f"Posted message to Webex space {params.room_id}."
        )
    except Exception as exc:
        return ActionResult.error(f"Failed to post message: {exc}")

@chat.function(
    "list_recordings",
    "List Webex meeting recordings.",
    action_type="read",
    chain_callable=True,
    effects=[],
    data_model=s.ListRecordingsParams
)
async def list_recordings(ctx, params: s.ListRecordingsParams) -> ActionResult:
    """List Webex recordings."""
    try:
        client = await _get_client(ctx, params.connection_id)
        recordings = await client.list_recordings(max_results=params.max_results)
        return ActionResult.success(
            data={"recordings": recordings, "count": len(recordings)},
            summary=f"Retrieved {len(recordings)} Webex recording(s)."
        )
    except Exception as exc:
        return ActionResult.error(f"Failed to list recordings: {exc}")

@chat.function(
    "audit_webex_health",
    "Audit Cisco Webex connectivity and account status.",
    action_type="read",
    chain_callable=True,
    effects=[],
    data_model=s.AuditHealthParams
)
async def audit_webex_health(ctx, params: s.AuditHealthParams) -> ActionResult:
    """Audit Cisco Webex connectivity."""
    try:
        client = await _get_client(ctx, params.connection_id)
        user = await client.get_me()
        meetings_count = 0
        meetings_error = None
        try:
            meetings = await client.list_meetings(max_results=5)
            meetings_count = len(meetings)
        except Exception as m_exc:
            meetings_error = str(m_exc)

        rooms_count = 0
        rooms_error = None
        try:
            rooms = await client.list_rooms(max_results=5)
            rooms_count = len(rooms)
        except Exception as r_exc:
            rooms_error = str(r_exc)

        is_bot = user.get("type") == "bot"
        summary_msg = f"Cisco Webex is healthy: connected as {user.get('displayName')} ({user.get('type', 'user')})."
        if rooms_error:
            summary_msg += f" Spaces notice: {rooms_error}."
        if meetings_error:
            summary_msg += f" Meetings notice: {meetings_error}."

        return ActionResult.success(
            data={
                "status": "healthy",
                "user": user.get("displayName"),
                "type": user.get("type"),
                "email": user.get("emails", [""])[0] if user.get("emails") else "",
                "sample_meetings_count": meetings_count,
                "sample_rooms_count": rooms_count,
                "meetings_error": meetings_error,
                "rooms_error": rooms_error
            },
            summary=summary_msg
        )
    except Exception as exc:
        return ActionResult.error(f"Health audit failed: {exc}")
