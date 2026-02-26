# Auto Accept for Antigravity

Auto-accept agent prompts in Anti Gravity (VS Code fork). Toggle on/off from the status bar — no manual clicking required.

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

## Usage

1. Install the extension
2. Click **"Auto-Accept OFF"** in the bottom-left status bar to enable
3. Click again to disable
4. View logs in Output panel → "Auto Accept"

## Requirements

- Windows 10/11
- Python 3.x installed and on PATH
- `comtypes` Python package (`pip install comtypes`)

## Status Bar

| State | Display |
|-------|---------|
| Off | `$(circle-slash) Auto-Accept OFF` |
| On | `$(check) Auto-Accept ON` |
