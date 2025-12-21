Philosophy

We learn by doing, document the struggle, and turn it into doctrine—then we automate it.

- Visible learning — DevOnboarder turns trials into AARs.
- Doctrine — core-instructions captures lessons as guardrails.
- Automation — SquirrelFocus feeds repeatable tooling.

---

# Foundational Knowledge Enhancement

A repeatable method for building durable understanding (not test-cramming). Works with or without AI.

---

## Principles

- **Outcomes over identity:** The goal is correct, repeatable results.
- **Behavior beats memorization:** If you can't *predict and reproduce* behavior, you don't own it yet.
- **Assumptions are liabilities:** Name them, test them, kill the wrong ones.
- **One variable at a time:** Change control prevents self-inflicted confusion.
- **Artifacts are the end product:** Notes, checklists, labs, and tests outlive motivation.

---

## The BUILD Method

**B**aseline → **U**nderstand → **I**mplement → **L**oad-test → **D**ocument

### 1) Baseline

Define the target and constraints.

- **Goal:** What do I need to be able to do?
- **Done means:** What observable result proves success?
- **Constraints:** Time, tools, environment, versions, permissions, inputs.
- **Known/unknown:** What do I already know? What is unclear?

**Output:** A one-sentence problem statement + "done" criteria.

---

### 2) Understand

Build a mental model before you collect facts.

- **Explain (1 paragraph):** What is it, why does it exist, where is it used?
- **System model:** Inputs → Process → Outputs
- **Failure modes (3):** How does it break? How would I detect each break?
- **Assumptions:** List them explicitly (versions, OS, runtime, data shape).

**Output:** A simple model + failure-mode list.

---

### 3) Implement

Prove the model with a minimal, runnable example.

- **Minimal reproduction:** Smallest example that demonstrates the concept.
- **Instrument:** Print/log inputs and outputs.
- **Convert to function/module:** Only after behavior is proven.

**Output:** A tiny working lab/script.

---

### 4) Load-test

Make it durable by attacking it.

- **Edge cases (2–5):** Null/empty, invalid types, boundary values, timeouts, permissions.
- **Alternative explanations (top 3):** What else could cause the same symptoms?
- **Disconfirming evidence:** What would change my mind?
- **Repeatability:** Can I run it again and get the same result?

**Output:** A short list of tests + observed outcomes.

---

### 5) Document

Turn learning into an artifact anyone can reuse.

- **Checklist:** Steps + expected outputs.
- **Verification:** Primary source references (official docs/spec/code/logs).
- **Teach-back:** 5 bullets: problem / root cause / fix / prevention / reference.
- **Storage:** Put it where Future You will actually find it.

**Output:** A reusable guide + proof.

---

## One-Page Learning Template (Copy/Paste)

**Topic:**

**Why I care (use-case):**

**Goal (what I need to do):**

**Done means (observable):**

**Constraints (versions/OS/tools):**

**1-paragraph explanation:**

**Inputs → Process → Outputs:**

**Assumptions:**

**Failure modes (3) + detection:**

**Minimal example / lab:**

**What I changed + what happened:**

**Edge cases tested + results:**

**Verification source(s):**

**Teach-back (5 bullets):**

**Quiz (10):**

- 5 recall
- 3 applied scenarios
- 2 edge/trick cases

---

## AI Use Policy (Optional, Recommended)

Use AI for **structure and challenge**, not authority.

### Allowed

- Turn raw material into **lessons**, **quizzes**, **checklists**, and **labs**
- Generate **edge cases**, **failure modes**, and **test plans**
- Explain concepts at different levels of depth

### Not Allowed (without verification)

- Commands/flags/configs used in production
- Security-sensitive guidance
- Anything where being wrong causes real damage

### "Anti-bullshit" Questions

- What assumptions are you making?
- What evidence supports this?
- What would change your mind?
- Give 3 alternative causes.
- Provide a minimal reproduction + pass/fail test.
- Cite primary sources or explain how to verify.

---

## Quick Daily Loop (15–30 minutes)

1. Pick one topic (small).
2. Write the 1-paragraph explanation from memory.
3. Run the minimal lab.
4. Add one edge case.
5. Update the checklist/notes.

**Result:** Knowledge compounds without cramming.

---

## Troubleshooting Overlay (When something breaks)

1. Capture the exact error and context (versions, environment).
2. Reproduce reliably.
3. Reduce to minimal reproduction.
4. Check docs + known issues.
5. Test top 3 hypotheses (one change at a time).
6. Fix, then prevent with a checklist/test.

---

## Notes

- If you can **predict the output before running**, you understand.
- If you can **teach it in 60 seconds**, you own it.
- If you can **write a checklist**, you can transfer it.

---

# 7-Day BUILD Challenge

A lightweight, execution-first challenge to turn the BUILD method into a habit.

**Time per day:** 15–30 minutes (45 minutes max if you go deep)

**Goal:** Build durable understanding through explanation, behavior, and proof—NOT memorization.

---

## Rules

1. **Small topics only.** If it takes more than 30 minutes to run a minimal example, the topic is too big.
2. **One artifact per day.** Use the One-Page Learning Template (or the "Minimum Post" format below).
3. **Behavior required.** No "I read about it." You must run a minimal example or reproduce a behavior.
4. **One variable at a time.** If you change multiple things, you learn nothing.
5. **Show proof.** Output, screenshots, logs, or test results.

---

## Daily Deliverable

### Minimum Post (3 items)

1. **1-paragraph explanation** (in your own words)
2. **Minimal lab/repro** (snippet, commands, or steps)
3. **One edge case** + outcome

Optional (recommended): link to the primary source you verified against.

---

## Day-by-Day Plan

### Day 1 — Baseline + Model

Pick a topic and build a clean mental model.

- Define goal + "done means"
- Inputs → Process → Outputs
- 3 failure modes + detection

**Deliverable:** Explanation + system model + failure modes.

---

### Day 2 — Minimal Reproduction

Prove the concept with the smallest runnable example.

- Run it
- Log input/output

**Deliverable:** Minimal lab + expected output.

---

### Day 3 — Edge Case #1

Break it on purpose.

- Pick one edge case (empty/null/invalid/boundary)
- Observe what happens

**Deliverable:** Edge case + result + what it taught you.

---

### Day 4 — Alternative Hypotheses

Force deeper understanding.

- List 3 plausible alternative explanations for the same behavior
- Run 1 test that rules one out

**Deliverable:** 3 alternatives + one disconfirming test.

---

### Day 5 — Teach-Back

Make it transferable.

Write 5 bullets:

- problem
- root cause
- fix
- prevention
- verification source

**Deliverable:** Teach-back bullets.

---

### Day 6 — Checklist + Repeatability

Turn it into a reusable procedure.

- Checklist with steps + expected outputs
- Re-run from scratch (or simulate "fresh machine")

**Deliverable:** Checklist + confirmation it repeats.

---

### Day 7 — Mini Assessment

Prove you own it.

- Create 10 questions:

  - 5 recall
  - 3 applied scenarios
  - 2 edge/trick
- Answer them without notes
- Verify anything uncertain

**Deliverable:** Quiz + score + corrections.

---

## Suggested Topic List (Pick One Per Day)

- What does `===` do in JavaScript vs `==`?
- What is an environment variable and how does it influence a process?
- What is a Promise, and what does `await` actually wait on?
- How do ports and sockets relate? (simple TCP client/server)
- What's the difference between relative and absolute paths?
- What does "idempotent" mean? Give one real example.
- What's a database transaction? What breaks without one?

---

## Success Criteria

By the end of 7 days, you should have:

- 7 one-page artifacts
- 7 runnable mini-labs
- 7 checklists
- a habit: explain → run → break → verify → document

---

# BUILD + AAR Integration (When It Breaks in the Real World)

BUILD gets you to **first correct understanding**. AAR keeps it correct after reality punches it.

Use this when a concept, checklist, or lab fails in production or in a real project.

---

## AAR Loop

- **Expected:** What did we think would happen?
- **Actual:** What happened (logs, outputs, timestamps, environment)?
- **Delta:** What changed / what assumption was wrong?
- **Root cause:** The simplest causal explanation supported by evidence.
- **Fix:** Minimal fix + robust fix.
- **Prevention:** Add a test, guardrail, or checklist step so this fails loudly next time.
- **Update artifact:** Patch the checklist/lab/template so Future You doesn't relearn this the hard way.

**Rule:** If it broke once, it earns a new edge case test and a prevention note.

---

## The Full Cycle

1. **BUILD** → Create the first correct artifact (explanation + lab + checklist)
2. **Use it** → Apply it to real work
3. **When it breaks** → Run AAR to find what changed
4. **Update artifact** → Add the edge case, update the checklist
5. **Repeat** → Knowledge compounds, failures become advantages

This prevents knowledge decay and turns every failure into a stronger artifact.
