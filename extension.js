const vscode = require("vscode");
const { spawn } = require("child_process");
const path = require("path");

let process = null;
let statusBarItem = null;
let outputChannel = null;

function activate(context) {
  outputChannel = vscode.window.createOutputChannel("Auto Accept");

  // Create status bar item (far left of status bar)
  statusBarItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Left,
    1000
  );
  statusBarItem.command = "botwell.autoAccept.toggle";
  updateStatusBar(false);
  statusBarItem.show();

  // Register toggle command
  const cmd = vscode.commands.registerCommand(
    "botwell.autoAccept.toggle",
    () => {
      if (process) {
        stop();
      } else {
        start();
      }
    }
  );

  context.subscriptions.push(cmd, statusBarItem, outputChannel);
}

function start() {
  const scriptPath = path.join(__dirname, "scripts", "auto_run.py");

  process = spawn("python", [scriptPath], {
    stdio: ["ignore", "pipe", "pipe"],
    windowsHide: true,
  });

  process.stdout.on("data", (data) => {
    outputChannel.appendLine(data.toString().trim());
  });

  process.stderr.on("data", (data) => {
    outputChannel.appendLine("[ERR] " + data.toString().trim());
  });

  process.on("close", (code) => {
    outputChannel.appendLine(`[Auto Accept stopped (code ${code})]`);
    process = null;
    updateStatusBar(false);
  });

  process.on("error", (err) => {
    vscode.window.showErrorMessage("Auto Accept failed: " + err.message);
    process = null;
    updateStatusBar(false);
  });

  updateStatusBar(true);
  outputChannel.appendLine("[Auto Accept started]");
}

function stop() {
  if (process) {
    process.kill();
    process = null;
  }
  updateStatusBar(false);
  outputChannel.appendLine("[Auto Accept stopped by user]");
}

function updateStatusBar(running) {
  if (running) {
    statusBarItem.text = "$(check) Auto-Accept ON";
    statusBarItem.tooltip = "Click to disable auto-accept";
    statusBarItem.backgroundColor = new vscode.ThemeColor(
      "statusBarItem.warningBackground"
    );
  } else {
    statusBarItem.text = "$(circle-slash) Auto-Accept OFF";
    statusBarItem.tooltip = "Click to enable auto-accept";
    statusBarItem.backgroundColor = undefined;
  }
}

function deactivate() {
  if (process) {
    process.kill();
    process = null;
  }
}

module.exports = { activate, deactivate };
