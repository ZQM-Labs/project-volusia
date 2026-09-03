# SMS GATEWAY DESIGN — PROJECT VOLUSIA CONTRIBUTION INTERFACE
# ==============================================================
# Version: 1.0
# Date: 2026-09-03
# Classification: Operational Design (addendum to
#                AGENTIC_CONTRIBUTION_STRATEGY.md)
#
# This document defines the SMS (text message) interface for Project
# Volusia contributions. The SMS gateway is a citizen-facing interface
# that lets residents contribute via text message — the lowest-friction
# channel for citizens who may not have reliable internet access, who
# are on the go, or who prefer text to web forms.
#
# The SMS gateway is designed for:
# - Residents who want to share a quick observation or correction
# - Business owners who want to report a change (closed business,
#   new opening, event)
# - Visitors who want to share tourism-related feedback
# - Anyone who finds texting easier than filling out a web form
#
# The SMS gateway calls the Contribution API (Appendix J of
# AGENTIC_CONTRIBUTION_STRATEGY.md) behind the scenes.
#
# Design principles:
# 1. Ultra-low friction — contribute in 30 seconds with 1-2 texts
# 2. No smartphone required — works on any phone that can send SMS
# 3. No app to install — just send a text to a number
# 4. Guided conversation — the system asks questions, citizen answers
# 5. Transparent — clear about what happens next, same as web form
# 6. Same review process — SMS submissions go through the same CGB
#   review pipeline as web form and API submissions

---

## 1. SMS GATEWAY ARCHITECTURE

### 1.1 How It Works

```
Citizen sends SMS to Project Volusia short code (e.g., 541-VOLUSIA)
  → SMS gateway receives the message
  → Gateway identifies the conversation state (new, in-progress, follow-up)
  → Gateway sends a guided response (question or acknowledgment)
  → Citizen replies with the requested information
  → Gateway assembles the submission and calls the API
  → Gateway sends confirmation with submission ID
```

### 1.2 Technology Components

- **SMS Provider:** Twilio, Vonage (Nexmo), or Plivo — handles SMS
  sending/receiving, number provisioning, delivery receipts
- **Gateway Server:** A lightweight server (Python/Flask or Node.js)
  that manages conversation state, maps SMS flows to API calls, and
  handles edge cases
- **Conversation State Store:** Redis or SQLite — tracks where each
  phone number is in the submission flow
- **API Client:** The gateway calls the Contribution API (Appendix J)
  just like the web form does

### 1.3 Phone Number

- **Short code:** 541-VOLUSIA (541-865-8742) — easy to remember,
  Volusia-specific. Short codes have higher throughput and delivery
  rates than long codes.
- **Fallback long code:** If short code provisioning takes too long
  (US short codes take 8-12 weeks to provision), start with a long
  code (e.g., (386) 555-01VOL) and migrate to short code later.
- **Cost:** Short codes cost ~$500-1000/month. Long codes cost ~$1-10/month
  but have lower throughput.

### 1.4 Conversation Flow

The SMS gateway uses a state machine to guide citizens through a
contribution submission. Each phone number has a conversation state
that persists across messages.

```
STATE: IDLE
  → Citizen sends: "START" or any message
  → System: "Welcome to Project Volusia! Share what you know about
             our county. What would you like to contribute?
             Reply: KNOWLEDGE, IDEA, or STATUS"

STATE: CHOOSE_PATHWAY
  → Citizen sends: "KNOWLEDGE" (or "KNOW", "K", "1")
  → System: "What do you know? Share an observation, fact, or
             piece of local knowledge."
  → Transition to: COLLECT_WHAT_I_KNOW

  → Citizen sends: "IDEA" (or "IDEA", "I", "2")
  → System: "What's your idea or concern? Share your thought."
  → Transition to: COLLECT_WHAT_TO_CONTRIBUTE

  → Citizen sends: "STATUS" (or "S", "3")
  → System: "Enter your submission ID (e.g., sub_fgh789) to check status."
  → Transition to: COLLECT_STATUS_ID

STATE: COLLECT_WHAT_I_KNOW
  → Citizen sends: [free text, what they know]
  → System: "Where is this about? (e.g., '123 Main St, Daytona Beach')"
  → Store: what_i_know
  → Transition to: COLLECT_WHERE

STATE: COLLECT_WHERE
  → Citizen sends: [free text, location]
  → System: "Why do you believe this is accurate?"
  → Store: where
  → Transition to: COLLECT_WHY_BELIEVE

STATE: COLLECT_WHY_BELIEVE
  → Citizen sends: [free text, basis]
  → System: "Can we follow up? Reply: EMAIL [your email], PHONE [your number], or NO"
  → Store: why_believe_accurate
  → Transition to: COLLECT_CONTACT

STATE: COLLECT_WHAT_TO_CONTRIBUTE
  → Citizen sends: [free text, idea/concern]
  → System: "What's your basis for this? (Why do you think it's important?)"
  → Store: what_to_contribute
  → Transition to: COLLECT_BASIS

STATE: COLLECT_BASIS
  → Citizen sends: [free text, basis]
  → System: "Can we follow up? Reply: EMAIL [your email], PHONE [your number], or NO"
  → Store: basis
  → Transition to: COLLECT_CONTACT

STATE: COLLECT_CONTACT
  → Citizen sends: "EMAIL test@example.com" or "PHONE 3865551234" or "NO"
  → Store: contact info
  → System: "Thank you! Your contribution has been submitted. ID: sub_fgh789.
             A Community Liaison will review within 5 business days.
             Reply STATUS to check progress."
  → Submit via API: POST /submissions/F (or /submissions/I)
  → Transition to: IDLE

STATE: COLLECT_STATUS_ID
  → Citizen sends: [submission ID]
  → Look up submission via API: GET /submissions/{submission_id}
  → System: "Submission sub_fgh789: [status]. [Details if available]"
  → Transition to: IDLE

STATE: IDLE (any time)
  → Citizen sends: "STOP"
  → System: "You have unsubscribed from Project Volusia SMS. Reply START to resubscribe."
  → Transition to: OPTED_OUT

STATE: IDLE (any time)
  → Citizen sends: "HELP"
  → System: "Project Volusia SMS: Share what you know about our county.
             Reply START to contribute. Reply STATUS [ID] to check status.
             Reply STOP to unsubscribe. Msg&data rates may apply."
  → Transition to: IDLE
```

---

## 2. SMS SUBMISSION TYPES

### 2.1 Pathway F (Community Knowledge) via SMS

The guided conversation collects:
1. What do you know? (what_i_know)
2. Where? (where)
3. Why do you believe this is accurate? (why_believe_accurate)
4. Follow up? (contact info)

All four fields map directly to the Pathway F API schema.

### 2.2 Pathway I (Direct Citizenry) via SMS

The guided conversation collects:
1. What would you like to contribute? (what_to_contribute)
2. What's your basis? (basis)
3. Follow up? (contact info)

All three fields map directly to the Pathway I API schema.

### 2.3 Status Check via SMS

- Citizen sends: `STATUS sub_fgh789`
- Gateway calls: `GET /api/v1/submissions/sub_fgh789`
- Gateway returns: status, estimated review date, decision details if available

### 2.4 What SMS CANNOT Handle Well

- **Long narratives:** SMS has a 160-character limit per segment. While
  modern phones handle concatenation, long messages are cumbersome.
  For long contributions, the system responds: "That's a lot of detail!
  For longer contributions, please use the web form at
  contribute.project-volusia.org or email community@project-volusia.org."

- **File uploads:** SMS doesn't support file attachments in a useful way
  (MMS is unreliable and often blocked). For photo contributions: "To
  share a photo, please use the web form at contribute.project-volusia.org."

- **Complex structured data:** Pathways A-E (data sources, analysis,
  tools, map layers, report content) are not practical via SMS. The
  system directs these contributors to the web form or API.

---

## 3. SMS GATEWAY BEHAVIOR

### 3.1 Message Handling

- **Incoming messages:** Received via webhook from the SMS provider.
  The webhook payload includes the sender's phone number, message body,
  message timestamp, and message ID.
- **Message parsing:** The gateway strips whitespace, converts to
  lowercase for keyword matching, and preserves original case for
  free-text fields.
- **Response time:** The gateway responds within 5 seconds of receiving
  a message (the SMS provider holds the connection open for ~10 seconds).

### 3.2 Conversation State

- **State store:** Redis (preferred) or SQLite (fallback).
- **State key:** Phone number (E.164 format, e.g., +13865551234).
- **State value:** Current state, collected fields, message count,
  last message timestamp.
- **State TTL:** 24 hours. If a citizen doesn't respond within 24 hours,
  the conversation times out and the state is cleared. The next message
  starts a new conversation.

### 3.3 Error Handling

| Error condition | System response |
|----------------|-----------------|
| Unrecognized keyword | "Sorry, I didn't understand. Reply KNOWLEDGE, IDEA, STATUS, HELP, or STOP." |
| Message too long (> 1600 chars) | "That's a lot of detail! For longer contributions, please use contribute.project-volusia.org." |
| Invalid email format | "That doesn't look like an email. Please try again or reply NO to skip." |
| Invalid phone format | "That doesn't look like a phone number. Please try again or reply NO to skip." |
| Invalid submission ID | "I couldn't find that submission ID. Please check and try again (e.g., STATUS sub_fgh789)." |
| API unavailable (500) | "We're experiencing technical difficulties. Please try again in a few minutes or use contribute.project-volusia.org." |
| Rate limit exceeded (429) | "You've sent a lot of messages. Please wait a few minutes before trying again." |
| Conversation timeout | (No response — next message starts fresh) |

### 3.4 Keyword Recognition

Keywords are matched case-insensitively. The system accepts the first
word of the message as the keyword (for state transitions) and the rest
as content (for free-text fields).

| Keyword | Aliases | Action |
|---------|---------|--------|
| START | CONTRIBUTE, HELLO, HI | Begin contribution flow |
| KNOWLEDGE | KNOW, K, 1 | Choose Pathway F |
| IDEA | THOUGHT, CONCERN, I, 2 | Choose Pathway I |
| STATUS | S, 3 | Check submission status |
| HELP | H, INFO, ? | Show help text |
| STOP | UNSUBSCRIBE, QUIT, END | Opt out |
| NO | N, NOPE, SKIP | Skip optional field |

### 3.5 Opt-Out Handling

- **STOP:** Immediately opts the phone number out. The system sends a
  confirmation: "You have unsubscribed. Reply START to resubscribe."
- **Opt-out state:** Stored in the state store as `opted_out: true`.
  The system will not send any messages to opted-out numbers.
- **Resubscribing:** If an opted-out number sends any message, the
  system responds: "You are currently unsubscribed. Reply START to
  resubscribe." If they send START, they are resubscribed.

### 3.6 Rate Limiting (SMS-Specific)

- **Messages per minute per number:** max 5
- **Messages per hour per number:** max 20
- **Submissions per day per number:** max 10
- **Submissions per week per number:** max 50
- **Cooldown after rate limit:** 10 minutes

These limits are separate from the API rate limits — the SMS gateway
has its own limits because SMS is a higher-cost channel and more
susceptible to abuse.

---

## 4. SMS PROVIDER SELECTION

### 4.1 Provider Comparison

| Feature | Twilio | Vonage (Nexmo) | Plivo |
|---------|--------|----------------|-------|
| Short code provisioning | Yes (US/CA) | Yes (US/CA) | Yes (US) |
| Long code (A2P) | Yes | Yes | Yes |
| MMS support | Yes | Yes | Yes |
| Delivery receipts | Yes | Yes | Yes |
| Webhook support | Yes | Yes | Yes |
| Pay-as-you-go | Yes | Yes | Yes |
| US short code cost | ~$500-1000/mo | ~$500-1000/mo | ~$500-1000/mo |
| Long code cost | ~$1-10/mo | ~$1-10/mo | ~$1-10/mo |
| SMS send cost | ~$0.0075/msg | ~$0.0062/msg | ~$0.0050/msg |
| SMS receive cost | ~$0.0075/msg | ~$0.0062/msg | ~$0.0050/msg |
| Python SDK | Yes | Yes | Yes |
| Reputation | Industry standard | Established | Budget-friendly |

### 4.2 Recommendation

**Twilio** — industry standard, best documentation, most reliable
delivery, widely used in civic tech. The slight premium over Vonage
and Plivo is worth it for a public-facing system where delivery
reliability matters.

### 4.3 Fallback

If Twilio has an outage, the gateway should be able to fall back to
a secondary provider (Vonage). The gateway's provider abstraction
layer should make this transparent — the gateway sends to whichever
provider is available.

---

## 5. COST ESTIMATION

### 5.1 Assumptions

- 1000 citizens using SMS contributions per month
- Average 3 messages per submission (1 in, 2 out)
- Average 1 submission per citizen per month

### 5.2 Monthly Costs

| Item | Cost |
|------|------|
| Short code rental | ~$500-1000/month |
| SMS send (1000 × 2 = 2000 messages) | ~$15-20/month |
| SMS receive (1000 × 1 = 1000 messages) | ~$7-10/month |
| Gateway server (small VM) | ~$5-20/month |
| **Total** | **~$530-1050/month** |

### 5.3 Cost Reduction Options

- **Long code instead of short code:** Saves ~$500-1000/month but
  reduces throughput and memorability.
- **Volume discounts:** At higher volumes (10,000+ messages/month),
  per-message costs drop 20-40%.
- **Nonprofit discount:** Twilio offers nonprofit discounts
  (up to 50% off). If Project Volusia or ZQM Labs has nonprofit
  status, this could significantly reduce costs.

---

## 6. LEGAL AND COMPLIANCE

### 6.1 TCPA Compliance

The Telephone Consumer Protection Act (TCPA) regulates SMS messaging
in the US. Key requirements:

- **Prior consent:** Citizens must opt in before receiving messages.
  The first message from the system includes: "By replying, you
  agree to receive messages from Project Volusia. Msg&data rates
  may apply. Reply STOP to unsubscribe."
- **Opt-out mechanism:** STOP must work and must be honored
  immediately.
- **Quiet hours:** No messages between 9 PM and 8 AM local time
  (except for time-sensitive emergency notifications).
- **Identification:** Every message must identify Project Volusia.

### 6.2 CTIA Guidelines

The CTIA (wireless industry association) provides best practices:

- **Double opt-in for marketing:** Not required for transactional
  messages (which contributions are), but recommended.
- **Message frequency:** Don't overwhelm users. Max 1-2 messages
  per day unless the user is actively engaged in a conversation.
- **Help and opt-out:** Every message thread must include HELP and
  STOP instructions (or they must be easy to find).

### 6.3 Record Keeping

- **Opt-in records:** Store the timestamp and content of the opt-in
  message for each phone number.
- **Opt-out records:** Store the timestamp of each opt-out.
- **Message logs:** Store all inbound and outbound messages for
  90 days for dispute resolution, then purge.

### 6.4 Accessibility for SMS

- **Language:** English and Spanish (same as web form).
- **Plain language:** No jargon, no complex sentences.
- **TTY/TDD:** SMS is not accessible to TTY/TDD users. Provide an
  alternative channel (phone hotline or email) for these users.

---

## 7. INTEGRATION WITH CONTRIBUTION API

### 7.1 API Calls

The SMS gateway calls the same API endpoints as the web form:

| SMS action | API call |
|-----------|----------|
| Pathway F submission | POST /api/v1/submissions/F |
| Pathway I submission | POST /api/v1/submissions/I |
| Status check | GET /api/v1/submissions/{submission_id} |

### 7.2 Authentication

The gateway uses a dedicated API key with the `system_internal` tier
(the gateway is a trusted intermediary, not a citizen-facing API
consumer). The key is stored securely (environment variable or secret
manager, not in code).

### 7.3 Idempotency

- Each SMS submission includes an idempotency key derived from the
  phone number + timestamp of the first message in the conversation.
- If the gateway crashes mid-submission, the citizen can restart the
  conversation and the gateway will detect the duplicate and return
  the existing submission.

### 7.4 Webhook Security

- The SMS provider signs each webhook request with a signature.
- The gateway validates the signature before processing the message.
- Invalid signatures are logged and rejected.

---

## 8. MONITORING AND ALERTING

### 8.1 Metrics

| Metric | Target | Alert threshold |
|--------|--------|-----------------|
| SMS delivery rate | >= 95% | < 90% |
| SMS send latency | < 5s | > 10s |
| Gateway response time | < 3s | > 5s |
| Submission conversion rate | >= 50% | < 30% |
| Opt-out rate | < 5% | > 10% |
| Error rate | < 2% | > 5% |

### 8.2 Alerts

- **Delivery failure spike:** Alert the Agent Operations Lead if the
  delivery rate drops below 90% for 15 minutes.
- **Gateway down:** Alert the Agent Operations Lead if the gateway
  doesn't respond to health checks for 2 minutes.
- **Rate limit spike:** Alert the Community Liaison if any single
  phone number exceeds the rate limits (possible abuse).

### 8.3 Logging

- All inbound and outbound messages are logged (with phone numbers
  hashed for privacy).
- API calls are logged (request ID, endpoint, response status, latency).
- Errors are logged with full context for debugging.

---

## 9. IMPLEMENTATION PHASES

### 9.1 Phase 1 (Weeks 1-4): Basic SMS Gateway

- Provision a long code (faster than short code).
- Build the basic state machine (Pathway F only).
- Integrate with Twilio (or chosen provider).
- Integrate with the Contribution API.
- Manual testing with a small group of users.

### 9.2 Phase 2 (Weeks 5-8): Enhanced SMS Gateway

- Add Pathway I support.
- Add status check support.
- Add HELP and STOP handling.
- Add rate limiting and opt-out handling.
- Add Spanish support (bilingual keyword recognition).

### 9.3 Phase 3 (Weeks 9-12): Polished SMS Gateway

- Migrate to short code (if long code was used initially).
- Add conversation timeout handling.
- Add error handling edge cases.
- Load testing (simulate 1000 concurrent conversations).
- TCPA compliance audit.

### 9.4 Phase 4 (Weeks 13+): Ecosystem Integration

- Add follow-up message capability (Community Liaison can send a
  follow-up question to a citizen's submission).
- Add notification when submission status changes (opt-in).
- Add emergency notification capability (time-sensitive alerts
  from Project Volusia to opted-in citizens).

---

## 10. EDGE CASES AND MITIGATIONS

### 10.1 Edge Case: Citizen sends multiple messages before the system responds

**Mitigation:** The gateway processes messages sequentially (per phone
number). Messages received while the system is responding are queued
and processed in order. The state is updated after each message.

### 10.2 Edge Case: Citizen sends a message in a language other than English or Spanish

**Mitigation:** The gateway detects the language (using a lightweight
language detection library or the SMS provider's language hint). If the
language is not supported, the gateway responds: "Sorry, we currently
only support English and Spanish. Please use the web form at
contribute.project-volusia.org for other languages."

### 10.3 Edge Case: Citizen sends a message that looks like a submission but is actually a question

**Mitigation:** The gateway's keyword recognition is designed to handle
this. If the first word is not a recognized keyword, the gateway
responds: "Sorry, I didn't understand. Reply KNOWLEDGE, IDEA, STATUS,
HELP, or STOP." If the citizen is asking a question, they can use the
web form's "Contact us" link or email community@project-volusia.org.

### 10.4 Edge Case: Citizen's phone number changes during a conversation

**Mitigation:** The state is tied to the phone number. If the citizen
gets a new number, the old conversation is orphaned (and will time out
after 24 hours). The citizen starts fresh with the new number.

### 10.5 Edge Case: Citizen sends a message to the wrong number

**Mitigation:** The SMS provider provisions a dedicated number for
Project Volusia. Citizens who text the wrong number will reach a
different service, not Project Volusia.

### 10.6 Edge Case: Citizen's phone is stolen or number is spoofed

**Mitigation:** The gateway doesn't take irreversible actions based on
SMS alone. All submissions go through CGB review before publication.
If a citizen suspects fraud, they can contact the Community Liaison
to flag the submission for investigation.

### 10.7 Edge Case: System sends a message while the citizen is typing a response

**Mitigation:** This is a natural part of SMS conversation. The gateway
handles it by processing messages sequentially. If the citizen's
response is interrupted by a system message, the citizen can simply
re-send their response.

### 10.8 Edge Case: Citizen sends a message with only whitespace or emoji

**Mitigation:** The gateway strips whitespace and checks for empty
content. If the message is empty after stripping, the gateway
responds: "Sorry, I didn't receive a message. Please try again."

---

## 11. OPEN QUESTIONS

1. **RCS (Rich Communication Services):** Should we support RCS
   for richer interactions (images, carousels, suggested replies)?
   RCS is the successor to SMS and is supported on most Android
   phones. It would allow richer interactions without requiring a
   smartphone app.

2. **WhatsApp / Messenger integration:** Should we support
   WhatsApp or Facebook Messenger as additional messaging channels?
   This would require a different provider (Twilio supports WhatsApp)
   and different compliance considerations.

3. **Voice call integration:** Should we support voice calls
   (citizen calls a number, speaks their contribution, which is
   transcribed and submitted)? Twilio supports this, and it would
   be accessible to citizens who cannot text.

4. **Two-way follow-up:** Should the Community Liaison be able to
   send follow-up questions to citizens via SMS? This would be
   valuable for clarifying submissions but adds complexity.

5. **Group messaging:** Should we support group messaging (e.g.,
   a community meeting where multiple people contribute via SMS)?
   This would be complex but could be valuable for community events.

---

END OF DOCUMENT
