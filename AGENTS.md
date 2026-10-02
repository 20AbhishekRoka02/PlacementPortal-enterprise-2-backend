# Repository Guidelines

## Project

Django REST backend for a placement portal.

Main apps:

* `users/`
* `student/`
* `company/`
* `course/`
* `job/`
* `configs/`

Shared asynchronous services live under `services/`.

Use Python 3.11.

## Development

Common commands:

```bash
python manage.py migrate
python manage.py test
python manage.py test <app>
docker compose up --build
docker compose down
```

Use the existing Docker/Compose setup when the task involves the full application stack.

Do not commit `.env`, credentials, uploaded resumes, generated exports, or other runtime media.

## Code Conventions

Follow existing Django/Python patterns before introducing new abstractions.

* Python: `snake_case`
* Classes/models/serializers/views: `PascalCase`
* Keep functions focused.
* Keep serializers in `serializers.py`.
* Keep routes in `urls.py`.
* Keep background tasks in `tasks.py`.
* Generate Django schema changes through migrations.
* Reuse existing project patterns instead of creating parallel patterns.

Do not introduce a formatter, linter, framework, or architectural pattern unless explicitly requested.

## API and Backend Rules

Backend validation is the source of truth. Do not rely on frontend validation for security, authorization, required fields, datatype validation, or business rules.

Preserve existing API contracts unless the task explicitly requires an API change.

Check authorization and role permissions when modifying or adding endpoints.

Avoid N+1 database queries. Inspect query behavior when changing list/detail APIs or adding related data.

Prefer the existing ORM/query patterns in the project before introducing custom SQL.

## Placement Portal Domain Rules

### Applications

Application submission creates multiple related records and must remain atomic. Do not allow partial application creation.

Application data intentionally contains snapshot information from the job/student state at submission time. Do not remove or replace snapshot fields with relations merely to eliminate duplication without first understanding the purpose of the snapshot.

### Dynamic Attributes

The placement portal uses reusable dynamic attributes for job/student/application data.

Understand the distinction between:

* `JobAttribute`
* `StudentAttributeValue`
* `ApplicationAttributeValue`

Before changing these models, inspect existing serializers, APIs, validation, and data flow.

Application attribute values represent the submitted/snapshotted state and should not be treated as the student's current reusable profile values.

### Validation

Required fields and datatype rules must be enforced by the backend even when the frontend already performs validation.

When changing dynamic attribute validation, consider existing stored values and compatibility with existing applications.

## Testing

For backend changes:

1. Run the most focused relevant test first.
2. Add regression tests for bug fixes.
3. Test authorization and validation for affected endpoints.
4. Run the broader test suite when practical.

Do not claim a change is complete without verifying the relevant tests.

## Change Discipline

Before modifying code:

1. Inspect the existing implementation and related code paths.
2. Identify the smallest set of files that need changing.
3. Reuse existing patterns where possible.

Do not modify unrelated functionality.

Do not perform destructive database operations or delete production-like data without explicit confirmation.

When an architectural decision is unclear, explain the tradeoff before making a broad change.

## Documentation

Update project documentation when a change introduces or modifies an important architectural decision, workflow, API contract, or deployment process.

Do not create documentation for trivial implementation details.

## Git

Keep commits scoped and use concise imperative messages such as:

* `Add user profile API`
* `Fix application validation`

Never commit secrets, credentials, `.env` files, resumes, uploaded media, or generated runtime files.
