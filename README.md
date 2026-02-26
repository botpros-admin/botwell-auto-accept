# Auto Accept for Antigravity

> ⚠️ **This extension is built exclusively for [Antigravity](https://antigravity.google) (a VS Code fork). It will NOT work correctly in standard VS Code.**

Auto-accept agent prompts in Antigravity. Toggle on/off from the status bar — no manual clicking required.

## Features

Automatically clicks these UI prompts when they appear:

- **Run** — Terminal command execution
- **Accept All** — File edit confirmations
- **Retry** — Error retry prompts
- **Allow This Conversation** — Conversation permission dialogs
- **Keep Waiting** — Timeout extension dialogs
- **Step Requires Input** — Expands collapsed sections that need attention

## How It Works

Uses Windows UI Automation (COM) to detect and invoke buttons programmatically. Focus lock prevents the extension from stealing your active window.

## Installation

> ⚠️ **You MUST use the `antigravity` CLI, NOT the `code` CLI.** Using `code --install-extension` will install to VS Code instead of Antigravity.

```bash
antigravity --install-extension botwell-auto-accept-1.1.0.vsix
```

To verify the install:

```bash
antigravity --list-extensions | findstr botwell
```

## Usage

1. Install the extension (see above)
2. Reload Antigravity (`Ctrl+Shift+P` → "Reload Window")
3. Click **"Auto-Accept OFF"** in the bottom-left status bar to enable
4. Click again to disable
5. View logs in Output panel → "Auto Accept"

## Requirements

- Windows 10/11
- Antigravity (VS Code fork) — **not standard VS Code**
- Python 3.x installed and on PATH
- `comtypes` Python package (`pip install comtypes`)

## Status Bar

| State | Display |
|-------|---------|
| Off | `$(circle-slash) Auto-Accept OFF` |
| On | `$(check) Auto-Accept ON` |

## Uninstall

```bash
antigravity --uninstall-extension botwell.botwell-auto-accept
```
