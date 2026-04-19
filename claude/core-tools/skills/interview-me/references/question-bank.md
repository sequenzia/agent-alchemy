# Interview Question Bank

Seed questions for the adaptive interview loop. The interviewer picks from these as starting points, then branches based on user answers. **Do not read this file to the user verbatim** — use it as raw material for shaping AskUserQuestion calls.

## How to use this bank

- **Start with a short list per round** (3–5 questions). Never fire all questions from a category at once.
- **Skip what the user already answered** in the initial framing or previous rounds.
- **Pick questions that match the depth level** (see tags: `[overview]`, `[detailed]`, `[deep-dive]`; untagged = any depth).
- **Follow the user's energy.** If they volunteered something interesting under Goals, probe *that* next — don't mechanically march through categories.
- **Rephrase in the user's vocabulary.** If they said "our members" don't say "the end users" — match their framing so the conversation stays natural.

---

## Category 1 — Background & Current State

Establish where the user is starting from. Valuable early — answers here shape everything downstream.

- What does the current situation look like today, in concrete terms? [overview]
- What triggered you to start thinking about this now?
- What have you tried already, and what happened?
- Who else is aware of this right now? [detailed]
- Where does the existing process (or tooling, or decision) come from — is there history here? [detailed]
- Is there an existing artifact, document, or system involved? If so, what role does it play?
- How long has this been on your mind? [overview]
- What's the biggest thing people get wrong when they hear about this topic from you? [deep-dive]

### Leading-question warning
Avoid "So the current system isn't working, right?" — it assumes the diagnosis. Use "How would you describe the current system in your own words?" instead.

---

## Category 2 — Goals & Motivation

Draw out what "good" looks like. Users often start with a solution in mind; these questions surface the underlying goal.

- If this goes well, what changes for you in three months? [overview]
- What does success look like in the most concrete terms you can give me? [overview]
- Whose life gets better, and how?
- Are there multiple goals here? If so, which ranks highest? [detailed]
- What's the difference between "good enough" and "great" for this? [detailed]
- Why this goal instead of an adjacent one? What did you choose not to optimize for? [deep-dive]
- Is this instrumental (a means to a larger end) or terminal (the thing itself)? [deep-dive]
- If you had to name the one thing you'd refuse to compromise on, what would it be? [detailed]

### Leading-question warning
Don't list "the usual goals" (cost, speed, quality). Let the user name their own so you don't steer them to a generic answer.

---

## Category 3 — Constraints

Constraints are the shape of the solution space. They're often what the user cares most about but mentions last.

- What are the hard limits — budget, time, people, technology, policy? [overview]
- What's off the table for reasons you can't change?
- Are there regulatory or compliance requirements? (GDPR, HIPAA, PCI, WCAG, internal policy…) [detailed]
- Who has to approve this, and what do they care about? [detailed]
- What existing commitments or decisions lock you in? [detailed]
- Are there cultural or political constraints that don't show up on paper? [deep-dive]
- How firm are these constraints — is any of them actually negotiable if the stakes are high enough? [deep-dive]
- Is there a constraint you *hope* to lift later but can't right now?

---

## Category 4 — Success Criteria

Push beyond "it works" into "we'd know it worked because…". Measurable conditions sharpen later recommendations.

- How will you measure whether this succeeded? [overview]
- What specifically would you see or hear that would convince you it's working? [detailed]
- Are there quantitative targets — response time, conversion rate, user count, revenue? [detailed]
- Qualitative signals — what would users say, how would stakeholders feel? [detailed]
- Is there a counter-metric you'd watch to make sure you're not making things worse elsewhere? [deep-dive]
- What's the timeline for judging success — days, weeks, a quarter, a year? [detailed]
- Who gets to call it "done"? [detailed]

### Leading-question warning
Don't propose a metric and ask the user to confirm ("Would 20% faster response time count as success?"). Ask open-ended and let them name their own.

---

## Category 5 — Risks & Unknowns

What could make this fail? Users often know the answer but haven't been asked directly.

- What's the single biggest thing that could make this fail? [overview]
- What keeps you up at night about this? [overview]
- Where are the unknowns — things you'd need to investigate before committing? [detailed]
- Have you seen similar efforts fail before? What went wrong? [detailed]
- Is there a dependency — a person, system, decision — that you don't fully control? [detailed]
- What's the "unknown unknown" you suspect exists but can't name? [deep-dive]
- If this fails halfway, what's the cost of the partial state? [deep-dive]
- Is the riskiest part at the start, the middle, or the end of the effort? [deep-dive]

---

## Category 6 — Stakeholders

Who else matters? Interviews that skip stakeholders produce plans that get rejected later.

- Besides you, who's affected by this — directly or indirectly? [overview]
- Who benefits most? Who loses something?
- Who has veto power over this, even informally? [detailed]
- Who's championing it besides you, if anyone? [detailed]
- Are there users (or customers, or audiences) whose voice isn't in the room? [detailed]
- What does each group need to see before they'll support it? [deep-dive]
- Is there tension between stakeholder groups that needs resolving before you proceed? [deep-dive]

---

## Category 7 — Timeline & Cadence

When things happen matters as much as what happens.

- Is there a hard deadline — external, contractual, seasonal? [overview]
- What's your ideal timeline, separately from any hard deadline? [detailed]
- Can this be phased, or does it need to land as one piece? [detailed]
- What's the cost of delay? [detailed]
- Are there windows when this *cannot* happen — launches, freezes, holidays? [detailed]
- What's the minimum you'd ship first, to test or de-risk? [deep-dive]

---

## Category 8 — Discovery Follow-ups

Generic follow-ups to deepen a thread the user opened. Use these when you want to go deeper on something the user just said rather than pivoting to a new category.

- Can you give me a specific example of what you mean?
- When was the last time this came up in practice?
- How does this look different from a week / a month / a year ago?
- What have you already ruled out, and why?
- If you had to pick between {option A the user named} and {option B the user named}, which would you pick and why?
- What's the version of this that would make you uncomfortable — too ambitious, too expensive, too ugly?
- What does the "boring, obvious" answer look like, and why haven't you already taken it?
- Who's the person you'd most want to talk to about this if you could?

---

## Depth-level guidance

| Depth | Coverage strategy |
|---|---|
| **Overview** (2–3 rounds, 6–10 Q total) | Stay in Categories 1, 2, and 4 primarily. Hit Category 3 (constraints) only if the user mentions one. Skip Category 8's deepening questions. |
| **Detailed** (3–4 rounds, 12–18 Q total) | Cover all 7 primary categories with at least one question each. Use Category 8 to go deeper on whichever thread the user is most engaged with. |
| **Deep-dive** (4–5 rounds, 18–25 Q total) | Hit every category. Spend at least one full round on Category 5 (Risks) and Category 6 (Stakeholders). Use the `[deep-dive]`-tagged questions liberally. |

---

## Question-shape reminders

- **Open-ended > closed.** "What would make this fail?" beats "Could X make this fail?"
- **Specific > abstract.** "Walk me through yesterday" beats "Describe your workflow."
- **One question at a time.** Compound questions ("and also…") cause users to answer only the first half.
- **No solution-language in the question.** Asking "Should we use React or Vue?" presumes a web-app solution — ask about the user's problem first.
- **Reflect before pivoting.** "I hear you saying X — is that right?" costs little and catches a lot of misunderstandings.
