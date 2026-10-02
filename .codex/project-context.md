# Project Context

## System Architecture

This repository is a Django 5.2 REST backend. It uses PostgreSQL, Redis, RabbitMQ, Celery worker/beat, Flower, and Adminer in `compose.yaml`. Django settings are selected by `DJANGO_ENV`: `settings/development.py` or `settings/production.py`, both built on `settings/base.py`. Celery imports email, notification, and resume-parser tasks; `job.tasks` creates asynchronous application-export ZIPs.

## Domains and Entry Points

- `users`: custom email-login `User`, JWT auth, profile API, password-reset APIs.
- `student`, `company`, `course`: student and company profiles plus course/batch ownership.
- `job`: jobs, resumes, applications, dynamic attributes, admin views, and exports.
- `configs`: resume limits.

Project routes are in `placement_portal_enterprise_2_backend/urls.py`: `/api/auth/`, `/job/`, `/student/`, Django admin, Swagger/Redoc, and application-resume viewing. DRF routers expose jobs, applications, and resumes beneath `/job/`.

## Authentication and Authorization

DRF uses `dj_rest_auth.jwt_auth.JWTCookieAuthentication`; JWT cookies are `access` and `refresh`, configured HTTP-only and `SameSite=Lax`. The job, application, and resume viewsets declare `IsAuthenticated`. Role helpers and role-specific list/detail behavior exist, but application creation itself only requires authentication then assumes `request.user.student_profile`; it does not explicitly enforce `UserRole.STUDENT`.

## Core Data Flows

Students list/retrieve jobs filtered to their batch. Resume upload uses `ResumeCreateSerializer`, then `Resume.clean()`/`save()` enforce PDF, size, and configured per-student count rules. An application is submitted to `POST /job/applications/` with `job`, integer `resume_id`, and optional `answers` mapping.

`ApplicationViewSet.create()` validates resume ownership manually, copies job fields and student email into `Application`, then inside `transaction.atomic()` writes the application, its answer snapshots, and reusable student values. Application data can be exported asynchronously as an Excel file plus resumes in a ZIP through the Django admin action.

Application status is a nullable FK to `ApplicationStatus`; new model-created applications default to the seeded `applied` status row, while API serialization presents any null status as `Applied`. The authenticated `/job/application-statuses/` endpoint lists and creates status rows. Application status updates accept a status name or status ID and continue returning the status name.

## Dynamic Attributes

`Attribute` defines a name, slug, and data type. `JobAttribute` attaches an attribute to a job and stores required/visibility/filter/order settings. `ApplicationAttributeValue` snapshots the submitted label, slug, type, required flag, and stringified value. `StudentAttributeValue` stores the latest reusable JSON value per `(student, attribute)` and prepopulates job-detail fields.

## Invariants and Current Limitations

`Application` is unique per `(student, job)` and retains job/email snapshot fields; its job, student, and resume foreign keys use cascading deletion. A `JobAttribute` is unique per `(job, attribute)`; student values are unique per `(student, attribute)`.

Application creation bypasses a create serializer. It does not currently validate complete required answers or answer values against dynamic data types, and it does not enforce batch eligibility, deadline, or an explicit student role. A nonexistent but truthy job ID can fail before its `try` block. Existing app `tests.py` files are largely generated empty test shells.

## Frontend Boundary and Recent Work

No frontend source is present here; client payload/error handling cannot be inferred beyond the API code. Recent Git history records dynamic form/admin model work, application submission/list/detail updates, profile APIs, application counts/admin links, and ZIP export of Excel plus resumes.
