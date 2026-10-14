# Guarded CI/CD — Fuggedaboutit Sense

This automation applies **only to BaconDisk22/FUGGEDABOUTIT-SENSE**. PRs run the Intel macOS CI. A separate `workflow_run` job may request GitHub auto-merge **only** for a successful, same-repository, non-draft PR into `master` bearing the `automerge-approved` label and not bearing `no-automerge`. GitHub branch protection and required reviews remain in force; the workflow never uses administrator bypass.

## One-time GitHub settings (required)

1. Repository **Settings → General → Pull Requests**: enable **Allow auto-merge** and **Allow squash merging**.
2. **Settings → Branches / Rulesets**: protect `master`; require the `mac-intel` check from **Fuggedaboutit Sense Intel Mac**, require PRs, and optionally require a review. Do not permit force pushes or bypasses.
3. **Settings → Actions → General**: allow workflow permissions necessary for the guarded workflow to request merges. Organization policy may override repository settings.
4. Add the `automerge-approved` label to PRs you have inspected and explicitly want automatically merged. Leave drafts unmerged; add `no-automerge` to prevent merges.

## Release procedure

Push a `v*` tag **pointing to a commit already on `master`**. CI builds an unsigned x64 Intel Mac DMG. Only after a successful matching build does the release workflow download its artifact and publish a **prerelease** with SHA256 checksum. A release is never published from an unverified PR or failed build.

Unsigned macOS apps can trigger Gatekeeper. Apple Developer ID signing/notarization requires credentials and is not configured here.

## Caveats

GitHub settings are not changed by committing workflows. The first workflow-run auto-merge execution will only be available once this automation reaches `master`. PRs cannot auto-merge unless GitHub allows auto-merge and the configured required checks pass. This is intentionally fail-closed.
