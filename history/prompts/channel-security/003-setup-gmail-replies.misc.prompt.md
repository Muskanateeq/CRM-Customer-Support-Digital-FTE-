---
id: 003
title: Setup Gmail Replies
stage: misc
date: 2026-08-25
surface: agent
model: gpt-5
feature: channel-security
branch: main
user: workspace-user
command: gmail setup guidance
labels: [gmail, oauth, render, email, polling]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - history/prompts/channel-security/003-setup-gmail-replies.misc.prompt.md
tests:
  - Inspected Gmail handler, polling endpoint, token generator, and Render configuration
  - Verified current Google Gmail OAuth and Render Cron requirements against official documentation
  - Confirmed backend .env and Python virtual environment exist without reading secret values
---

## Prompt

mujha gamil ka batao email kaisa setup karo taka mear application webform per reply karraha ha gmail per bhi kara gmail setup batao

## Response snapshot

Provided the project-specific Gmail setup sequence: enable Gmail API, configure Google Auth Platform and a Desktop OAuth client, generate the Gmail refresh token locally, place the credentials and token JSON in Render secrets, enable Gmail, and configure a recurring polling process that calls the protected email polling endpoint. Included exact local commands, Render variables, verification endpoints, and an end-to-end test procedure.

## Outcome

- Gmail requires OAuth credentials for the support mailbox and the `gmail.modify` scope.
- The deployed backend requires both OAuth JSON values and a strong shared polling secret.
- Incoming messages are polling-based, so a Render Cron Job or background worker must trigger email polling.
- Successful verification requires the email channel to report `ready`, a poll request to authenticate, and a real email to receive an automated threaded reply.

