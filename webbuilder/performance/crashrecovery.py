import json
from pathlib import Path


class CrashRecovery:
    def __init__(self, directory):
        self._directory = Path(directory)
        self._file = self._directory / "recovery.json"

    def save_session(self, data):
        payload = {"project": data}
        self._file.write_text(json.dumps(payload), encoding="utf-8")

    def has_recovery(self):
        return self._file.exists()

    def get_recovery(self):
        if self._file.exists():
            return json.loads(self._file.read_text(encoding="utf-8"))
        return None

    def get_recovery_info(self):
        data = self.get_recovery()
        if data and "project" in data:
            return {"project_name": data["project"].get("name", "")}
        return None

    def clear_recovery(self):
        if self._file.exists():
            self._file.unlink()
