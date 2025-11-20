import httpx
from typing import Dict, Any, Optional
import json


async def send_n8n_webhook(
    webhook_url: str,
    data: Dict[str, Any],
    timeout: int = 10
) -> bool:
    """Send data to n8n webhook"""
    if not webhook_url:
        return False

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json=data,
                timeout=timeout
            )
            return response.status_code == 200
    except Exception as e:
        print(f"Error sending webhook: {e}")
        return False


async def send_lead_to_n8n(
    webhook_url: str,
    lead_data: Dict[str, Any]
) -> bool:
    """Send lead data to n8n"""
    payload = {
        "event": "new_lead",
        "data": lead_data
    }
    return await send_n8n_webhook(webhook_url, payload)


async def send_conversation_to_n8n(
    webhook_url: str,
    conversation_data: Dict[str, Any]
) -> bool:
    """Send conversation data to n8n"""
    payload = {
        "event": "new_conversation",
        "data": conversation_data
    }
    return await send_n8n_webhook(webhook_url, payload)
