# FortuneBox — v0 baseline

A Flask + SQLite fortune-cookie application for the DFCS H4013 CA3 project.

## Features
- Guest homepage and account registration/login
- User role: draw random approved fortunes, view draw history, submit fortunes for approval
- Admin role: review/approve/reject submissions; create, edit and delete approved fortunes
- SQLite persistence via Flask-SQLAlchemy

## Run locally
1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Start the application: `python app.py`
4. Open `http://127.0.0.1:5000`

On first run, the database is created and seeded with sample fortunes and an admin account:
- Username: `admin`
- Password: `ChangeMe123!`

Set `ADMIN_PASSWORD` before first run to choose a different initial admin password.
Set `SECRET_KEY` to a random value before running outside a local development environment.

## Version 0 scope and limitations
This is the functional AI-generated baseline, not a security-hardened release. It includes basic authentication, password hashing and role checks because the brief requires authentication and access-controlled functionality. It intentionally does not yet implement the planned v1 hardening controls such as CSRF protection, secure cookie/session configuration, rate limiting, stronger server-side validation, audit logging, production configuration, or automated security headers. The Flask development server and debug mode are for local development only.

Do not deploy this version publicly or use real personal data. Test only in an isolated local environment with synthetic data.

## Suggested next steps for the group
- Review every route and understand the data flow.
- Create a Git commit and tag/branch named `v0`.
- Record the AI tool/model, prompt, generated files, and your own review/tests in the AI usage record.
- Define security user stories and verification tests before making v1 changes.
