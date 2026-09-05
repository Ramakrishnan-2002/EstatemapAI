# ADR-009: Authentication, JWT Security, and Resource Ownership Authorization

## Status
Accepted

## Context
EstateMap AI requires secure user registration, password management, stateless token authentication, and a clear authorization foundation for protected resources and user profile data.

## Decision
1. **Password Hashing**: Use Argon2id via `passlib.context.CryptContext` with Bcrypt backward-compatibility support. Plaintext passwords are never stored, logged, or returned.
2. **Stateless JWT Tokens**: Issues standard JWT Bearer tokens containing `sub` (user_id), `iat`, `exp`, and `type="access"` signed with HMAC-SHA256 (`HS256`) and dynamic secret keys from environment configuration.
3. **Anti-Enumeration Safeguard**: Login failures for nonexistent emails and incorrect passwords return identical `AUTHENTICATION_FAILED` (401) error responses.
4. **Current User Dependency**: `get_current_user` extracts the Bearer token, validates signature/expiration, and loads the active user entity from PostgreSQL.
5. **Ownership Authorization**: Authorization is enforced at the service level using `AuthService.ensure_ownership(resource_owner_id, current_user_id)` raising `FORBIDDEN` (403).

## Consequences
- Clean separation of authentication concerns via reusable FastAPI dependencies.
- Zero credential or password hash leakage through strict Pydantic response models (`UserResponse`).
- Robust protection against user enumeration and timing-based attacks.
