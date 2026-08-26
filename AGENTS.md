# Agent Entry Point

This repository is the governance and coordination control plane for the Game Planner AI Workspace. Its default and only business domain is Game Design; it is not a general-purpose AI platform or a business-code repository.

Before making changes:

1. Pull the latest `main` safely.
2. Read `AI_TEAM.md`, `ARCHITECTURE.md`, and `CONTRIBUTING.md`.
3. Read the relevant file under `handoff/`.
4. Read the affected RFC, ADR, project Status, and `CHANGELOG.md`.

Rules:

- Keep confirmed facts separate from hypotheses.
- Keep all models, Skills, Workflows, Templates, and projects within the Game Design domain.
- Do not copy business code, credentials, private datasets, or full runtime logs into this repository.
- Preserve project repositories as the source of truth for implementation.
- Update the relevant handoff and project Status when work changes shared state.
- Commit documentation and coordination records together, then push before handoff.
