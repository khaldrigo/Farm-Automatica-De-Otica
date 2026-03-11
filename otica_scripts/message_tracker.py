import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from otica_scripts.config import MESSAGES_DATA_FILE


@dataclass
class SentMessage:
    store_name: str
    store_phone: str
    message: str
    sent_at: str
    status: str = "sent"
    response: str | None = None
    responded_at: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SentMessage":
        return cls(**data)


class MessageManager:
    def __init__(self, data_file: str = MESSAGES_DATA_FILE) -> None:
        self.data_file = Path(data_file)
        self._ensure_data_file()

    def _ensure_data_file(self) -> None:
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self._save_messages([])

    def _load_messages(self) -> list[SentMessage]:
        with open(self.data_file) as f:
            data = json.load(f)
        return [SentMessage.from_dict(m) for m in data]

    def _save_messages(self, messages: list[SentMessage]) -> None:
        with open(self.data_file, "w") as f:
            json.dump([m.to_dict() for m in messages], f, indent=2, ensure_ascii=False)

    def add_message(self, store_name: str, store_phone: str, message: str) -> SentMessage:
        messages = self._load_messages()
        sent_msg = SentMessage(
            store_name=store_name,
            store_phone=store_phone,
            message=message,
            sent_at=datetime.now().isoformat(),
            status="sent"
        )
        messages.append(sent_msg)
        self._save_messages(messages)
        return sent_msg

    def get_messages_by_phone(self, phone: str) -> list[SentMessage]:
        messages = self._load_messages()
        return [m for m in messages if m.store_phone == phone]

    def get_all_messages(self) -> list[SentMessage]:
        return self._load_messages()

    def get_latest_message_per_store(self) -> dict[str, SentMessage]:
        messages = self._load_messages()
        latest: dict[str, SentMessage] = {}
        for msg in messages:
            if msg.store_phone not in latest or msg.sent_at > latest[msg.store_phone].sent_at:
                latest[msg.store_phone] = msg
        return latest

    def add_response(self, phone: str, response: str) -> bool:
        messages = self._load_messages()
        updated = False
        for msg in messages:
            if msg.store_phone == phone and msg.status == "sent":
                msg.status = "responded"
                msg.response = response
                msg.responded_at = datetime.now().isoformat()
                updated = True
        if updated:
            self._save_messages(messages)
        return updated

    def mark_as_responded(self, phone: str, response: str = "") -> bool:
        messages = self._load_messages()
        updated = False
        for msg in messages:
            if msg.store_phone == phone:
                msg.status = "responded"
                if response:
                    msg.response = response
                msg.responded_at = datetime.now().isoformat()
                updated = True
        if updated:
            self._save_messages(messages)
        return updated

    def get_pending_stores(self) -> list[SentMessage]:
        messages = self._load_messages()
        pending: dict[str, SentMessage] = {}
        for msg in messages:
            if msg.store_phone not in pending or msg.sent_at > pending[msg.store_phone].sent_at:
                pending[msg.store_phone] = msg
        return [m for m in pending.values() if m.status == "sent"]
