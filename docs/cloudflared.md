# Cloudflare Tunnel setup for Apex Mentor

Cloudflared is the recommended first tunnel option if you already have a Cloudflare account.

## Local or Deepnote flow

Start Apex Mentor first:

```bash
bash scripts/start.sh
```

In a second terminal, install and run cloudflared.

## Temporary tunnel, fastest test

This gives you a random HTTPS URL. Good for quick testing.

```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

If you are running in Deepnote and the app is bound to `0.0.0.0:8000`, this still forwards the local port correctly.

Cloudflared will print a URL like:

```text
https://something.trycloudflare.com
```

Use this as your public base URL.

## Private API requirement

Apex Mentor private endpoints require:

```text
Authorization: Bearer YOUR_APEX_AUTH_TOKEN
```

Set the token in `.env`:

```env
APEX_AUTH_TOKEN=replace-with-a-long-random-secret
```

## Test through the tunnel

```bash
export APEX_BASE_URL=https://your-tunnel-url.trycloudflare.com
export APEX_AUTH_TOKEN=replace-with-a-long-random-secret
bash scripts/check.sh
```

## Recommended later: named tunnel

A named tunnel is better than a temporary tunnel because it gives a stable URL.

```bash
cloudflared tunnel login
cloudflared tunnel create apex-mentor
cloudflared tunnel route dns apex-mentor apex-mentor.yourdomain.com
cloudflared tunnel run apex-mentor
```

You will also need a Cloudflare tunnel config file that maps the hostname to the local service:

```yaml
tunnel: apex-mentor
credentials-file: /home/USER/.cloudflared/TUNNEL_ID.json

ingress:
  - hostname: apex-mentor.yourdomain.com
    service: http://127.0.0.1:8000
  - service: http_status:404
```

## Security checklist

- Keep the GitHub repo private.
- Use a long `APEX_AUTH_TOKEN`.
- Do not share the tunnel URL publicly.
- Prefer Cloudflare Access for stronger protection later.
- Do not expose the API without auth.
