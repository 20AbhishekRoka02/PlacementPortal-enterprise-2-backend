# Project Context

## System Architecture

This repository is a Django 5.2 REST backend. It uses PostgreSQL, Redis, RabbitMQ, Celery worker/beat, Flower, and Adminer in `compose.yaml`. Django settings are selected by `DJANGO_ENV`: `settings/development.py` or `settings/production.py`, both built on `settings/base.py`. Celery imports email, notification, and resume-parser tasks; `job.tasks` creates asynchronous application-export ZIPs.

## Domains and Entry Points

- `users`: custom email-login `User`, JWT auth, profile API, password-reset APIs.
- `student`, `company`, `course`: student profiles, independent company records, and course/batch ownership. Companies no longer belong to user accounts.
- `job`: jobs, resumes, applications, dynamic attributes, admin views, and exports.
- `configs`: resume limits.

Project routes are in `placement_portal_enterprise_2_backend/urls.py`: `/api/auth/`, `/job/`, `/company/`, `/student/`, Django admin, Swagger/Redoc, and application-resume viewing. DRF routers expose jobs, applications, resumes, attributes, and application statuses beneath `/job/`, and company list/detail/create routes beneath `/company/`.

## Authentication and Authorization

DRF uses `dj_rest_auth.jwt_auth.JWTCookieAuthentication`; JWT cookies are `access` and `refresh`, configured HTTP-only and `SameSite=Lax`. The `UserRole` choices are admin, university, student, and placement officer; there is no Company user role. Existing Company-role accounts are retained by migration with `role=NULL`, `is_staff=False`, and active status preserved. Company list/detail/create APIs and job/attribute creation use `is_student(user) == "staff"` for authorization. Application creation still only requires authentication then assumes `request.user.student_profile`; it does not explicitly enforce `UserRole.STUDENT`.

## Core Data Flows

Students list/retrieve jobs filtered to their batch. Resume upload uses `ResumeCreateSerializer`, then `Resume.clean()`/`save()` enforce PDF, size, and configured per-student count rules. An application is submitted to `POST /job/applications/` with `job`, integer `resume_id`, and optional `answers` mapping.

`ApplicationViewSet.create()` validates resume ownership manually, copies job fields and student email into `Application`, then inside `transaction.atomic()` writes the application, its answer snapshots, and reusable student values. Application data can be exported asynchronously as an Excel file plus resumes in a ZIP through the Django admin action.

Application status is a nullable FK to `ApplicationStatus`; new model-created applications default to the seeded `applied` status row, while API serialization presents any null status as `Applied`. The authenticated `/job/application-statuses/` endpoint lists and creates status rows. Application status updates accept a status name or status ID and continue returning the status name.

## Dynamic Attributes

`Attribute` defines a name, slug, and data type. `JobAttribute` attaches an attribute to a job and stores required/visibility/filter/order settings. `ApplicationAttributeValue` snapshots the submitted label, slug, type, required flag, and stringified value. `StudentAttributeValue` stores the latest reusable JSON value per `(student, attribute)` and prepopulates job-detail fields.

Job and attribute creation is exposed through REST APIs. Authenticated `GET /job/attributes/` lists the catalog; `POST /job/attributes/` creates an attribute from `name` and `data_type` and returns its generated slug. Both attribute creation and `POST /job/jobs/` require `is_student(request.user) == "staff"`. Job creation accepts either an existing Company primary key in `company` or new company fields in write-only `company_data`, never company-name matching. Company creation, the job, and optional `JobAttribute` rows are atomic. The existing-ID request contract remains supported. The intended sequence for a new attribute is to create it first, then submit its returned ID with the job. Attribute names are not unique in the current model.

Staff users can list/retrieve companies and create them through `/company/companies/`; Company records contain `name`, `website`, `hr_phone_number`, and `hr_email`, with no User FK. During migration, each linked user’s email is copied to its Company’s `hr_email`; Company IDs and job references are preserved. The Company group and its grants are removed. Resume viewing is available to `ADMIN`, `UNIVERSITY`, and `PLACEMENT_OFFICER` roles, as well as superusers.

## Invariants and Current Limitations

`Application` is unique per `(student, job)` and retains job/email snapshot fields; its job, student, and resume foreign keys use cascading deletion. A `JobAttribute` is unique per `(job, attribute)`; student values are unique per `(student, attribute)`.

Application creation bypasses a create serializer. It does not currently validate complete required answers or answer values against dynamic data types, and it does not enforce batch eligibility, deadline, or an explicit student role. A nonexistent but truthy job ID can fail before its `try` block. Existing app `tests.py` files are largely generated empty test shells.

## Frontend Boundary and Recent Work

No frontend source is present here; client payload/error handling cannot be inferred beyond the API code. Recent functionality includes staff-gated Company list/create APIs, removal of Company-user coupling and role, inline Company creation during job creation, staff-gated job/attribute creation APIs, dynamic form/admin model work, application submission/list/detail updates, profile APIs, application counts/admin links, and ZIP export of Excel plus resumes.
