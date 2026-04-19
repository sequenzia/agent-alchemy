# Research Triggers

When to dispatch the `interview-researcher` agent during an adaptive interview. The goal is to fire research *only when it will make the next question better* — not to pad the interview with a survey of the topic.

## Trigger categories

### 1. Explicit request
The user directly asks for research. Always fire (no budget consumed — this is an on-demand call, not a proactive one).

Trigger phrases:
- "Can you research {X}?"
- "Look up {X}"
- "Find out what the options are for {X}"
- "What's the current state of {X}?"
- "Check the docs for {X}"
- "How do others handle {X}?"

### 2. User uncertainty
The user signals they don't know something that's material to the interview. Fire proactively if the unknown is blocking the next question — hold back if the conversation can proceed without it.

Trigger phrases:
- "I'm not sure"
- "I don't know what's out there"
- "What's standard for {X}?"
- "What would you recommend?"
- "I've been meaning to look into {X}"
- "Is {approach} still the way to go?"

**Rule:** Only fire if the uncertainty is about *external facts* (technology, regulation, competitor behavior). If the uncertainty is about *their own preference or situation*, don't research — ask them a clarifying question instead.

### 3. Compliance or regulatory mention
Regulations change, penalties are real, and guessing is expensive. Fire proactively when a compliance keyword appears and the user seems uncertain.

Keywords:
- **Data privacy**: GDPR, CCPA, PIPEDA, LGPD, POPIA
- **Health**: HIPAA, HITECH, 21 CFR Part 11
- **Finance**: PCI-DSS, SOC 2, SOX, KYC, AML
- **Accessibility**: WCAG, ADA, Section 508, EN 301 549
- **Education**: FERPA, COPPA
- **Security frameworks**: ISO 27001, NIST, FedRAMP
- **AI / data**: EU AI Act, Colorado AI Act, state-level data laws

**Rule:** If the user is clearly already expert in the regulation ("We're SOC 2 Type II audited and I know Section 1.3.2 well"), skip research — they don't need it. If they mention the regulation tentatively or ask what applies, fire.

### 4. Named technology, library, or product
The user refers to a specific named technology where the interviewer could meaningfully improve the next question by knowing what the product actually does.

Trigger examples:
- "We want to use {library} for this"
- "{Service} supposedly handles {X} — does it?"
- "Should we migrate to {framework}?"

**Rule:** Fire if the technology is specific and central. Skip for throwaway mentions ("we're on Postgres, which is fine") or if the question is about the user's constraints rather than the tool's capabilities.

### 5. Complex trade-off between named options
The user is weighing 2+ specific options and current information would change the decision.

Trigger examples:
- "Stripe vs. Paddle for global tax"
- "Should we self-host or use {hosted service}?"
- "REST vs. gRPC for our internal services"

**Rule:** Fire if the options are named and the user seems stuck. Skip if they've already committed and are just venting.

### 6. Domain the user admits they're new to
The user is stepping into an unfamiliar domain and doesn't know what questions to ask yet.

Trigger phrases:
- "I've never done {X} before"
- "This is new territory for me"
- "We're entering {domain} and I don't know the landscape"

**Rule:** Fire a single orientation call — "what are the key concepts in {domain}" — so the interviewer can ask informed follow-ups. Don't keep firing on every sub-question; one orientation is usually enough.

---

## Proactive-budget accounting

Every fire that was *not* explicitly requested by the user counts against the proactive budget (default 3, configurable via `interview-me.proactive-research-budget`).

Before firing a proactive call:
1. Track the current count: `{used}/{budget}`.
2. If `used < budget`, fire silently — don't ask permission, just note it in the round summary.
3. If `used >= budget`, use `AskUserQuestion` to offer: "I have some research I could dispatch on {topic}. Budget's used up — want to do it anyway?"

On-demand calls (the user explicitly asked) never count against the budget.

---

## When NOT to fire

- The user's question is about **their own team / company / product** — research can't answer that.
- The topic is **clearly solved** by a question to the user instead. ("Should you use X or Y?" is often "What are your constraints?" in disguise.)
- **Late in the interview** with the budget already spent. Don't hold up compilation for marginal info.
- The answer is **obvious and well-known** — don't research "what is React."
- The user has already **demonstrated expertise** in the topic — research adds noise, not signal.

---

## Worked examples

### Fire
> **User**: "We need to handle payment data but I don't really know the PCI requirements."
> **Fire**: Compliance + uncertainty. One research call on "PCI-DSS requirements for {user's architecture type}." Budget: `1/3`.

> **User**: "Research how Vercel and Netlify compare for our use case."
> **Fire**: Explicit request. On-demand call. Budget unchanged.

> **User**: "I'm thinking of using Temporal but I don't know if it's overkill for this."
> **Fire**: Named technology + uncertainty. Research: "Temporal's use cases, minimum operational overhead, and alternatives for simpler workflows."

### Don't fire
> **User**: "We're on AWS and that's not changing."
> **Don't fire**: No uncertainty, no open question. Ask a follow-up about *why* AWS is locked in instead.

> **User**: "I don't know how my team will feel about this."
> **Don't fire**: Uncertainty is about the user's own team. Ask a stakeholder question instead.

> **User**: "Should I optimize for X or Y?" *(late in the interview, budget used)*
> **Don't fire** proactively. Note the open question in the final report and recommend they research before deciding.

---

## Round-level rule of thumb

- **Round 1**: No research. Let the user set the frame first.
- **Rounds 2–3**: Prime time for proactive research when triggers hit.
- **Final round**: Hold back — you're closing, not opening. Save anything unresolved for the Open Questions section.
