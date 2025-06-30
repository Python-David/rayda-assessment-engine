# Multi-Tenant SaaS Platform Backend with External Integrations

## Project Overview

This project is a robust, production-grade backend system designed to support a multi-tenant SaaS platform combined with external API integration capabilities. It emphasizes secure tenant isolation, role-based access control (RBAC), and a scalable, extensible integration engine.

## Architectural Decisions

### Multi-Tenant Design

Each organization (tenant) has fully isolated data, scoped by org_id. This prevents data leaks and enforces strong security boundaries.

### Controlled Onboarding (No Public Registration)

Superadmins create organizations, and admins manage users internally. This aligns with real-world SaaS practices where companies want strict control over who can access their data.

### Role-Based Access Control (RBAC)

- Superadmin: Global permissions. Can create organizations and assign initial admins.
- Admin: Scoped to org_id. Can create/manage users in their org.
- User: Scoped to org_id, manages only their own profile.

Principles:

- Least Privilege: Only necessary permissions.
- Explicit Control: No implicit escalations.
- Strict Tenant Isolation: No cross-org actions.
- Security Over Convenience: No self-service registration.

### Tech Stack

- FastAPI: High-performance API framework.
- SQLAlchemy: ORM and DB toolkit.
- Alembic: Migrations.
- Pydantic: Validation and settings.
- PostgreSQL: Database.
- JWT (python-jose): Authentication.
- Docker & Docker Compose: Containerization.
- Celery + Redis + Flower: Async task processing and monitoring.
- Passlib: Password hashing.
- SlowAPI: Rate limiting.

## Phase 1: Multi-Tenant Platform

#### Key Features

- JWT-based authentication with role enforcement.
- Fully scoped API endpoints.
- Initial superadmin bootstrap.
- Dynamic organization and user creation.
- Audit logs for sensitive actions.
- Role-based permission checks in each route.

#### Tests

Verified authentication, role enforcement, and data isolation through unit and integration tests.

## Phase 2: External Integration Engine

### Design Decisions & Architecture Notes

#### Celery + Redis + Flower

Why: Needed to decouple webhook request-response from long-running external sync operations.

Setup:

- Redis as broker and backend.
- Flower for real-time monitoring.
- Celery configured for retries and exponential backoff.

#### Failure Simulation

Configurable using:

FORCE_SERVICE_FAILURES=2
ENABLE_RANDOM_FAILURES=false

Deterministic failures to explicitly test retry logic.

Why: Enables predictable failure scenarios to demonstrate robust retry and error handling during assessment.

#### Celery Retry Config

Controlled via:

CELERY_RETRY_BACKOFF_BASE=2
CELERY_MAX_RETRIES=3

Exponential backoff (2, 4, 8 seconds). Flexible and environment-specific.

#### Single Integration Queue

A single integration_queue used for clarity.

Why: Simplifies demonstration during assessment. In production, easily extensible to multiple queues (e.g., billing, notifications).

#### New Models: Subscription & CommunicationLog

Subscription: Persistent subscription and billing data for lifecycle and audit.

CommunicationLog: Records notification delivery states for troubleshooting and transparency.

Other Model Updates:

- external_id added to User for webhook mapping.
- hashed_password made nullable for SSO scenarios.
- Added User status enum for lifecycle management.

#### RBAC and Webhooks

Webhooks treated as system-level integrations, not user-level actions.

Enforced Rules:

- Organization must exist.
- Syncs user data within existing orgs.
- Never auto-create orgs to protect tenant structure.

#### Nullable hashed_password & SSO Lifecycle

Users created by webhooks start with hashed_password = None.

Status set to pending.

Activated later via invite or SSO login.

Security: Users without hashed passwords cannot log in using local credentials until explicitly activated.

## Phase 3: External Webhook Processing & Health Monitoring

### Design Decisions & Architecture Notes

#### Tenant-Aware Webhook Endpoints

Separate endpoints for User, Payment, and Communication services.

Supports both single and batch payloads (via Pydantic unions).

Async processing using Celery (integration_queue).

Why: Batch support increases throughput (e.g., Stripe). Pydantic ensures strong validation and security.

#### Idempotency Handling

Every event includes a unique event_id.

Events checked in WebhookLog before processing to skip duplicates.

Why: Prevents duplicate writes and ensures safe replays by external services.

#### Webhook Logging & Tracking

Every webhook stored in WebhookLog.

Contains event_id, service, org_id, status, and payload snapshot.

Why: Full auditability, historical tracking, and easier debugging.

#### Integration Health Endpoint

/integrations/status: Shows health summary per service.

Tracks:

- Last successful event.
- Last event ID.
- Computed status: healthy, degraded, or error.

Why: Provides admins with integration observability.

#### Rate Limiting via SlowAPI

Per-IP rate limiting enforced on webhooks.

Controlled via environment variables:

WEBHOOK_RATE_LIMIT_COUNT
WEBHOOK_RATE_LIMIT_PERIOD

Example: 10/minute.

Why: Protects backend from overload and ensures fair usage.

#### External Service Simulation & Failures

User, Payment, and Communication services simulated.

Deterministic error behavior via FORCE_SERVICE_FAILURES and ENABLE_RANDOM_FAILURES.

Why: Enables controlled end-to-end testing, supports CI stability.

#### Testing Strategy

Heavy use of patching to isolate sync logic.

Webhook tests verify idempotency, routing correctness, and rate limiting.

Authenticated flow checks ensure RBAC enforcement during webhook integrations.

## Security Considerations

- JWT Authentication: Strict role checks.
- Tenant Isolation: Scoped strictly to org_id.
- Idempotency: Blocks replay and duplicate writes.
- Strict Validation: Pydantic models at every input layer.
- Rate Limiting: Additional defense layer.
- Password Hashing: Bcrypt via Passlib.

## Future Improvements

- Fully integrated audit logs for webhooks and external sync.
- Circuit breaker pattern for external APIs.
- Advanced bulk webhook support with granular error collection.
- Dynamic queue scaling with separate priority queues.
- Production-grade SSO onboarding flow.

## Setup & Running

### Environment Variables

.env.template

### Docker

docker-compose up --build

- Automatically runs migrations.
- Boots superadmin.
- Starts FastAPI at http://0.0.0.0:8000.

## Tests

### How to run

pip install pytest pytest-asyncio httpx
pytest

- Tests cover RBAC, tenant isolation, webhook flows, idempotency, rate limiting, and audit logging.
- Audit log tests verify that all critical data modifications (e.g., user creation, organization creation, webhook sync events) are consistently logged in the audit trail.
- Fixtures and patching isolate side effects and async tasks to ensure repeatable, reliable tests.

## API Endpoints Summary

| Endpoint                       | Method | Role         | Purpose                                              |
|--------------------------------|---------|--------------|------------------------------------------------------|
| /users/login                   | POST    | All          | JWT login.                                          |
| /users/me                      | GET     | All          | Get current user profile.                           |
| /users/                        | POST    | Admin        | Create users and/or additional admins in org.       |
| /orgs/                         | POST    | Superadmin   | Create organization and initial admin.              |
| /orgs/{org_id}                | GET     | All          | Get organization details.                           |
| /integrations/status          | GET     | Admin, Superadmin | View external integrations health summary.      |
| /webhooks/user-service        | POST    | System       | Receive user service webhooks (single/batch).      |
| /webhooks/payment-service     | POST    | System       | Receive payment service webhooks (single/batch).   |
| /webhooks/communication-service | POST | System       | Receive communication service webhooks (single/batch). |

## Future Improvements

- Fully integrated audit logs for webhooks and external sync.
- Circuit breaker pattern for external APIs.
- Advanced bulk webhook support with granular error collection.
- Dynamic queue scaling with separate priority queues.
- Production-grade SSO onboarding flow.
- Additional update and delete endpoints for users and organizations to support full lifecycle management and administrative flexibility.

## Credits

Architect & Developer: David Nwobodo

## Final Note

This project showcases a secure, scalable, and extensible SaaS backend architecture, with a strong focus on robust external integrations. It emphasizes thoughtful design, explicit security boundaries, and real-world operational concerns.

"Documentation is not just about code, it's about ideas and ideas live forever."
