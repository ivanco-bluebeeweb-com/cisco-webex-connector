"""Cisco Webex REST API v1 client implementation."""
from __future__ import annotations
import httpx
from typing import Any, Dict, List, Optional

class WebexClient:
    def __init__(self, access_token: str):
        self.base_url = "https://webexapis.com/v1"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    async def get_me(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.base_url}/people/me", headers=self.headers, timeout=15.0)
            res.raise_for_status()
            return res.json()

    async def list_meetings(self, state: Optional[str] = "active", max_results: int = 50) -> List[Dict[str, Any]]:
        params = {"max": max_results}
        if state:
            params["state"] = state
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.base_url}/meetings", headers=self.headers, params=params, timeout=15.0)
            res.raise_for_status()
            return res.json().get("items", [])

    async def get_meeting(self, meeting_id: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.base_url}/meetings/{meeting_id}", headers=self.headers, timeout=15.0)
            res.raise_for_status()
            return res.json()

    async def create_meeting(self, title: str, start: str, end: str, password: Optional[str] = None, invitees: Optional[List[str]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "title": title,
            "start": start,
            "end": end
        }
        if password:
            payload["password"] = password
        if invitees:
            payload["invitees"] = [{"email": e} for e in invitees]
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{self.base_url}/meetings", headers=self.headers, json=payload, timeout=15.0)
            res.raise_for_status()
            return res.json()

    async def delete_meeting(self, meeting_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            res = await client.delete(f"{self.base_url}/meetings/{meeting_id}", headers=self.headers, timeout=15.0)
            return res.status_code in (200, 204)

    async def list_rooms(self, room_type: Optional[str] = None, max_results: int = 50) -> List[Dict[str, Any]]:
        params = {"max": max_results}
        if room_type:
            params["type"] = room_type
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.base_url}/rooms", headers=self.headers, params=params, timeout=15.0)
            res.raise_for_status()
            return res.json().get("items", [])

    async def create_room(self, title: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{self.base_url}/rooms", headers=self.headers, json={"title": title}, timeout=15.0)
            res.raise_for_status()
            return res.json()

    async def post_message(self, room_id: str, text: str, markdown: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"roomId": room_id, "text": text}
        if markdown:
            payload["markdown"] = markdown
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{self.base_url}/messages", headers=self.headers, json=payload, timeout=15.0)
            res.raise_for_status()
            return res.json()

    async def list_recordings(self, max_results: int = 50) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.base_url}/recordings", headers=self.headers, params={"max": max_results}, timeout=15.0)
            res.raise_for_status()
            return res.json().get("items", [])
