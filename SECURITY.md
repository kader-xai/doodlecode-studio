# Security Policy

## Supported versions

DoodleCode Studio is pre-1.0; only the `main` branch is supported. Please
upgrade to the latest commit before reporting.

## Reporting a vulnerability

Please **do not open a public issue** for security reports. Instead, email
the maintainer via the contact link on <https://kader-xai.github.io>, or open
a [GitHub security advisory](https://github.com/kader-xai/doodlecode-studio/security/advisories/new).

Include:

- A description of the issue and its impact
- Steps to reproduce (a minimal `.py` upload that triggers it is ideal)
- Affected version / commit
- Any suggested mitigation

You can expect an acknowledgement within 72 hours and a fix or mitigation
plan within 14 days for confirmed reports.

## Threat model

DoodleCode Studio is designed for **local, single-user** use. The backend:

- Executes arbitrary Python supplied by the user inside a persistent
  IPython kernel — full system access. **Do not expose it to the internet.**
- Persists notebooks under `~/.doodlecode/` with the user's filesystem
  permissions.
- Uses an open CORS policy (`*`) suited to localhost development.

If you want to host DoodleCode Studio for multiple users, you must:

- Sandbox the kernel (containers, gVisor, Firejail, or a kernel pool with
  per-user OS users).
- Restrict CORS in `backend/app/main.py`.
- Front the API with authentication and TLS.
- Disable or rate-limit `/execute`, `/upload`, and `/autosave`.

Patches to harden these defaults behind a configuration flag are welcome.
