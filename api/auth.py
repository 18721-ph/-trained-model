"""SQLite user/session storage and FastAPI dependencies for browser sessions."""
from __future__ import annotations
import hashlib, hmac, secrets, sqlite3, time
from dataclasses import dataclass
from getpass import getpass
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from fastapi import Depends, HTTPException, Request, status
from api.config import settings

password_hasher = PasswordHasher()  # argon2-cffi defaults to Argon2id.
_DUMMY_HASH = password_hasher.hash("not-a-real-password")

@dataclass(frozen=True)
class AuthenticatedUser:
    id: int; username: str; display_name: str; role: str; session_id: str

def _now() -> int: return int(time.time())
def _digest(value: str) -> str: return hashlib.sha256(value.encode()).hexdigest()
def _connection() -> sqlite3.Connection:
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(settings.database_path); db.row_factory = sqlite3.Row
    return db

def initialize_database() -> None:
    with _connection() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE COLLATE NOCASE, display_name TEXT NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL, created_at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions (id_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL, csrf_hash TEXT NOT NULL, created_at INTEGER NOT NULL, last_seen_at INTEGER NOT NULL, idle_expires_at INTEGER NOT NULL, absolute_expires_at INTEGER NOT NULL, revoked_at INTEGER, FOREIGN KEY(user_id) REFERENCES users(id));
        CREATE TABLE IF NOT EXISTS login_attempts (ip_address TEXT NOT NULL, attempted_at INTEGER NOT NULL);
        CREATE INDEX IF NOT EXISTS login_attempts_ip_time ON login_attempts(ip_address, attempted_at);
        """)

def validate_password_strength(password: str) -> None:
    if len(password) < 12 or password.lower() == password or password.upper() == password or not any(c.isdigit() for c in password):
        raise ValueError("Password must be at least 12 characters and include upper-case, lower-case, and a number.")

def create_user(username: str, password: str, display_name: str | None = None, role: str = "analyst") -> None:
    username = username.strip()
    if len(username) < 3 or len(username) > 254: raise ValueError("Username must be between 3 and 254 characters.")
    validate_password_strength(password); initialize_database()
    try:
        with _connection() as db:
            db.execute("INSERT INTO users(username, display_name, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)", (username, (display_name or username).strip(), password_hasher.hash(password), role, _now()))
    except sqlite3.IntegrityError as exc: raise ValueError("An account with that username already exists.") from exc

def provision_user() -> None:
    username = input("Username or email: ").strip(); display_name = input("Display name (optional): ").strip()
    password = getpass("Password: "); confirmation = getpass("Confirm password: ")
    if password != confirmation: raise SystemExit("Passwords did not match; no account was created.")
    create_user(username, password, display_name or None); print("Authorized user created.")

def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"  # never trust X-Forwarded-For directly
def rate_limited(request: Request) -> bool:
    now = _now(); cutoff = now - settings.login_window_seconds; ip = _client_ip(request)
    with _connection() as db:
        db.execute("DELETE FROM login_attempts WHERE attempted_at < ?", (cutoff,))
        return db.execute("SELECT COUNT(*) FROM login_attempts WHERE ip_address = ?", (ip,)).fetchone()[0] >= settings.login_limit
def record_failed_login(request: Request) -> None:
    with _connection() as db: db.execute("INSERT INTO login_attempts(ip_address, attempted_at) VALUES (?, ?)", (_client_ip(request), _now()))
def authenticate(username: str, password: str) -> sqlite3.Row | None:
    with _connection() as db: user = db.execute("SELECT * FROM users WHERE username = ?", (username.strip(),)).fetchone()
    try: valid = password_hasher.verify(user["password_hash"] if user else _DUMMY_HASH, password)
    except (VerifyMismatchError, InvalidHashError): valid = False
    return user if user and valid else None
def create_session(user: sqlite3.Row) -> tuple[str, str]:
    session_id, csrf_token, now = secrets.token_urlsafe(32), secrets.token_urlsafe(32), _now()
    with _connection() as db: db.execute("INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?, NULL)", (_digest(session_id), user["id"], _digest(csrf_token), now, now, now + settings.session_idle_seconds, now + settings.session_absolute_seconds))
    return session_id, csrf_token
def revoke_session(session_id: str | None) -> None:
    if session_id:
        with _connection() as db: db.execute("UPDATE sessions SET revoked_at = ? WHERE id_hash = ? AND revoked_at IS NULL", (_now(), _digest(session_id)))
def current_user(request: Request) -> AuthenticatedUser:
    session_id = request.cookies.get(settings.cookie_name); now = _now()
    if not session_id or len(session_id) > 256: raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required.")
    with _connection() as db:
        row = db.execute("SELECT s.*, u.username, u.display_name, u.role FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.id_hash=?", (_digest(session_id),)).fetchone()
        if not row or row["revoked_at"] is not None or row["idle_expires_at"] <= now or row["absolute_expires_at"] <= now:
            if row and row["revoked_at"] is None: db.execute("UPDATE sessions SET revoked_at=? WHERE id_hash=?", (now, _digest(session_id)))
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required.")
        db.execute("UPDATE sessions SET last_seen_at=?, idle_expires_at=? WHERE id_hash=?", (now, min(now + settings.session_idle_seconds, row["absolute_expires_at"]), _digest(session_id)))
    return AuthenticatedUser(row["user_id"], row["username"], row["display_name"], row["role"], session_id)
def require_csrf(request: Request, user: AuthenticatedUser = Depends(current_user)) -> AuthenticatedUser:
    token = request.headers.get("X-CSRF-Token", "")
    with _connection() as db: row = db.execute("SELECT csrf_hash FROM sessions WHERE id_hash=? AND revoked_at IS NULL", (_digest(user.session_id),)).fetchone()
    if not token or not row or not hmac.compare_digest(_digest(token), row["csrf_hash"]): raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid CSRF token.")
    return user
def issue_session_cookie(response, session_id: str) -> None:
    response.set_cookie(settings.cookie_name, session_id, max_age=settings.session_absolute_seconds, httponly=True, secure=settings.secure_cookies, samesite="lax", path="/")
def clear_session_cookie(response) -> None:
    response.delete_cookie(settings.cookie_name, path="/", httponly=True, secure=settings.secure_cookies, samesite="lax")
