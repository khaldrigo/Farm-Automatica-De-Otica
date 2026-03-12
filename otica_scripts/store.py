import json
from dataclasses import asdict, dataclass
from pathlib import Path

from otica_scripts.config import STORES_DATA_FILE


@dataclass
class Store:
    name: str
    phone: str
    address: str | None = None
    instagram: str | None = None

    def __post_init__(self) -> None:
        self.phone = self._normalize_phone(self.phone)
        if self.instagram:
            self.instagram = self._normalize_instagram(self.instagram)

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        digits = "".join(c for c in phone if c.isdigit())
        if not digits.startswith("55"):
            digits = "55" + digits
        return f"+{digits}"

    @staticmethod
    def _normalize_instagram(ig: str) -> str:
        ig = ig.strip()
        if not ig.startswith("@"):
            ig = "@" + ig
        return ig

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Store":
        return cls(**data)


class StoreManager:
    def __init__(self, data_file: str = STORES_DATA_FILE) -> None:
        self.data_file = Path(data_file)
        self._ensure_data_file()

    def _ensure_data_file(self) -> None:
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self._save_stores([])

    def _load_stores(self) -> list[Store]:
        with open(self.data_file) as f:
            data = json.load(f)
        return [Store.from_dict(s) for s in data]

    def _save_stores(self, stores: list[Store]) -> None:
        import os
        import tempfile

        temp_dir = self.data_file.parent
        with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False, encoding="utf-8") as f:
            json.dump([s.to_dict() for s in stores], f, indent=2, ensure_ascii=False)
            tempname = f.name

        try:
            os.replace(tempname, self.data_file)
        except Exception:
            if os.path.exists(tempname):
                os.unlink(tempname)
            raise

    def add_store(self, name: str, phone: str, address: str | None = None, instagram: str | None = None) -> Store:
        stores = self._load_stores()
        store = Store(name=name, phone=phone, address=address, instagram=instagram)
        stores.append(store)
        self._save_stores(stores)
        return store

    def remove_store(self, name: str) -> bool:
        stores = self._load_stores()
        initial_len = len(stores)
        stores = [s for s in stores if s.name.lower() != name.lower()]
        if len(stores) < initial_len:
            self._save_stores(stores)
            return True
        return False

    def get_all_stores(self) -> list[Store]:
        return self._load_stores()

    def get_store(self, name: str) -> Store | None:
        stores = self._load_stores()
        for store in stores:
            if store.name.lower() == name.lower():
                return store
        return None
