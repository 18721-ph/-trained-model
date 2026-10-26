from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from api.auth import (AuthenticatedUser, _connection, authenticate, change_password, clear_session_cookie, create_session, current_user, initialize_database, issue_session_cookie, rate_limited, record_failed_login, require_csrf, revoke_session)
from api.config import settings
from api.schemas import ApplicantRequest, ChangePasswordRequest, LoginRequest, PredictionResponse, UserResponse
from api.service import predict_default

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; connect-src 'self'"
        return response

app = FastAPI(title="Loan Default Prediction API", description="Authenticated loan-default risk assessment API.", version="1.1.0")
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=list(settings.frontend_origins), allow_credentials=True, allow_methods=["GET", "POST"], allow_headers=["Content-Type", "X-CSRF-Token"])

@app.on_event("startup")
def startup() -> None: initialize_database()

@app.get("/")
def root(): return {"message": "Loan Default Prediction API is running"}

def public_user(user: AuthenticatedUser) -> UserResponse:
    return UserResponse(username=user.username, display_name=user.display_name, role=user.role)

@app.post("/auth/login", response_model=UserResponse)
def login(credentials: LoginRequest, request: Request, response: Response):
    if rate_limited(request): raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many login attempts. Please try again later.")
    user = authenticate(credentials.username, credentials.password)
    if not user:
        record_failed_login(request)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password.")
    session_id, _ = create_session(user)  # Fresh ID prevents session fixation.
    issue_session_cookie(response, session_id)
    return UserResponse(username=user["username"], display_name=user["display_name"], role=user["role"])

@app.get("/auth/me", response_model=UserResponse)
def me(user: AuthenticatedUser = Depends(current_user)): return public_user(user)

@app.post("/auth/change-password", response_model=UserResponse)
def change_current_password(payload: ChangePasswordRequest, response: Response, user: AuthenticatedUser = Depends(require_csrf)):
    try:
        changed = change_password(user.id, payload.current_password, payload.new_password)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    if not changed:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password is incorrect.")
    # Password changes get a brand-new session; every prior browser is signed out.
    with _connection() as db:
        account = db.execute("SELECT * FROM users WHERE id = ?", (user.id,)).fetchone()
    session_id, _ = create_session(account)
    issue_session_cookie(response, session_id)
    return public_user(AuthenticatedUser(user.id, user.username, user.display_name, user.role, session_id))

@app.get("/auth/csrf")
def csrf(user: AuthenticatedUser = Depends(current_user)):
    # Synchronizer token is issued only after session validation and kept in browser memory.
    from api.auth import _connection, _digest
    import secrets
    token = secrets.token_urlsafe(32)
    with _connection() as db: db.execute("UPDATE sessions SET csrf_hash=? WHERE id_hash=?", (_digest(token), _digest(user.session_id)))
    return {"csrf_token": token}

@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, user: AuthenticatedUser = Depends(require_csrf)):
    revoke_session(user.session_id); clear_session_cookie(response)

@app.post("/predict", response_model=PredictionResponse)
def predict(applicant: ApplicantRequest, user: AuthenticatedUser = Depends(require_csrf)):
    return predict_default(applicant.model_dump())
