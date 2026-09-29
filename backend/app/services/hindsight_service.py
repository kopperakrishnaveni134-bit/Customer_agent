from datetime import datetime

from hindsight_client import Hindsight

from app.config import settings


BANK_ID = settings.hindsight_bank_id


def get_hindsight_client():
    return Hindsight(
        base_url=settings.hindsight_api_url,
        api_key=settings.hindsight_api_key,
        timeout=60.0,
    )


def retain_memory(
    content: str,
    context: str | None = None,
    document_id: str | None = None,
    metadata: dict | None = None,
):
    client = get_hindsight_client()

    try:
        return client.retain(
            bank_id=BANK_ID,
            content=content,
            context=context,
            timestamp=datetime.utcnow(),
            document_id=document_id,
            metadata=metadata,
            retain_async=False,
        )
    finally:
        client.close()


def recall_memory(
    query: str,
    max_tokens: int = 3000,
):
    client = get_hindsight_client()

    try:
        return client.recall(
            bank_id=BANK_ID,
            query=query,
            max_tokens=max_tokens,
            budget="mid",
        )
    finally:
        client.close()


def list_memories(limit: int = 50):
    client = get_hindsight_client()

    try:
        return client.list_memories(
            bank_id=BANK_ID,
            limit=limit,
            offset=0,
        )
    finally:
        client.close()