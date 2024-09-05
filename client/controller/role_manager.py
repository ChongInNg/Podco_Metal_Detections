
from log.logger import Logger

ROLE_USER = "user"
ROLE_ADMIN = "admin"

class RoleManager:
    _instance = None
    _current_role = ROLE_USER  

    @classmethod
    def instance(cls) -> 'RoleManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def current_role(self):
        return self._current_role

    def login_as_user(self):
        self._login(ROLE_USER)

    def login_as_admin(self):
        self._login(ROLE_ADMIN)

    def _login(self, role):
        if role not in [ROLE_ADMIN, ROLE_USER]:
            raise ValueError("Invalid role. Must be 'admin' or 'user'.")
        
        if self._current_role == ROLE_ADMIN and role == ROLE_USER:
            raise PermissionError("Cannot log in as 'user' while an 'admin' is active.")
        
        self._current_role = role
        Logger.info(f"Login as {self._current_role}")
        return True

    def logout(self):
        self._current_role = ROLE_USER
        Logger.info(f"Logout, current role: {self._current_role}")

    def is_admin(self):
        return self._current_role == ROLE_ADMIN

    def is_user(self):
        return self._current_role == ROLE_USER