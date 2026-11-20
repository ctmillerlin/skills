# Repository Conventions

## Directory Structure

```text
skills/
└── <skill-name>/
    ├── SKILL.md          # Required: YAML frontmatter (name, description) + instructions
    ├── references/       # Optional: supporting docs loaded on demand
    └── scripts/          # Optional: helper scripts
```

- Skill directory names use lowercase `kebab-case` and must match the `name` field in `SKILL.md`.
- Keep `README.md` in sync whenever a skill is added, renamed, or removed.

## Public Hygiene

This is a **public** repository. Before committing, verify that all files contain:

- No internal company names, domains, IPs, URLs, or project identifiers.
- No secrets, tokens, credentials, or local machine paths.

## Branch & PR Workflow

- `main` is the only long-lived branch; do not push directly to `main`.
- Make changes on a short-lived branch (for example, `feat/<skill-name>`, `fix/<skill-name>`, `chore/<topic>`) and open a pull request.
- Merge only after all CI checks (`Validate Spec`, `Security Scan`) pass.
- Use **Squash and merge**; the PR title must follow the Commit Messages format below because it becomes the commit message on `main`.

## Commit Messages

- **Format**: `type(scope): description` (Conventional Commits v1.0.0 core).
  - Types: `feat`, `fix`, `refactor`, `docs`, `ci`, `chore` (add `test` only if adopted).
  - Scope: skill directory name for skill changes (e.g., `feat(tech-diagram): ...`); omit for repository-wide changes.
- **Style**: English imperative mood (`add`, not `added`), lowercase first letter, no trailing period.
- **Atomicity**: one commit does one thing in one sentence.
- **Adoption boundary**: omit `!`, `BREAKING CHANGE` footers, and multi-paragraph bodies until a real need appears; when needed, adopt the spec as written without custom variants.
