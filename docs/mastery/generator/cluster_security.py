# -*- coding: utf-8 -*-
# Stories 14 - 17 (Security, Identity & Authentication)

def get_security_stories():
    stories = []

    # Story 14
    stories.append({
        'num': 14,
        'title': 'Password Hashing with Argon2id & Cryptographic Salting',
        'points': 3,
        'why_exists': 'Legacy hashing algorithms like MD5, SHA-256, and even raw bcrypt are vulnerable to GPU-accelerated dictionary attacks and ASIC brute-forcing. Modern secure authentication requires memory-hard password hashing algorithms.',
        'problem_solved': 'Database breaches that leak unsalted or weak password hashes allow attackers to recover plaintext user passwords in seconds using rainbow tables and GPU cracking rigs.',
        'prereq_stories': ['Story 03 — Type-Safe Configuration with Pydantic-Settings', 'Story 05 — RFC 7807 Centralized Error Handling'],
        'prereq_concepts': ['Cryptographic salts', 'Memory-hard hashing functions', 'Argon2id winner of Password Hashing Competition', 'Passlib CryptContext'],
        'depends_on': [3, 5],
        'unlocks': [15, 16],
        'readiness': [
            'Understand why hashing is a one-way mathematical function',
            'Able to explain why SHA-256 is fast and therefore unsuitable for password hashing',
            'Familiar with salt generation to prevent rainbow table attacks'
        ],
        'objectives': [
            'Implement Argon2id password hashing and verification using passlib.context.CryptContext',
            'Configure memory cost, time cost, and parallelism parameters for optimal security/performance tradeoff',
            'Prevent timing attacks during password verification using constant-time string comparison'
        ],
        'concepts': [
            'Argon2id: Hybrid memory-hard hashing algorithm combining Argon2d (data-dependent) and Argon2i (data-independent) to resist side-channel and GPU attacks',
            'Unique Cryptographic Salt: Random per-user byte string appended before hashing to ensure identical passwords produce distinct hashes',
            'Constant-Time Verification: Mitigating timing side-channel attacks by comparing byte representations in constant time',
            'CryptContext Configuration: Managing algorithm migration and deprecated hash deprecation seamlessly'
        ],
        'impl': 'backend/app/core/security.py instantiates pwd_context = CryptContext(schemes=["argon2"], deprecated="auto") and exports get_password_hash(password: str) -> str and verify_password(plain_password: str, hashed_password: str) -> bool.',
        'files': [
            'backend/app/core/security.py (get_password_hash, verify_password)',
            'backend/app/models/user.py',
            'backend/app/api/v1/endpoints/auth.py'
        ],
        'data_flow': 'User Registration/Login Request -> Plaintext password passed to security.py -> Argon2id hashes with unique salt -> Stored in users.hashed_password -> On login, verify_password computes hash with stored salt in constant time -> Boolean match returned',
        'lab_standalone': '''Build a standalone password hashing lab:
1. Install argon2-cffi and passlib.
2. Create CryptContext with argon2.
3. Hash password "SecretPass123!" twice and observe that both resulting hashes are completely distinct due to automatic salt generation.
4. Verify both plain text candidates against both hashes and verify constant-time matching returns True for exact match and False for mismatch.''',
        'lab_mapping': 'Inspect backend/app/core/security.py lines 10-25 and verify how get_password_hash is called in backend/app/services/auth_service.py.',
        'acceptance_criteria': [
            'Plaintext passwords are never stored in the database or logged in plain text.',
            'verify_password correctly validates matching passwords and rejects invalid passwords.',
            'Argon2id hash string contains embedded salt and iteration parameters.',
            'Password hashing execution takes approximately 50-100ms per operation, preventing high-speed brute forcing.'
        ],
        'evidence': [
            'Run docker exec estatemap-backend python -c "from app.core.security import get_password_hash, verify_password; h=get_password_hash(\'test\'); assert verify_password(\'test\', h); print(\'Argon2id verified\')".',
            'Run docker exec estatemap-backend pytest tests/unit/test_security.py.'
        ],
        'outcome_conceptual': 'Deep understanding of memory-hard cryptography, password salting, and side-channel timing attack defense.',
        'outcome_impl': 'Ability to implement robust, production-grade authentication cryptography using Argon2id in Python.',
        'outcome_interview': 'Ability to explain why Argon2id is mathematically superior to bcrypt and PBKDF2 in resisting GPU/ASIC attacks.',
        'mistakes': [
            'Using raw hashlib.sha256(password.encode()).hexdigest() which is vulnerable to GPU cracking at billions of hashes/second.',
            'Hardcoding a single global static salt across all users instead of per-user random salts.',
            'Logging plaintext passwords in debug logs during login request validation.'
        ],
        'debug_symptom': 'Authentication fails for a valid user after database migration or server environment change.',
        'debug_investigate': 'Check if the underlying C library (argon2-cffi) is properly compiled in the Docker container and verify CryptContext schemes.',
        'debug_goal': 'Ensure argon2-cffi binary wheels are installed in the Python container environment.',
        'tradeoffs': [
            'Argon2id vs Bcrypt: Argon2id provides configurable memory hardness, defeating GPU farms, whereas bcrypt has a fixed 4KB memory cost.',
            'High memory/time cost vs Login latency: Set parameters to ~50ms computation time to balance high security with responsive user authentication.'
        ],
        'prod_current': 'Argon2id via Passlib CryptContext with automatic salt generation stored in PostgreSQL users table.',
        'prod_scale': 'Offload authentication to dedicated Auth0/Keycloak identity providers or run password verification on isolated auth worker pools at millions of users.',
        'q_basic': 'Why is SHA-256 unsuitable for password hashing and what makes Argon2id secure?',
        'q_impl': 'How does EstateMap configure Passlib CryptContext to hash and verify passwords using Argon2id?',
        'q_tradeoff': 'What are the tradeoffs between memory cost, time cost, and server throughput when tuning Argon2id parameters?',
        'q_debug': 'How do you detect and prevent timing side-channel attacks during password verification in Python?',
        'q_sysdesign': 'How would you migrate a legacy system with 10 million MD5 or bcrypt password hashes to Argon2id without requiring users to reset their passwords?',
        'ans_framework': 'Highlight: 1) The threat model (GPU/ASIC parallel cracking), 2) Why memory hardness matters (Argon2id requires megabytes of RAM per thread, destroying GPU scalability), 3) Constant-time verification, 4) EstateMap security.py implementation and transparent upgrade strategy.',
        'conn_prev': 'Story 06 established logging and tracing; Story 14 implements user credential security.',
        'conn_next': 'Story 15 builds upon secure password verification to issue stateless JSON Web Tokens (JWT).',
        'checklist': [
            'Can explain why memory-hard hashing is required for modern passwords',
            'Can implement Argon2id hashing and verification using passlib',
            'Can explain the components of an Argon2id hash string ($argon2id$v=19$m=65536,t=3,p=4$...)',
            'Can explain how transparent password hash upgrades work on user login'
        ]
    })

    # Story 15
    stories.append({
        'num': 15,
        'title': 'Stateless JWT Authentication & Cryptographic Signature Verification',
        'points': 5,
        'why_exists': 'Stateful session authentication requires database or Redis lookups on every single HTTP request, creating database bottlenecks at scale. Stateless JSON Web Tokens (JWT) allow backend microservices and serverless instances to verify user identity cryptographically in-memory.',
        'problem_solved': 'Session storage lookups add 5-20ms of database latency to every API call and fail when sessions cannot be shared across horizontally scaled backend replicas.',
        'prereq_stories': ['Story 03 — Type-Safe Configuration with Pydantic-Settings', 'Story 14 — Password Hashing with Argon2id & Cryptographic Salting'],
        'prereq_concepts': ['JWT Structure (Header.Payload.Signature)', 'HMAC-SHA256 (HS256) symmetric signing', 'FastAPI OAuth2PasswordBearer', 'Token expiration (exp claim)'],
        'depends_on': [3, 14],
        'unlocks': [16, 48, 80],
        'readiness': [
            'Understand the difference between stateful sessions and stateless tokens',
            'Familiar with Authorization: Bearer <token> HTTP headers',
            'Able to explain how cryptographic signatures prevent token tampering'
        ],
        'objectives': [
            'Generate signed JWT access tokens containing user ID, email, role, and expiration timestamps',
            'Implement FastAPI dependency get_current_user using OAuth2PasswordBearer to validate tokens on protected routes',
            'Handle expired, malformed, and tampered tokens gracefully with RFC 7807 401 Unauthorized responses'
        ],
        'concepts': [
            'Stateless Authentication: Validating user claims entirely via cryptographic signature verification without querying the session database',
            'HS256 Signing: Using a shared SECRET_KEY with HMAC-SHA256 to sign and verify the JWT header and payload',
            'Token Claims: Standardized payload fields (sub: subject ID, exp: expiration timestamp, iat: issued at, role: user role)',
            'Dependency Injection in FastAPI: Extracting and validating Bearer tokens transparently before route handlers execute'
        ],
        'impl': 'backend/app/core/security.py implements create_access_token(data: dict, expires_delta: timedelta) -> str using python-jose. backend/app/api/deps.py implements oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login") and async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User.',
        'files': [
            'backend/app/core/security.py (create_access_token)',
            'backend/app/api/deps.py (get_current_user, get_current_active_user)',
            'backend/app/api/v1/endpoints/auth.py'
        ],
        'data_flow': 'Client POST /auth/login with credentials -> Backend verifies Argon2id hash -> Generates signed JWT with sub=user_id, exp=now+60m -> Returns {access_token, token_type: "bearer"} -> Client sends Authorization: Bearer <token> on future requests -> FastAPI get_current_user dependency decodes JWT, verifies HS256 signature, checks exp -> Injects authenticated User into route handler',
        'lab_standalone': '''Build a standalone JWT authentication module:
1. Install python-jose and passlib.
2. Define create_token(user_id: int, secret: str) -> str with 15-minute expiration.
3. Define decode_token(token: str, secret: str) -> dict that extracts user_id or raises InvalidTokenError if expired or tampered.
4. Test with a tampered token (alter 1 character in payload) and verify signature verification fails.''',
        'lab_mapping': 'Inspect backend/app/api/deps.py to see how get_current_user extracts the user from the database or token claims and injects it into protected endpoints like POST /properties.',
        'acceptance_criteria': [
            'POST /api/v1/auth/login with valid credentials returns a valid JWT access token.',
            'Protected endpoints return HTTP 401 Unauthorized if Authorization header is missing, expired, or tampered.',
            'Modifying any character in the JWT payload immediately invalidates signature verification.',
            'Token expiration timestamp (exp) is strictly enforced by python-jose.'
        ],
        'evidence': [
            'Login request: curl -X POST http://localhost:8000/api/v1/auth/login -d "username=demo@estatemap.ai&password=password" -> verify token response.',
            'Protected request: curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/auth/me -> verify user profile JSON.'
        ],
        'outcome_conceptual': 'Mastery of stateless authentication architecture, cryptographic signature verification, and FastAPI security dependency injection.',
        'outcome_impl': 'Ability to implement complete JWT issuance, verification, and protected endpoint decorators in FastAPI from scratch.',
        'outcome_interview': 'Ability to explain how JWT signatures work mathematically and articulate the tradeoffs between stateless JWTs and stateful sessions.',
        'mistakes': [
            'Using None as algorithm or allowing algorithm switching (alg: "none" exploit).',
            'Storing sensitive data (like plaintext passwords or internal credit card numbers) in the JWT payload (JWT payloads are Base64 encoded, not encrypted).',
            'Using a short, predictable SECRET_KEY that can be brute-forced offline using hashcat.'
        ],
        'debug_symptom': 'jose.exceptions.JWTError: Signature verification failed on all incoming client requests.',
        'debug_investigate': 'Check if SECRET_KEY or ALGORITHM differs between token generation and token decoding (e.g. env var mismatch).',
        'debug_goal': 'Ensure centralized Settings singleton supplies identical SECRET_KEY and ALGORITHM to both create_access_token and decode_token.',
        'tradeoffs': [
            'Stateless JWT vs Stateful Redis Sessions: Stateless JWT eliminates database lookups on every request, but instant token revocation requires a token blocklist in Redis.',
            'Short-lived Access Token + Refresh Token vs Long-lived Access Token: Short-lived access tokens (15-60m) minimize exposure window if a token is intercepted.'
        ],
        'prod_current': 'HS256 signed JWTs with 60-minute expiration validated via FastAPI Depends(get_current_user).',
        'prod_scale': 'Migrate from symmetric HS256 (shared secret) to asymmetric RS256/EdDSA (public/private key pairs) so edge API gateways can verify tokens without knowing the private signing key.',
        'q_basic': 'What are the three components of a JSON Web Token and what is the role of the cryptographic signature?',
        'q_impl': 'How does FastAPI\'s Depends(get_current_user) extract and validate a JWT Bearer token on protected endpoints?',
        'q_tradeoff': 'What are the security tradeoffs between stateless JWT tokens and server-side stateful sessions?',
        'q_debug': 'How do you handle immediate token revocation (e.g. on user logout or password reset) in a stateless JWT architecture?',
        'q_sysdesign': 'How do you design a secure authentication architecture for web and mobile clients using Short-Lived Access Tokens and Refresh Token Rotation?',
        'ans_framework': 'Explain: 1) JWT Anatomy (Header.Payload.Signature), 2) Signature verification mechanics (HMAC-SHA256 over Base64 header and payload), 3) The stateless advantage (zero DB lookup on requests), 4) The revocation challenge and EstateMap\'s implementation with FastAPI dependency injection.',
        'conn_prev': 'Story 14 established password hashing; Story 15 issues JWT tokens upon successful password verification.',
        'conn_next': 'Story 16 uses validated JWT user claims to enforce Role-Based Access Control (RBAC) and resource ownership.',
        'checklist': [
            'Can explain the mathematical difference between Base64 encoding and encryption in JWTs',
            'Can implement create_access_token and get_current_user in FastAPI',
            'Can configure algorithm whitelisting to prevent alg="none" exploits',
            'Can explain how refresh token rotation and Redis blocklisting enable secure revocation'
        ]
    })

    # Story 16
    stories.append({
        'num': 16,
        'title': 'Role-Based Authorization & Ownership Verification',
        'points': 3,
        'why_exists': 'Authentication verifies who a user is, but authorization enforces what that user is allowed to do. Missing authorization checks allow any logged-in user to modify or delete properties belonging to other users (Insecure Direct Object References - IDOR).',
        'problem_solved': 'IDOR vulnerabilities allow authenticated users to tamper with property listings, access admin metrics, or modify foreign accounts simply by changing the ID parameter in API requests.',
        'prereq_stories': ['Story 14 — Password Hashing with Argon2id & Cryptographic Salting', 'Story 15 — Stateless JWT Authentication & Cryptographic Signature Verification'],
        'prereq_concepts': ['Role-Based Access Control (RBAC)', 'Insecure Direct Object Reference (IDOR)', 'FastAPI Security Dependencies', 'Resource Ownership Checks'],
        'depends_on': [14, 15],
        'unlocks': [18, 98],
        'readiness': [
            'Understand the difference between 401 Unauthorized (unauthenticated) and 403 Forbidden (unauthorized)',
            'Familiar with User roles (e.g. "user", "agent", "admin")',
            'Able to explain why client-supplied user IDs must never be trusted without token verification'
        ],
        'objectives': [
            'Implement role-based authorization dependencies (require_role("admin"), require_role("agent"))',
            'Enforce resource ownership verification in domain services to prevent IDOR vulnerabilities',
            'Raise RFC 7807 403 Forbidden responses when an authenticated user attempts an unauthorized operation'
        ],
        'concepts': [
            'Principle of Least Privilege: Granting users the minimum permissions necessary to perform their tasks',
            'IDOR Defense: Verifying that property.owner_id == current_user.id or current_user.role == "admin" before permitting mutations',
            'Declarative Role Dependencies: Creating reusable FastAPI dependency factories for role enforcement',
            'Defense in Depth: Enforcing authorization at both the API routing layer and the domain service layer'
        ],
        'impl': 'backend/app/api/deps.py defines get_current_active_user and role checkers require_role("admin"). In backend/app/services/property_service.py, update_property and delete_property verify that the listing owner ID matches current_user.id unless current_user.role is "admin", raising AuthorizationError (mapped to HTTP 403) on mismatch.',
        'files': [
            'backend/app/api/deps.py (get_current_active_user, require_role)',
            'backend/app/services/property_service.py',
            'backend/app/models/user.py (UserRole enum)'
        ],
        'data_flow': 'Client sends PUT /api/v1/properties/123 with JWT -> get_current_user decodes token -> Endpoint passes current_user to PropertyService.update_property -> Service fetches Property 123 -> Checks if property.owner_id == current_user.id or current_user.is_admin -> If mismatch, raises AuthorizationError -> 403 Forbidden returned -> If valid, updates property and commits',
        'lab_standalone': '''Build an RBAC & Ownership verification lab:
1. Define User(id, role) and Document(id, owner_id, title).
2. Write a function verify_permission(user: User, doc: Document, action: str) -> bool.
3. Test: User 1 edits Document 1 (owner 1) -> Allowed.
4. Test: User 2 edits Document 1 (owner 1) -> Raises ForbiddenError.
5. Test: Admin edits Document 1 (owner 1) -> Allowed.''',
        'lab_mapping': 'Inspect backend/app/services/property_service.py update_property method to verify the exact owner_id check before executing updates.',
        'acceptance_criteria': [
            'Standard users can create, update, and delete only their own property listings.',
            'Attempting to edit or delete a listing owned by another user returns HTTP 403 Forbidden.',
            'Admin users can update or delete any property listing across the platform.',
            'Admin-only endpoints (e.g. system metrics) reject standard users with HTTP 403.'
        ],
        'evidence': [
            'Attempt IDOR update: Log in as User A, send PUT /api/v1/properties/<id_of_user_b> -> verify HTTP 403 Forbidden response.',
            'Run docker exec estatemap-backend pytest tests/unit/test_authorization.py.'
        ],
        'outcome_conceptual': 'Clear understanding of authorization architectures, IDOR prevention, and multi-tenant resource protection.',
        'outcome_impl': 'Ability to design and implement robust RBAC and ownership verification checks in FastAPI and SQLAlchemy services.',
        'outcome_interview': 'Ability to explain how to prevent OWASP Top 10 Broken Access Control and IDOR vulnerabilities in REST APIs.',
        'mistakes': [
            'Relying on frontend UI to hide "Edit" or "Delete" buttons without enforcing backend ownership validation.',
            'Accepting owner_id directly in the request body (e.g. {"owner_id": 2}) instead of extracting it securely from the validated JWT token.',
            'Returning 404 Not Found when a user lacks permission (can sometimes be intentional for security obscurity, but confusing if not standardized).'
        ],
        'debug_symptom': 'User receives HTTP 403 Forbidden when trying to update a property they legitimately created.',
        'debug_investigate': 'Check if current_user.id type (UUID vs Integer) matches property.owner_id type in database and repository query.',
        'debug_goal': 'Ensure consistent type casting between user token claims and database foreign keys.',
        'tradeoffs': [
            'Role-Based Access Control (RBAC) vs Attribute-Based Access Control (ABAC): RBAC is simple, fast, and sufficient for EstateMap; ABAC adds fine-grained policy engines (Opa/Casbin) for complex enterprise hierarchies.',
            'Route-level authorization vs Service-level ownership checks: Service-level ownership checks ensure business logic is protected regardless of which route or background worker invokes it.'
        ],
        'prod_current': 'FastAPI dependency injection for role checks combined with service-level ownership validation against PostgreSQL owner_id.',
        'prod_scale': 'Adopt Open Policy Agent (OPA) or AWS Cedar for externalized, audited policy evaluation across distributed microservices.',
        'q_basic': 'What is the difference between Authentication (401) and Authorization (403)?',
        'q_impl': 'How does EstateMap prevent Insecure Direct Object References (IDOR) when updating property listings?',
        'q_tradeoff': 'What are the tradeoffs between Role-Based Access Control (RBAC) and Attribute-Based Access Control (ABAC)?',
        'q_debug': 'How do you audit an existing API codebase to detect missing authorization checks on destructive endpoints (POST/PUT/DELETE)?',
        'q_sysdesign': 'How would you design a fine-grained permission system allowing real estate agency managers to manage all properties listed by agents within their branch?',
        'ans_framework': 'Explain: 1) The vulnerability definition (IDOR / Broken Object Level Authorization), 2) Why client-supplied IDs must never be trusted, 3) EstateMap 2-layer defense (JWT subject extraction + Service-layer owner_id equality check), 4) Admin override capabilities.',
        'conn_prev': 'Story 15 established user identity via JWT; Story 16 enforces permissions based on that identity.',
        'conn_next': 'Story 17 implements HTTP security headers, CORS policies, and defense-in-depth middleware.',
        'checklist': [
            'Can explain what an IDOR vulnerability is and provide a real-world attack example',
            'Can implement a custom require_role dependency factory in FastAPI',
            'Can write automated tests that assert 403 Forbidden on cross-user modification attempts',
            'Can design database schemas with explicit owner foreign keys to support ownership checks'
        ]
    })

    # Story 17
    stories.append({
        'num': 17,
        'title': 'Security Headers, CORS Policy & Defense-in-Depth',
        'points': 3,
        'why_exists': 'Web applications face browser-based attacks including Cross-Origin Resource Sharing (CORS) misconfigurations, Cross-Site Scripting (XSS), clickjacking, and MIME-type sniffing. Security headers instruct modern browsers to enforce strict security boundaries.',
        'problem_solved': 'Overly permissive CORS configurations (allow_origins=["*"] with credentials) allow malicious third-party websites to make authenticated cross-origin requests and steal sensitive real estate user data.',
        'prereq_stories': ['Story 01 — Python Project Structure & Clean Architecture', 'Story 15 — Stateless JWT Authentication & Cryptographic Signature Verification'],
        'prereq_concepts': ['Cross-Origin Resource Sharing (CORS)', 'HTTP Security Headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options)', 'Defense-in-Depth principle'],
        'depends_on': [1, 15],
        'unlocks': [81, 98],
        'readiness': [
            'Understand browser Same-Origin Policy (SOP)',
            'Familiar with CORS preflight OPTIONS requests',
            'Able to explain how X-Frame-Options prevents clickjacking attacks'
        ],
        'objectives': [
            'Configure strict FastAPI CORSMiddleware with explicit whitelisted frontend origins',
            'Implement custom middleware to inject essential security headers (X-Content-Type-Options, X-Frame-Options, Strict-Transport-Security)',
            'Validate that preflight CORS requests succeed without exposing authorization credentials to unauthorized domains'
        ],
        'concepts': [
            'Same-Origin Policy (SOP): Fundamental browser security mechanism restricting how documents loaded from one origin interact with resources from another',
            'CORS Whitelisting: Explicitly granting cross-origin access only to trusted frontend origins (e.g. http://localhost:3000, https://estatemap.ai)',
            'Clickjacking Defense: Preventing unauthorized UI redressing using X-Frame-Options: DENY and Content-Security-Policy frame-ancestors',
            'MIME-Sniffing Prevention: Forcing browsers to adhere to declared Content-Type using X-Content-Type-Options: nosniff'
        ],
        'impl': 'backend/app/main.py configures CORSMiddleware using settings.CORS_ORIGINS (whitelisting frontend URLs, allowing standard methods and headers, with credentials enabled). Custom middleware injects X-Content-Type-Options: nosniff, X-Frame-Options: DENY, and X-XSS-Protection: 1; mode=block on all responses.',
        'files': [
            'backend/app/main.py (CORSMiddleware)',
            'backend/app/core/middleware.py',
            'backend/app/core/config.py (CORS_ORIGINS)'
        ],
        'data_flow': 'Browser sends OPTIONS preflight request -> CORSMiddleware checks Origin header against whitelist -> Returns Access-Control-Allow-Origin: http://localhost:3000 -> Browser sends actual GET/POST -> Response enriched with security headers -> Browser renders securely',
        'lab_standalone': '''Build a security headers verification test:
1. Create a FastAPI app with CORSMiddleware allowing only http://localhost:3000.
2. Add middleware adding X-Frame-Options: DENY.
3. Test request with Origin: http://malicious.com -> verify Access-Control-Allow-Origin is absent.
4. Test request with Origin: http://localhost:3000 -> verify CORS headers and X-Frame-Options are present.''',
        'lab_mapping': 'Inspect backend/app/main.py lines 55-75 to see how CORSMiddleware and settings.CORS_ORIGINS are initialized.',
        'acceptance_criteria': [
            'CORS allows requests only from explicitly configured frontend origins in settings.CORS_ORIGINS.',
            'Wildcard allow_origins=["*"] is strictly prohibited when allow_credentials=True is enabled.',
            'All responses include X-Content-Type-Options: nosniff and X-Frame-Options: DENY.',
            'Preflight OPTIONS requests return HTTP 200 with appropriate Access-Control-Allow-Methods headers.'
        ],
        'evidence': [
            'Send CORS preflight: curl -i -X OPTIONS http://localhost:8000/api/v1/properties -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: GET" -> verify Access-Control-Allow-Origin header.',
            'Inspect security headers: curl -i http://localhost:8000/health -> verify X-Frame-Options: DENY.'
        ],
        'outcome_conceptual': 'Comprehensive understanding of browser security boundaries, CORS protocol mechanics, and HTTP header defenses.',
        'outcome_impl': 'Ability to configure production-grade CORS policies and security header middleware in FastAPI.',
        'outcome_interview': 'Ability to articulate why CORS is a browser security mechanism (not a backend firewall) and explain defense-in-depth principles.',
        'mistakes': [
            'Thinking CORS protects the backend against malicious curl or backend-to-backend attacks (CORS is enforced exclusively by web browsers).',
            'Setting allow_origins=["*"] with allow_credentials=True which modern browsers reject as an insecure combination.',
            'Failing to handle CORS preflight OPTIONS requests before authentication middleware, causing 401 errors on preflights.'
        ],
        'debug_symptom': 'Browser console displays "Cross-Origin Request Blocked: The Same Origin Policy disallows reading the remote resource at..."',
        'debug_investigate': 'Check if the frontend origin URL (including protocol and port, e.g. http://localhost:3000) exactly matches an entry in backend CORS_ORIGINS.',
        'debug_goal': 'Add the exact client origin to CORS_ORIGINS environment variable in .env or docker-compose.yml.',
        'tradeoffs': [
            'Strict CORS Whitelist vs Permissive Wildcard: Strict whitelist prevents credential leakage and cross-origin attacks; requires maintaining environment-specific domain lists.',
            'Application-level security headers vs Reverse Proxy (Nginx/Cloudflare) headers: Implementing in application ensures security in local Docker dev while reverse proxy provides caching at edge.'
        ],
        'prod_current': 'CORSMiddleware configured from Settings with explicit frontend URL whitelisting and security header middleware.',
        'prod_scale': 'Offload SSL/TLS termination and HSTS/CSP header enforcement to Cloudflare or AWS CloudFront edge CDN.',
        'q_basic': 'What is CORS and why is it enforced by browsers rather than backend servers?',
        'q_impl': 'How does EstateMap configure CORS in FastAPI to allow authenticated requests from the Next.js frontend while rejecting unauthorized origins?',
        'q_tradeoff': 'What is the danger of setting allow_origins=["*"] in an API that accepts cookie or Bearer token authentication?',
        'q_debug': 'Why does a browser send an OPTIONS request before a POST or PUT request, and how must the backend respond?',
        'q_sysdesign': 'How do you design a Content Security Policy (CSP) and security header strategy for a real estate web platform that loads map tiles from external CDN providers?',
        'ans_framework': 'Explain: 1) The purpose of Same-Origin Policy (SOP) and CORS, 2) The preflight OPTIONS handshake, 3) Why CORS does not protect against curl/bots, 4) EstateMap\'s strict origin whitelisting and security header injection.',
        'conn_prev': 'Story 16 established RBAC and ownership; Story 17 hardens HTTP transport and browser communication.',
        'conn_next': 'Story 07 (or Story 18) applies these security mechanisms to database models and property domain operations.',
        'checklist': [
            'Can explain the difference between SOP and CORS',
            'Can configure FastAPI CORSMiddleware with explicit origin whitelists',
            'Can list the top 4 essential HTTP security headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options)',
            'Can diagnose and resolve CORS preflight errors in under 2 minutes'
        ]
    })

    return stories
