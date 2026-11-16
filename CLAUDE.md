# CLAUDE.md — botwell-auto-accept

Operating guide for AI agents working in this repo. Read before making changes.

## What this is

A small, **public**, MIT-licensed VS Code extension that auto-accepts agent prompts in **Antigravity** (a VS Code fork) — Windows only. `extension.js` (VS Code Extension API) registers a status-bar toggle and spawns `scripts/auto_run.py`, a Python 3 worker that finds and invokes buttons through the Windows UI Automation tree (`comtypes` + COM). Default branch: `master`.

## Public repo — keep it public-safe

This repository is public. Do **not** add internal hostnames, IP addresses, infra identifiers (GCP project numbers/IDs, KMS key paths, service-account emails, WIF provider paths), tenant/tier details, or anything Bot Pros wouldn't want on the open internet. Keep docs and code generic.

## Build / test / deploy

- **Install deps (runtime):** `pip install comtypes`. Python 3.x must be on `PATH`.
- **Package:** `npx @vscode/vsce package` → produces `botwell-auto-accept-<version>.vsix`. No packaging script is committed; `package.json` has no `scripts` block.
- **Install into Antigravity:** `antigravity --install-extension botwell-auto-accept-<version>.vsix` (use the `antigravity` CLI, **never** `code`).
- **Uninstall:** `antigravity --uninstall-extension botwell.botwell-auto-accept`.
- **Test:** none automated. Verify manually — install, toggle on, trigger a prompt, watch the **Auto Accept** output channel. Run the worker standalone with `python scripts/auto_run.py`.
- **Release:** bump `version` in `package.json`, update `CHANGELOG.md`, re-package, commit the new `.vsix`.

## Conventions

- Create a feature branch for changes; open a PR into `master`. Do not force-push.
- Keep the two runtimes in sync: the extension's `main`, command id (`botwell.autoAccept.toggle`), and the spawn path (`scripts/auto_run.py`) must stay consistent with `package.json` and `extension.js`.
- Plain JS + a standalone Python script — no bundler, no framework. Don't introduce a build toolchain unless asked.

## Secret handling

This repo contains and requires **no secrets** — no keys, tokens, accounts, or network calls. There is nothing to configure.

- Never commit plaintext secrets, `.env` files, `*.pem`, or credentials of any kind.
- Never hardcode a key/token/password in source.
- Every new commit is scanned for accidentally committed secrets by the Bot Pros build farm (there are no GitHub Actions workflows).
- If you ever spot a plaintext secret already in the repo or its history, flag it to the maintainer — do not reproduce the value.

(For context: across the Bot Pros org, machine secrets are managed by a dedicated secrets manager, not committed to git. That machinery is irrelevant here because this tool uses none — don't paste org infra details into this public repo.)

## Gotchas / non-obvious facts

- **Antigravity-only.** The button names and accessibility tree it targets are Antigravity's; it will not behave correctly in standard VS Code. `activationEvents` is `["*"]`, so it activates on any window.
- **Windows-only.** The worker uses `ctypes.windll.user32` and `UIAutomationCore.dll` via COM. It cannot run on macOS/Linux.
- **Brittle by nature.** `auto_run.py` matches buttons by hardcoded UIA property IDs (e.g. control type `50000` = Button, `50020` = Text) and exact/partial names ("Accept all", "Run…Alt", "Keep Waiting", "Retry", "Allow This Conversation", "Requires Input", "Expand", "Scroll to bottom"). Antigravity UI/label changes can silently break matching — update the name/type conditions here when that happens.
- **Focus safety.** Each invoke is wrapped in `LockSetForegroundWindow(1/2)` so clicking does not steal foreground focus. Preserve this when editing `invoke_with_focus_lock`.
- **Process lifecycle.** The extension spawns/kills the Python worker; `deactivate()` and the toggle both kill it. If Python isn't on `PATH`, `spawn` errors surface via `showErrorMessage`.
- The uninstall/extension id is `botwell.botwell-auto-accept` (publisher `botwell` + name `botwell-auto-accept`).

## Do-nots

- ❌ Don't add internal infra details, secrets, or tenant/tier info to this public repo.
- ❌ Don't recommend `code --install-extension` — it installs into VS Code, not Antigravity.
- ❌ Don't add network calls, telemetry, or credential handling.
- ❌ Don't force-push or push directly to `master`.
- ✅ Only touch `README.md` / `CLAUDE.md` for docs work unless explicitly asked to change behavior.
