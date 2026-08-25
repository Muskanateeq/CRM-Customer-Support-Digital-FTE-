---
id: 004
title: Deploy Production Channels
stage: misc
date: 2026-08-25
surface: agent
model: gpt-5
feature: channel-security
branch: main
user: workspace-user
command: production channel deployment guidance
labels: [gmail, whatsapp, render, vercel, production, polling]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - history/prompts/channel-security/004-deploy-production-channels.misc.prompt.md
tests:
  - Inspected current Render Blueprint service definitions and production channel routes
  - Confirmed no Gmail cron or background worker is defined in render.yaml
  - Verified current Gmail offline OAuth, Twilio webhook, and Render worker requirements against official documentation
---

## Prompt

mera local per webform whatsapp gmail sar setup ha lakin jab mera apa project ka bacekdn render epr depkoy kiya or fronntend vercel to web form sa to repsons emilraha ha lkin whatsapp or gamil sa hai miilraha production is ka liyein mujha kiya kar ahoga kiya isko bhi laga sa deploy kara ha jo steps hem mujha batao kiya hein jisa mear gamil sa bhi production work kara

## Response snapshot

Explained the production topology and root cause: the existing Render Blueprint deploys only the API web service, while Gmail requires an additional continuously running polling worker or scheduled cron invocation. WhatsApp does not require another application deployment, but Twilio must be configured with the exact public Render webhook and production credentials. Provided exact Render environment variables, background-worker settings, OAuth token deployment steps, WhatsApp Sandbox/production sender requirements, and channel-specific verification checks.

## Outcome

- Web form continues to call the existing Render API from Vercel.
- Gmail uses the same API but needs a separately deployed polling process to discover inbound mail.
- WhatsApp uses the same API and needs Twilio to deliver inbound webhook requests to its public endpoint.
- Production acceptance requires both channels to report ready, their inbound triggers to reach Render, and replies to be delivered to the originating channel.

