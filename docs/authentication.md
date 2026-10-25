# Authentication

Only provisioned lending staff can use the prediction API. A password is hashed with Argon2id; neither its plaintext value nor a reversible form is stored. Login creates a cryptographically random opaque session ID. The browser receives that ID only in an `HttpOnly`, `SameSite=Lax` cookie, while SQLite stores only its SHA-256 digest. Server-side records enforce both 30-minute idle expiry (by default) and 8-hour absolute expiry, and logout revokes the record.

`POST /predict` requires both a valid session and a synchronizer CSRF token in `X-CSRF-Token`. The raw CSRF token is returned by `GET /auth/csrf` only after authentication, retained in frontend memory, and compared with its server-side digest. SameSite reduces some cross-site requests but is not a complete CSRF defence, so the custom-header token remains required. CORS only controls browser origin access; it is not authentication or CSRF protection.

## Local use

Copy `.env.example` to `.env` if settings must change. Create an authorized user without exposing a password in shell history:

```powershell
.\.venv\Scripts\python.exe -m scripts.provision_user
.\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8001
cd frontend; npm.cmd run dev
```

For local HTTP development `Secure` is false by the explicit development configuration. In production set `APP_ENV=production`, deploy behind HTTPS, set `SESSION_COOKIE_SECURE=true`, and configure exact HTTPS `FRONTEND_ORIGINS`. If frontend and API are different sites, revisit the SameSite/CORS architecture deliberately; do not use wildcard credentialed CORS.

## Request flow

1. Staff sign in at `POST /auth/login`; a cookie is issued.
2. The SPA calls `GET /auth/csrf` with that cookie, keeping the returned token only in memory.
3. It calls `POST /predict` with the cookie and `X-CSRF-Token`; invalid sessions return 401 and invalid/missing CSRF returns 403.
4. `POST /auth/logout` verifies CSRF, revokes the session, and expires the cookie.

Login failures use one generic message and are limited per direct client IP (default five failures per 15 minutes). This SQLite limiter works across processes that share the database, but a real multi-instance service should use a shared rate-limit store and trusted-proxy configuration.

## Verification and limits

Run `.\.venv\Scripts\python.exe -m pytest tests/test_auth.py -v`. This prototype adds browser headers and tightly configured CORS, but is not ready for a financial institution: it still needs TLS/proxy hardening, managed secrets and database backups, audit trails with privacy controls, role administration, independent penetration testing, monitoring, retention governance, and fairness/privacy validation.
