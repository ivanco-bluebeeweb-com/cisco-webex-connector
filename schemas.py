"""Pydantic schemas for Cisco Webex Connector (Webex REST API v1)."""
from __future__ import annotations
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field

class NoParams(BaseModel):
    """Empty parameter model."""
    pass

class ConnectWebexParams(BaseModel):
    label: str = Field(default="", description="Friendly connection label, e.g. Acme Webex.")
    access_token: str = Field(..., description="Webex Integration / Bot Bearer Access Token.")

class DisconnectWebexParams(BaseModel):
    connection_id: str = Field(..., description="Connection ID to remove.")

class ListMeetingsParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    state: Optional[str] = Field(default="active", description="Filter state: active, scheduled, ready, ended.")
    max_results: int = Field(default=50, description="Max meetings to return (1-100).")

class GetMeetingParams(BaseModel):
    meeting_id: str = Field(..., description="Unique Webex Meeting ID.")
    connection_id: str = Field(default="", description="Optional connection ID.")

class CreateMeetingParams(BaseModel):
    title: str = Field(..., description="Meeting title/topic.")
    start: str = Field(..., description="Meeting start time (ISO 8601 UTC string, e.g. 2026-09-04T10:00:00Z).")
    end: str = Field(..., description="Meeting end time (ISO 8601 UTC string, e.g. 2026-09-04T11:00:00Z).")
    password: Optional[str] = Field(default=None, description="Optional meeting password.")
    invitees: Optional[List[str]] = Field(default=None, description="List of participant email addresses.")
    connection_id: str = Field(default="", description="Optional connection ID.")

class DeleteMeetingParams(BaseModel):
    meeting_id: str = Field(..., description="Unique Webex Meeting ID.")
    connection_id: str = Field(default="", description="Optional connection ID.")

class ListRoomsParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    room_type: Optional[str] = Field(default=None, description="direct or group.")
    max_results: int = Field(default=50, description="Max rooms to return.")

class CreateRoomParams(BaseModel):
    title: str = Field(..., description="Space/Room title.")
    connection_id: str = Field(default="", description="Optional connection ID.")

class PostMessageParams(BaseModel):
    room_id: str = Field(..., description="Room/Space ID.")
    text: str = Field(..., description="Plain text message content.")
    markdown: Optional[str] = Field(default=None, description="Optional markdown formatted message.")
    connection_id: str = Field(default="", description="Optional connection ID.")

class ListRecordingsParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    max_results: int = Field(default=50, description="Max recordings to return.")

class AuditHealthParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
