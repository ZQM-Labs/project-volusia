# WEB FORM DESIGN — PROJECT VOLUSIA CONTRIBUTION INTERFACE
# ==========================================================
# Version: 1.0
# Date: 2026-09-03
# Classification: Operational Design (addendum to
#                AGENTIC_CONTRIBUTION_STRATEGY.md)
#
# This document defines the citizen-facing web form interface for
# Project Volusia contributions. The web form is the primary human
# interface for Pathway F (Community Knowledge) and Pathway I (Direct
# Citizenry) contributions. It calls the Contribution API (Appendix J
# of AGENTIC_CONTRIBUTION_STRATEGY.md) behind the scenes.
#
# The web form is designed for:
# - Residents who want to share knowledge, observations, or concerns
# - Business owners who want to contribute ground-level intelligence
# - Visitors who want to share tourism-related observations
# - Anyone who prefers a visual form over SMS, email, or phone
#
# The web form is NOT designed for:
# - AI agents (they use the API directly via /submissions/agent-item)
# - Bulk submissions (use the API with an API key)
# - Complex multi-section submissions (use the API or email)
#
# Design principles:
# 1. Low friction — a resident should be able to submit in < 2 minutes
# 2. Accessible — works on mobile, tablet, and desktop; WCAG 2.1 AA
# 3. Multilingual — English and Spanish at launch (Volusia demographics)
# 4. Progressive disclosure — show simple fields first, expand for detail
# 5. Transparent — clear about what happens after submission
# 6. Trust-building — no login required for anonymous submissions;
#    clear privacy policy; no tracking beyond what's needed

---

## 1. WEB FORM ARCHITECTURE

### 1.1 Technology Stack

- **Frontend:** Static HTML/CSS/JS (no framework dependency — works on
  low-end devices, fast load, accessible)
- **Backend:** The Contribution API (Appendix J) — the web form is a
  thin client that calls the API
- **Hosting:** Served via the same infrastructure as the Project Volusia
  portal (cloudflared tunnel or Caddy reverse proxy on :250)
- **Analytics:** Privacy-respecting (no third-party trackers; server-side
  access logs only; no cookies for anonymous users)

### 1.2 URL Structure

```
https://contribute.project-volusia.org/          — landing page
https://contribute.project-volusia.org/f         — Pathway F form
https://contribute.project-volusia.org/i         — Pathway I form
https://contribute.project-volusia.org/status    — check submission status
https://contribute.project-volusia.org/es/       — Spanish landing
https://contribute.project-volusia.org/es/f      — Spanish Pathway F
https://contribute.project-volusia.org/es/i      — Spanish Pathway I
```

### 1.3 User Flow

```
Landing page
  → Choose pathway (F or I) — or "Not sure" defaults to I
  → Fill form (progressive disclosure)
  → Submit (calls API POST /submissions/F or /submissions/I)
  → Confirmation page (submission_id, estimated review date)
  → Optional: provide email for status updates
  → Optional: check status later via /status?submission_id=...
```

---

## 2. LANDING PAGE

### 2.1 Hero Section

```
+-------------------------------------------------------------+
|                                                             |
|   Share what you know about Volusia County                  |
|                                                             |
|   Your knowledge helps build a shared understanding         |
|   of our community. Contribute observations, insights,      |
|   and local knowledge that data alone can't capture.        |
|                                                             |
|   [Share community knowledge]  [Share a general thought]    |
|                                                             |
|   No account needed. Takes less than 2 minutes.             |
|                                                             |
+-------------------------------------------------------------+
```

### 2.2 Three-Column Value Proposition

```
+--------+--------+--------+
|  Easy  |  Safe  | Matters |
+--------+--------+--------+
| No     | Your   | Your    |
| account| info is| contri-|
| needed | protec-| bution  |
|        | ted    | reaches |
| 2 min  | No     | real   |
| or less| tracking| deci-|
|        |        | sions  |
+--------+--------+--------+
```

### 2.3 Trust Indicators

- "No account required for anonymous submissions"
- "Your contribution is reviewed by a human before publication"
- "You choose how you're credited (or stay anonymous)"
- "Privacy policy" link (plain language, < 1 page)

---

## 3. PATHWAY F FORM — Community Knowledge

### 3.1 Form Layout

```
+-------------------------------------------------------------+
|  Share what you know about Volusia                    [ES]  |
+-------------------------------------------------------------+
|                                                             |
|  What do you know? *                                        |
|  +---------------------------------------------------------+|
|  |                                                         ||
|  |  (e.g., "The seafood restaurant at 123 Main St closed  ||
|  |   in March 2026.")                                      ||
|  |                                                         ||
|  +---------------------------------------------------------+|
|  0 / 5000 characters                                        |
|                                                             |
|  Where is this about?                                       |
|  +---------------------------------------------------------+|
|  |  (e.g., "123 Main St, Daytona Beach")                   ||
|  +---------------------------------------------------------+|
|                                                             |
|  When?                                                      |
|  +---------------------------------------------------------+|
|  |  (e.g., "March 2026")                                   ||
|  +---------------------------------------------------------+|
|                                                             |
|  Why do you believe this is accurate? *                     |
|  +---------------------------------------------------------+|
|  |                                                         ||
|  |  (e.g., "I visited it regularly and saw it close.      ||
|  |   The owner told me directly.")                         ||
|  |                                                         ||
|  +---------------------------------------------------------+|
|  0 / 2000 characters                                        |
|                                                             |
|  What decision or report could this help?                   |
|  +---------------------------------------------------------+|
|  |  (e.g., "The Q3 2026 Quarterly Economic Briefing")     ||
|  +---------------------------------------------------------+|
|                                                             |
|  --- Show more options ---                                  |
|                                                             |
+-------------------------------------------------------------+
```

### 3.2 Expanded Fields (after "Show more options")

```
+-------------------------------------------------------------+
|                                                             |
|  How did you learn about Project Volusia?                   |
|  ( ) Web form  ( ) Email  ( ) SMS  ( ) Phone                |
|  ( ) Library  ( ) Community meeting  ( ) Social media       |
|  ( ) Other                                                  |
|                                                             |
|  How would you like to be credited?                         |
|  +---------------------------------------------------------+|
|  |  (e.g., "Daytona Beach resident")                       ||
|  +---------------------------------------------------------+|
|                                                             |
|  Can we follow up with you?                                 |
|  ( ) Yes, by email   ( ) Yes, by phone   ( ) No thanks     |
|                                                             |
|  Your email (optional):                                     |
|  +---------------------------------------------------------+|
|  |                                                         ||
|  +---------------------------------------------------------+|
|                                                             |
|  [Submit contribution]                                      |
|                                                             |
+-------------------------------------------------------------+
```

### 3.3 Form Behavior

- **Character counters** update in real-time (no surprises at submit)
- **Required fields** marked with `*` and validated on blur
- **Submit button** disabled until required fields are valid
- **Submit** calls `POST /api/v1/submissions/F` with the form data
- **On success (201):** redirect to confirmation page with submission_id
- **On rate limit (429):** show "We're receiving a high volume of
  contributions. Please try again in a few minutes." with Retry-After
- **On validation error (400):** show per-field errors inline (not a
  generic "something went wrong")
- **On server error (500):** show "Something went wrong on our end.
  Please try again or email community@project-volusia.org"
- **Network error:** detect offline state, show "You appear to be
  offline. Your contribution has been saved locally and will be
  submitted when you reconnect." (localStorage + background sync)

### 3.4 Confirmation Page

```
+-------------------------------------------------------------+
|                                                             |
|  Thank you for your contribution!                           |
|                                                             |
|  Your submission ID: sub_fgh789                             |
|                                                             |
|  What happens next:                                         |
|                                                             |
|  1. A Community Liaison will review your submission         |
|     within 5 business days.                                 |
|  2. If we need more information, we'll reach out via         |
|     the contact method you provided.                        |
|  3. If accepted, your contribution may be cited in          |
|     Project Volusia reports and dashboards.                 |
|                                                             |
|  [Submit another contribution]  [Return to home]            |
|                                                             |
+-------------------------------------------------------------+
```

---

## 4. PATHWAY I FORM — Direct Citizenry Contribution

### 4.1 Form Layout

The Pathway I form is the simplest possible — three fields plus contact.

```
+-------------------------------------------------------------+
|  Share a thought, idea, or concern about Volusia     [ES]  |
+-------------------------------------------------------------+
|                                                             |
|  Not sure where your contribution fits? That's OK —         |
|  share it here and we'll figure out where it belongs.       |
|                                                             |
|  What would you like to contribute? *                       |
|  +---------------------------------------------------------+|
|  |                                                         ||
|  |  (e.g., "I think the quarterly report should cover     ||
|  |   the impact of short-term rentals on long-term         ||
|  |   housing availability in Daytona Beach...")            ||
|  |                                                         ||
|  +---------------------------------------------------------+|
|  0 / 5000 characters                                        |
|                                                             |
|  What's your basis for this? *                              |
|  +---------------------------------------------------------+|
|  |                                                         ||
|  |  (e.g., "I live in the neighborhood. I know the        ||
|  |   families personally.")                                ||
|  |                                                         ||
|  +---------------------------------------------------------+|
|  0 / 2000 characters                                        |
|                                                             |
|  What decision or report could this help?                   |
|  +---------------------------------------------------------+|
|  |  (e.g., "Annual report? Housing section?")             ||
|  +---------------------------------------------------------+|
|                                                             |
|  Anything else?                                             |
|  +---------------------------------------------------------+|
|  |                                                         ||
|  +---------------------------------------------------------+|
|  0 / 2000 characters                                        |
|                                                             |
|  Can we follow up with you?                                 |
|  ( ) Yes, by email   ( ) Yes, by phone   ( ) No thanks     |
|                                                             |
|  Your email (optional):                                     |
|  +---------------------------------------------------------+|
|  |                                                         ||
|  +---------------------------------------------------------+|
|                                                             |
|  [Submit contribution]                                      |
|                                                             |
+-------------------------------------------------------------+
```

### 4.2 Form Behavior

Same as Pathway F (Section 3.3), but calls `POST /api/v1/submissions/I`.

---

## 5. STATUS CHECK PAGE

### 5.1 Layout

```
+-------------------------------------------------------------+
|  Check your submission status                        [ES]  |
+-------------------------------------------------------------+
|                                                             |
|  Enter your submission ID:                                  |
|  +---------------------------------------------------------+|
|  |  (e.g., sub_fgh789)                                     ||
|  +---------------------------------------------------------+|
|                                                             |
|  [Check status]                                             |
|                                                             |
+-------------------------------------------------------------+
```

### 5.2 Status Display

```
+-------------------------------------------------------------+
|                                                             |
|  Submission: sub_fgh789                                     |
|  Pathway: Community Knowledge (F)                           |
|  Submitted: September 3, 2026                               |
|  Status: Under review                                       |
|                                                             |
|  Timeline:                                                  |
|  ● Submitted — September 3, 2026                            |
|  ● Acknowledged — September 4, 2026                         |
|  ○ Estimated review by — September 8, 2026                  |
|                                                             |
|  [Back to home]                                             |
|                                                             |
+-------------------------------------------------------------+
```

Status states:
- **Queued** — received, waiting for Community Liaison acknowledgment
- **Under review** — being reviewed by a CGB member
- **Accepted** — accepted for inclusion in the knowledge base
- **Returned** — needs revision (with feedback)
- **Rejected** — not accepted (with rationale)
- **Resolved** — accepted and integrated into a report or dataset
- **Noted** — recorded but not directly used (still valuable)

---

## 6. ACCESSIBILITY REQUIREMENTS

### 6.1 WCAG 2.1 AA Compliance

- **Color contrast:** minimum 4.5:1 for text, 3:1 for large text
- **Keyboard navigation:** all form fields and buttons reachable via Tab
- **Screen reader support:** proper labels, ARIA attributes, live regions
  for character counters and validation errors
- **Focus indicators:** visible focus rings on all interactive elements
- **Form labels:** every input has a visible label (not just placeholder)
- **Error identification:** errors are announced to screen readers
- **Language:** `lang="en"` on the form, `lang="es"` on Spanish versions

### 6.2 Mobile-First Design

- Single column layout on mobile (< 768px)
- Touch targets minimum 44x44px
- Form fields use appropriate input types (email, tel, textarea)
- No hover-dependent interactions
- Test on: Chrome Android, Safari iOS, Samsung Internet

### 6.3 Performance

- First contentful paint < 1.5s on 3G
- Total page weight < 200KB (no heavy frameworks or images)
- Works offline (service worker caches the form; submissions queue
  locally and sync when online)

---

## 7. MULTILINGUAL SUPPORT

### 7.1 Launch Languages

1. **English** — primary
2. **Spanish** — Volusia County has a significant Hispanic population
   (~15% per ACS estimates)

### 7.2 Implementation

- All UI strings externalized (JSON translation files)
- Language toggle in the header (persists across pages)
- Form submissions include a `language` field (en/es)
- Reviewers see the original language + machine translation if needed
- Future languages: Haitian Creole (significant Volusia population),
  Portuguese (tourism industry)

### 7.3 Translation Quality

- UI strings: professional translation (not machine translation)
- Form help text: professional translation
- Contributor submissions: reviewed in original language; if the
  reviewer doesn't speak the language, machine translation is used
  for initial review, with human verification before publication

---

## 8. PRIVACY AND DATA HANDLING

### 8.1 Data Collected

- **Required:** the contribution content itself
- **Optional:** contact email/phone (only if contributor wants follow-up)
- **Automatic:** submission timestamp, IP address (for rate limiting
  and abuse prevention, not shared or published)

### 8.2 Data NOT Collected

- No third-party tracking cookies
- No browser fingerprinting
- No social media tracking
- No sale or sharing of contributor data

### 8.3 Data Retention

- Submissions: retained indefinitely (part of the knowledge base)
- Contact info: retained until the contributor requests deletion
- IP addresses: retained for 30 days for rate limiting, then purged
- Rejected submissions: retained for 90 days for pattern analysis,
  then purged (unless the contributor requests earlier deletion)

### 8.4 Contributor Rights

- **Right to anonymity:** submit without providing any contact info
- **Right to be forgotten:** request deletion of your submissions
  (contact community@project-volusia.org)
- **Right to correction:** request correction of factual errors in
  your published contributions
- **Right to know:** request information about how your contribution
  was used

### 8.5 Privacy Policy

A single-page, plain-language privacy policy linked from every page:
- What we collect and why
- How we use it
- How long we keep it
- Your rights
- How to contact us

---

## 9. ANTI-ABUSE MEASURES

### 9.1 Rate Limiting (Client-Side)

- Maximum 5 submissions per hour per browser (localStorage-based)
- Maximum 20 submissions per hour per IP (server-side, via API)
- Cooldown period after rate limit exceeded

### 9.2 Spam Prevention

- Honeypot field (hidden from humans, bots fill it out → rejected)
- No CAPTCHA for anonymous submissions (friction vs. accessibility
  trade-off; honeypot + rate limiting is sufficient for launch)
- Content moderation: submissions flagged by automated profanity/
  toxicity filters are queued for human review (not auto-rejected)

### 9.3 Content Moderation

- Submissions are NOT published automatically — all go through CGB
  review (the web form is a submission interface, not a publication
  interface)
- Automated pre-screening flags: profanity, personal information
  (phone numbers, addresses), links to external sites
- Flagged submissions are reviewed by the Community Liaison before
  normal CGB review

---

## 10. ANALYTICS AND METRICS

### 10.1 What We Track

- Page views (server-side access logs)
- Form starts vs. completions (to measure friction)
- Submission volume by pathway (F vs. I)
- Submission volume by language (en vs. es)
- API error rates (400, 429, 500)
- Average time to complete the form

### 10.2 What We DON'T Track

- Individual user journeys
- Cross-site tracking
- Third-party analytics (no Google Analytics, no Facebook Pixel)
- Personal identifiers beyond what's needed for the contribution

### 10.3 Reporting

- Monthly dashboard: submissions by pathway, language, status
- Quarterly report: contribution trends, acceptance rates, feedback
- Annual review: web form usability, accessibility audit, performance

---

## 11. IMPLEMENTATION PHASES

### 11.1 Phase 1 (Weeks 1-4): Static Form

- Static HTML/CSS/JS form
- Calls the Contribution API (which is also in development)
- English only
- Basic validation
- No offline support
- Hosted on the same infrastructure as the Project Volusia portal

### 11.2 Phase 2 (Weeks 5-8): Enhanced Form

- Spanish translation
- Offline support (service worker + localStorage queue)
- Progressive disclosure (show/hide optional fields)
- Status check page
- Accessibility audit and fixes

### 11.3 Phase 3 (Weeks 9-12): Polished Form

- Mobile-first refinements based on analytics
- Performance optimizations
- Anti-abuse measures (honeypot, rate limiting)
- Integration with the contributor record system
- Email notifications for status updates

### 11.4 Phase 4 (Weeks 13+): Ecosystem Integration

- School project submission portal (Pathway H) — a variant of the
  web form with additional fields for institution, sponsor, privacy
- Business owner toolkit contribution form
- Tourism operator contribution form
- API key self-service portal (for programmatic contributors)

---

## 12. DESIGN FILES

### 12.1 Wireframes

- `contribute/wireframes/landing.png`
- `contribute/wireforms/pathway-f.png`
- `contribute/wireframes/pathway-i.png`
- `contribute/wireframes/confirmation.png`
- `contribute/wireframes/status.png`
- `contribute/wireframes/mobile-landing.png`
- `contribute/wireframes/mobile-pathway-f.png`

### 12.2 HTML Templates

- `contribute/templates/landing.html`
- `contribute/templates/pathway-f.html`
- `contribute/templates/pathway-i.html`
- `contribute/templates/confirmation.html`
- `contribute/templates/status.html`
- `contribute/templates/privacy.html`

### 12.3 CSS

- `contribute/assets/css/main.css` — core styles
- `contribute/assets/css/form.css` — form-specific styles
- `contribute/assets/css/responsive.css` — mobile/tablet breakpoints

### 12.4 JavaScript

- `contribute/assets/js/form.js` — form validation, API calls, UI logic
- `contribute/assets/js/i18n.js` — language switching
- `contribute/assets/js/offline.js` — service worker registration,
  localStorage queue, background sync

### 12.5 Translation Files

- `contribute/i18n/en.json` — English UI strings
- `contribute/i18n/es.json` — Spanish UI strings

---

## 13. OPEN QUESTIONS

1. **CAPTCHA vs. honeypot:** If spam becomes a problem, should we add
   CAPTCHA (and which one — reCAPTCHA, hCaptcha, Turnstile)? Or stick
   with honeypot + rate limiting?

2. **Social login:** Should contributors be able to log in with Google,
   Facebook, or Apple? This reduces friction for some users but adds
   privacy concerns and third-party dependencies.

3. **File uploads:** Should the web form support file uploads (photos,
   documents)? This is useful for community knowledge (e.g., a photo
   of a closed business) but adds complexity and storage costs.

4. **Moderation queue visibility:** Should contributors see that their
   submission is "in the moderation queue" or just "under review"?
   Transparency vs. potential for gaming the system.

5. **Gamification:** Should we add any gamification elements (badges,
   contribution counts, leaderboards)? This could incentivize
   contributions but could also incentivize quantity over quality.

---

END OF DOCUMENT
