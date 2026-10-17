# Project Context

Last reviewed: 17 October 2026. Update this file with every non-trivial code,
schema, API, workflow, or infrastructure change.

## System Architecture

This is a Django 5.2 / DRF backend, targeting Python 3.11. PostgreSQL stores
application data; Redis is the cache/result backend; RabbitMQ brokers Celery
tasks. `compose.yaml` starts Django, PostgreSQL, Adminer, RabbitMQ, Redis,
Celery worker, Celery Beat, and Flower. Settings are selected from `DJANGO_ENV`
(`settings.development` or `settings.production`) and extend `settings.base`.

Celery imports email, notification, resume-parser, and job-export tasks. Only
password-reset email and application export currently have substantive flows;
notification and resume-parser tasks are placeholders/not implemented.

## Applications and Routes

| Area | Responsibility | Main route prefix |
| --- | --- | --- |
| `users` | Custom email-login user, JWT auth, password reset, basic user profile | `/api/auth/` |
| `student` | Student profile display/update | `/student/` |
| `company` | Independent company contact records | `/company/companies/` |
| `course` | Course and batch data | `/course/batches/` |
| `job` | Jobs, resumes, applications, attributes, statuses, exports | `/job/` |
| `configs` | Admin-managed resume configuration | Django admin only |

The project also exposes `/admin/`, `/swagger/`, `/redoc/`, and
`/application/<application_id>/resume/`. Router resources beneath `/job/` are
`jobs`, `applications`, `resumes`, `attributes`, and `application-statuses`.
There is no frontend source in this repository.

## Identity and Access Model

`users.User` authenticates by unique email. DRF uses HTTP-only JWT cookies named
`access` and `refresh` (`SameSite=Lax`; production additionally sets `Secure`).
Roles are `admin`, `university`, `student`, and `placement_officer`; Company is
not a user role and `Company` has no User foreign key. Legacy Company accounts
were retained as active role-less non-staff accounts by migration.

The helper `is_student()` classifies any non-student role as `staff`. Therefore
job/attribute creation and Company APIs are staff-gated, but this is role-based
rather than `is_staff`-based. Resume file viewing is restricted to superusers
or `ADMIN`, `UNIVERSITY`, and `PLACEMENT_OFFICER` roles.

## Core Data Model and Flows

`Course` owns `Batch`; a `Student` is a one-to-one User profile and can belong
to one batch. A `Job` belongs to one Company and one or more Batches. Job
creation accepts `batches` as a non-empty list of batch IDs. Students see jobs
linked to their batch; staff see all jobs and the applications embedded in job
detail. Job list/detail responses expose batch names under `batches`. The
schema migration drops the old single-batch relation without migrating its
assignments; existing data is managed separately.

Staff create an Attribute first (`POST /job/attributes/`), then create a Job.
A job payload supplies exactly one of an existing `company` ID or write-only
`company_data`, plus optional `job_attributes`. The Company, Job, and attribute
links are created atomically. `JobAttribute` is unique per `(job, attribute)`.

Students upload PDF resumes through `/job/resumes/`. Upload validation limits
the file to 20 KB and `Resume.clean()` also enforces the singleton
`ResumeConfig.max_number_of_resumes` under a row lock. `max_resume_size` exists
in configuration but is not yet used: the 20 KB size limit is currently
hard-coded in model and serializer. Resume parsing/status tracking is not wired
into the upload flow.

Application submission is `POST /job/applications/` with `job`, integer
`resume_id`, and optional `answers` keyed by Attribute ID. The view verifies
that the resume belongs to the current student's profile, snapshots the job
title/description/location/salary and student email, then atomically creates:

1. the `Application`;
2. `ApplicationAttributeValue` records containing submitted field snapshots;
3. current `StudentAttributeValue` records for future form prefill.

An Application is unique per `(student, job)`. Status is a protected nullable
foreign key to `ApplicationStatus`; migration seeds legacy statuses including
`Applied`, and new ORM-created applications default to its `applied` code. API
output renders a null value as `Applied`. Application updates use the default
ModelViewSet serializer and accept a status ID or existing status name.

Application exports support both the Django-admin Job action and staff-only API
access. `POST /job/application-exports/` accepts exactly one `job_id`, creates
an export requested by the authenticated staff user, and queues the task after
the database transaction commits. `GET /job/application-exports/` lists every
export to staff, and `GET /job/application-exports/<id>/` returns one export's
status; both include the requester so the shared export history is attributable.
`GET /job/application-exports/<id>/download/` streams the ZIP only after it has
completed (otherwise `409 Conflict`).

`job.tasks` creates a ZIP containing `applications.xlsx` and readable attached
resumes. `ApplicationExport` records pending/processing/completed/failed state,
step (`queued`, spreadsheet, resumes, finalizing, terminal), totals and processed
counts for applications/resumes, percentage, timestamps, errors, and file
metadata. Progress updates are persisted by the worker so the client polls the
database-backed status rather than Celery state. Exports deliberately remain
one job per request.

## Dynamic Attributes: Important Boundary

`Attribute` is the shared field catalogue with data type and generated slug.
`JobAttribute` configures a catalogue field for a particular job (required,
visibility, filterability, order). `StudentAttributeValue` is the latest,
reusable JSON profile value, unique per `(student, attribute)`. In contrast,
`ApplicationAttributeValue` is immutable-in-intent submission snapshot data;
it stores the label, slug, type, required flag, and stringified answer without
a foreign key to Attribute. Do not collapse these two value types when changing
application or profile logic.

## Known Constraints and Follow-up Work

- Application creation assumes `request.user.student_profile`; it does not
  explicitly enforce the student role, job batch eligibility, or job deadline.
  An invalid truthy job ID is dereferenced before the transaction/error handler.
- Required dynamic answers, answers for only the job's attributes, and data-type
  validation are not enforced server-side. This is a priority for any dynamic
  attribute work.
- Several list/detail serializers perform related-object queries per row; use
  `select_related`/`prefetch_related` if extending these endpoints.
- Resume, job, and student foreign keys on Application currently use `CASCADE`.
  Deleting a resume deletes linked applications, despite the older planning note
  proposing `SET_NULL`; do not change this without deciding the retention
  contract and adding a migration/tests. The resume file is physically removed
  by `Resume.delete()`.
- Student-only endpoints and application retrieval assume a student profile;
  staff cannot retrieve an individual application through the current API.
  `BatchViewSet` has no authentication/authorization override.
- There is no pagination, deadline enforcement, or soft deletion. Production
  host/CORS settings remain permissive and should be hardened before deployment.

## Tests and Working Convention

Most meaningful automated coverage is in `job/tests.py` and `company/tests.py`:
application status migration/API behavior, roles, company migration/API behavior,
job and dynamic-attribute creation, atomic rollback, and staff export creation,
visibility, download gating, and persisted task progress. The other app test
files are empty shells. Run the focused app test first, then broader tests when
practical.

Before a non-trivial change, read the relevant sections here and inspect the
affected code path. Update this document in the same change set with factual
implemented behavior, changed contracts, migrations, and remaining decisions;
do not use it as a substitute for source-level verification.
