# Security Policy

GG Tank Watch is a **frozen historical archive** of a resolved May 2026 emergency. It is a static site with no backend, no database, no authentication, and no collection of user data, and it is not under active development.

## Reporting an issue

For a security or content-integrity issue (a broken link, a stale claim, a provenance problem), email **ggtankwatch@gmail.com** or open a GitHub issue. Because the project is archived, there is no guaranteed response time; fixes are best-effort only.

## Scope and posture

- No secrets or credentials are stored in this repository.
- The site is served read-only behind `X-Robots-Tag: noindex, nofollow` and a strict Content-Security-Policy (`default-src 'self'`); see [`vercel.json`](../public/vercel.json).
- The data pipeline is retired — `scripts/refresh_local.py` exits with an `ARCHIVED` notice and the dashboard no longer polls.
- `noindex` is kept permanently by choice, not a pending gate. Attorney review (originally the launch gate) was judged unnecessary once the incident resolved and the site froze. No wide launch is planned (see [`docs/DEPLOYMENT_READINESS.md`](../docs/DEPLOYMENT_READINESS.md)).
