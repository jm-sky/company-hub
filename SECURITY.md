# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in CompanyHub, please report it privately rather
than opening a public issue.

- Email: jan.madeyski@gmail.com
- Please include a description of the vulnerability, steps to reproduce, and its potential
  impact.

We aim to acknowledge reports within 5 business days. Once a fix is available, we'll
coordinate disclosure timing with you.

## Supported Versions

This project tracks `main` as the only supported branch. Security fixes are applied there
and released promptly; there are no maintained older release branches.

## Dependency Vulnerabilities

Dependency updates are tracked via Dependabot (`.github/dependabot.yml`) and audited on
every pull request that touches dependency manifests (`.github/workflows/dependency-audit.yml`,
running `pip-audit` and `pnpm audit`).
