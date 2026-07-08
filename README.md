# botwell-auto-accept

Auto-accept agent prompts (Run, Accept All, Retry, Allow, Keep Waiting) in [Antigravity](https://antigravity.google), toggled from the status bar.

> ⚠️ Built **exclusively for Antigravity** (a VS Code fork). It will **not** work correctly in standard VS Code. Windows only.

## Overview

`botwell-auto-accept` is a small, MIT-licensed developer-productivity extension. When an Antigravity agent surfaces an interactive prompt, the extension detects the button through the OS accessibility layer and clicks it for you, so long-running agent sessions can proceed unattended. It is a single-toggle status-bar control — no configuration, no accounts, no network calls.

Automatically invoked prompts:

- **Run** — terminal command execution
- **Accept All** — file-edit confirmations
- **Retry** — error retry prompts
- **Allow This Conversation** — conversation permission dialogs
- **Keep Waiting** — timeout-extension dialogs
- **Step Requires Input** — expands collapsed sections that need attention (with a scroll-to-bottom fallback for off-screen buttons)

## Architecture / stack

Two cooperating pieces:

- **`extension.js`** — the VS Code extension entry point (Node / VS Code Extension API, engine `^1.70.0`). Registers a status-bar toggle and command (`botwell.autoAccept.toggle`). On enable it spawns the Python worker as a child process and streams its stdout/stderr to the **Auto Accept** output channel; on disable/deactivate it kills the process.
- **`scripts/auto_run.py`** — a Python 3 worker that polls the desktop UI Automation tree via `comtypes` (Windows `UIAutomationCore.dll`, COM). It finds the target buttons by control type + name and invokes them using the UIA `InvokePattern`. `LockSetForegroundWindow` is used around each invoke so clicking does **not** steal focus from your active window.

No bundler, no framework — plain JS plus a standalone Python script.

## Local setup

Prereqs:

- Windows 10/11
- [Antigravity](https://antigravity.google) (VS Code fork) — **not** standard VS Code
- Python 3.x installed and on `PATH`
- `comtypes` Python package: `pip install comtypes`

Install the packaged extension using the **`antigravity`** CLI (not `code`):

```bash
antigravity --install-extension botwell-auto-accept-1.1.0.vsix
```

Verify:

```bash
antigravity --list-extensions | findstr botwell
```

Run / use:

1. Reload Antigravity (`Ctrl+Shift+P` → "Reload Window").
2. Click **"Auto-Accept OFF"** in the bottom-left status bar to enable (it turns to **"Auto-Accept ON"** with a warning-colored background).
3. Click again to disable.
4. Watch logs in the Output panel → **Auto Accept**.

To run the worker directly for debugging (outside the extension): `python scripts/auto_run.py`.

## Build / test / deploy

- **Package:** built with the standard VS Code extension packager, e.g. `npx @vscode/vsce package`, which produces `botwell-auto-accept-<version>.vsix`. (No packaging script is committed; `package.json` defines no `scripts`.)
- **Test:** no automated test suite. Verify manually by installing in Antigravity, toggling on, triggering an agent prompt, and confirming the click in the **Auto Accept** output channel.
- **Deploy / distribute:** the committed `.vsix` is the release artifact; install it with the `antigravity` CLI as shown above. Not published to a marketplace.

Bump the version in `package.json`, update `CHANGELOG.md`, then re-package.

## Secrets & config

This project ships **no secrets and requires none** — no API keys, tokens, accounts, or network access. There is nothing to configure beyond having Python + `comtypes` on `PATH`.

Do not commit any credentials here. Every push runs an org secret-policy check (`.github/workflows/secret-policy.yml`) that scans for accidentally committed secrets.

## Repo structure

```
extension.js                     VS Code extension entry point (toggle + spawns worker)
scripts/auto_run.py              Python UI Automation worker (finds + invokes buttons)
package.json                     Extension manifest (name, publisher, command, engine)
botwell-auto-accept-1.1.0.vsix   Packaged release artifact
CHANGELOG.md                     Version history
LICENSE                          MIT
.github/workflows/secret-policy.yml   Org secret-scanning enforcement
```

## Status bar

| State | Display |
|-------|---------|
| Off | `$(circle-slash) Auto-Accept OFF` |
| On | `$(check) Auto-Accept ON` |

## Uninstall

```bash
antigravity --uninstall-extension botwell.botwell-auto-accept
```
