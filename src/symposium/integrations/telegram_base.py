from dataclasses import dataclass


@dataclass(frozen=True)
class ChatContext:
    chat_id: int
    user_id: int
    thread_id: int | None
    business_connection_id: str | None
