from datetime import datetime
from .base_log import BaseLog


class SessionLog(BaseLog):
    def __init__(self, file_name="session_log.json"):
        super().__init__(file_name=file_name)
        self.session_started_at = None

    def start_session(self):
        self.session_started_at = datetime.now()
        session_log = self._read_json()

        if "current_session" in session_log:
            current_session = session_log.pop("current_session")
            session_log.setdefault("session_histories", []).append(current_session)

        session_log["current_session"] = {
            "session_started_at": self.session_started_at.isoformat(),
            "total_run_minutes": 0,
            "session_last_updated": self.session_started_at.isoformat(),
        }

        self._write_json(session_log)

    def update_session_log(self, session_index):
        if not self.session_started_at:
            raise RuntimeError("Session has not started. Call start_session() first.")
        
        session_log = self._read_json()

        current_time = datetime.now()
        session_log["current_session"]["session_last_updated"] = current_time.isoformat()
        session_log["current_session"]["total_run_minutes"] = (
            (current_time - datetime.fromisoformat(session_log["current_session"]["session_started_at"])).total_seconds() // 60
        )

        self._write_json(session_log)
