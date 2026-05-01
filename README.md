# Apex Runner

**Give AI a real workspace.**

Apex Runner is a private execution layer for AI agents. It gives an assistant controlled access to a workspace where it can inspect files, apply changes, run commands, test code, and return verified results.

This project is designed to run on your own VM first. The assistant should never receive unrestricted control over your full machine. Apex Runner only works inside the configured workspace directory.

## What Apex Runner can do in v0

- List files inside the workspace
- Read files inside the workspace
- Write files inside the workspace
- Apply git patches inside the workspace
- Run guarded shell commands inside the workspace
- Show git diff
- Run test/build commands

## Safety model

Apex Runner is intentionally restricted:

- No access outside `APEX_WORKSPACE_ROOT`
- No `sudo`
- No destructive system commands
- Command timeout
- Output size limits
- Optional bearer token for HTTP access
- Designed to run inside a disposable VM or sandbox

## Quick start on a VM

```bash
sudo apt update
sudo apt install -y git curl nodejs npm

git clone https://github.com/AlsayedHoota/Apex-Runner.git
cd Apex-Runner
npm install
cp .env.example .env
mkdir -p ~/apex-workspace
npm run dev
```

By default, Apex Runner starts an HTTP MCP server on:

```text
http://127.0.0.1:3030/mcp
```

For remote access, expose it securely using a tunnel such as Cloudflare Tunnel, ngrok, Tailscale, or a reverse proxy with HTTPS.

## Important

Do not expose Apex Runner publicly without authentication. Use a private VM, tunnel access control, and a strong `APEX_AUTH_TOKEN`.
