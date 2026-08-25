# Channel Security Deployment

This release secures and durably processes Gmail and WhatsApp inbound messages.

## Render environment

Configure these values on the backend web service before deploying:

```env
GMAIL_ENABLED=true
GMAIL_ADDRESS=custora.support@gmail.com
GMAIL_CREDENTIALS_JSON=<secret JSON>
GMAIL_TOKEN_JSON=<secret JSON>
EMAIL_POLL_SECRET=<random 32+ character secret>

WHATSAPP_ENABLED=true
TWILIO_ACCOUNT_SID=<secret>
TWILIO_AUTH_TOKEN=<secret>
TWILIO_WHATSAPP_NUMBER=<E.164 number>
TWILIO_WEBHOOK_URL=https://crm-customer-support-digital-fte.onrender.com/api/v1/channels/whatsapp/webhook
TWILIO_VALIDATE_SIGNATURES=true

CHANNEL_JOB_WORKER_ENABLED=true
```

The Gmail polling process must use the same `EMAIL_POLL_SECRET` and send it in
the `X-Email-Poll-Secret` request header. `scripts/poll_emails.py` now does this
automatically.

## Migration

`render.yaml` runs this command before the web service starts:

```bash
python run_channel_security_migration.py
```

It creates `channel_jobs`, a durable queue with a unique
`(channel, external_message_id)` key. Pending and stale jobs survive process
restarts and are claimed with PostgreSQL row locking.

For a manually configured Render service, set the same command as the service's
Pre-Deploy Command, or run it once as a Render job before deploying the new API.

## Twilio

Set Twilio's inbound message webhook to the exact value of
`TWILIO_WEBHOOK_URL`, including scheme, host, and path. Twilio signs that exact
URL, so a mismatch causes a `403 Invalid Twilio signature` response.

## Verification

After deployment:

```bash
curl https://crm-customer-support-digital-fte.onrender.com/health
curl https://crm-customer-support-digital-fte.onrender.com/api/v1/channels/status
```

Expected Render logs include `Durable channel job worker started`. A valid
Twilio request returns `queued`; a Twilio retry returns `duplicate`. Gmail poll
requests without the shared secret return `403`.

## Rollback

Set `CHANNEL_JOB_WORKER_ENABLED=false` to stop claiming new durable jobs. The
table is additive and can remain in place during rollback. Do not drop it while
pending jobs exist.

## Credential rotation

Rotate any credential that has appeared in a committed file. In particular,
rotate the Neon password and Better Auth secret, then update Render and Vercel.
Revoke and recreate Google or Twilio credentials if they were ever committed.
