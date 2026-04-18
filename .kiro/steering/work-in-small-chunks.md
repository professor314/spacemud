---
inclusion: auto
---

# Work in Small Chunks

When delegating work to subagents or writing large documents, break the work into small, completable pieces. Do not attempt to write or refactor an entire system in a single pass.

## Chunk Size Rules

- When writing or updating spec documents (requirements, design, tasks), handle one system or feature at a time. Do not write 7 systems in one subagent call.
- When generating implementation tasks, group them into batches of 3-5 related sub-tasks per subagent invocation.
- When executing code tasks, delegate at most 3-5 closely related sub-tasks per subagent call. Wait for completion before starting the next batch.
- When writing large files (batch_code.py, design docs), prefer appending sections incrementally over rewriting the entire file at once.
- If a subagent needs to produce more than ~200 lines of output, split the work into multiple calls.

## Plan Before Executing

- Before starting any multi-step work, present a short numbered plan to the user and wait for approval.
- The plan should list what will be done in what order, broken into the small chunks described above.
- Do not begin execution until the user confirms the plan.
- Example: "Here's the plan: 1) Write chassis design section, 2) Write professions design section, 3) Review both together. Want me to start?"

## Requirements Before Design

- When a new feature or system is being added, update the requirements document FIRST, then the design document.
- Do not write design details for something that has no matching requirement.
- If a design decision introduces something not in the requirements (e.g., a new command, a data format change, an infrastructure tool), add the requirement before writing the design.
- The flow is always: Requirements → Design → Tasks → Code.

## Ask Clarifying Questions First

- Before writing or rewriting any spec document, ask 1-3 clarifying questions if anything is ambiguous.
- Do not guess at design decisions. If the requirements leave room for interpretation, ask.
- Keep questions short and specific. One question at a time unless they're closely related.

## Track Progress as Tasks

- When a multi-step plan is approved, write it into tasks.md (or a scratch checklist) so progress is visible and resumable.
- Mark each chunk complete as it finishes, before starting the next.
- If the conversation is interrupted or context resets, the task list shows exactly where to resume.

## Avoid Redundant Work

- Before writing or modifying any file, read it first to check current state. Do not rewrite content that already exists and is correct.
- Before executing a task, check if it was already completed (look at the file, not just the task status).
- If a subagent fails or times out, check what it actually wrote before retrying. Partial work may be usable.
- Do not re-run passing tests unless code has changed since the last run.

## Verify Incrementally

- After each batch of 3-5 tasks, run relevant tests or syntax checks before moving to the next batch.
- Do not wait until the end to discover that an early change broke something.
- If a verification step fails, fix it before proceeding. Do not accumulate broken state.

## Why

Large single-pass operations hit output limits and fail silently. Redundant work burns credits. Smaller chunks complete reliably, are easier to verify, give the user visibility into progress, and are resumable if interrupted.

## Examples

### Bad — too much in one call
"Write the full Phase 2 design covering chassis, professions, skills, PVP, unit state, missions, and extended repair."

### Good — one system at a time
"Write the Phase 2 design section for Chassis and Professions."
Then: "Write the Phase 2 design section for the Skills System."
Then: "Write the Phase 2 design section for PVP and Unit State Management."

### Bad — executing without a plan
User says "implement Phase 2" → immediately start writing code.

### Good — plan first, then execute
User says "implement Phase 2" → present a plan → wait for approval → execute in chunks.

### Bad — rewriting a file without reading it
Rewrite all of objects.py to add one new class.

### Good — read then append
Read objects.py, confirm existing classes are correct, append the new class at the end.
