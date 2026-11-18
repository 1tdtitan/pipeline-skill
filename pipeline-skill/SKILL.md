---
name: pipeline-skill
description: Reviews a seller's open pipeline across CRM, email, calendar, call recordings, and chat, then produces one ordered checklist of paste-ready Next Step updates, CRM hygiene fixes, re-engagement email drafts for deals with no two-way contact in 14 days, and everything the user owes or needs to chase. Read-only by design, so it never writes to the CRM or sends a message. Use this whenever someone asks for a pipeline review, deal review, forecast or pipeline-call prep, Next Step updates, CRM cleanup, stale or quiet deals, "what do I owe people", "who do I need to chase", or "what should I work on today" in a sales or account management context, even if they don't name the skill. Also use it for first-time setup ("set up the pipeline skill") and for a demo run on the bundled sample data.
---

# Pipeline Skill

A seller's pipeline lives in several places at once. The CRM holds the official version, the inbox and call recordings hold what was really said, and chat holds the small promises nobody logged. This skill reads all of them and returns one ordered checklist: what to paste into the CRM so it matches reality, which quiet deals to re-engage and with what, and what the user owes or is waiting on.

The output is a reporting aid. It describes what is true about each deal and what was promised. It does not coach, strategize, or recommend how to win the deal.

## Three rules that shape everything

**1. Read-only.** Never create, update, send, post, or draft anything inside the CRM, email, calendar, chat, or call tools, even when a connector offers tools that could. The user reviews every suggestion and pastes it into its destination. This is what makes the skill safe to point at a live pipeline and a real inbox: the worst outcome of a mistake is a bad suggestion the user ignores. The only things this skill writes are its own report files and its config file.

**2. Every statement traces to a dated source.** A report like this is only useful if the user can trust it without re-reading every thread. One invented commitment or stretched date and they will have to check everything, which defeats the purpose. Before writing anything about a deal, read `references/evidence-rules.md` and follow it. The short version: no source, no statement; a "maybe" is never written as a commitment; no date appears unless someone stated it.

**3. Short and specific beats complete.** Sellers stop reading long reports. Every item is one action, written so it could only be about this deal, with the proof in one line underneath. The length caps in `references/report-format.md` are hard limits. If something has to be cut, cut the least urgent item, not the evidence.

## Pick the mode

- **Setup.** No saved config, or the user asks to set up or change settings. Read `references/setup.md` and run the wizard.
- **Demo.** The user asks for a demo, a sample run, or to try it without connecting anything. Read `references/demo.md`. The bundled fixture files stand in for the live tools.
- **Run.** A config exists and the user wants their pipeline reviewed. Follow the workflow below.

To find a saved config, look in this order: a `pipeline-config.md` file in the working folder or project files, then the tool's memory or project instructions, then a config block pasted into the conversation. If none exists, say so in one line and start setup.

## Run workflow

Work through these in order. Steps 3 to 6 each have a reference file with the detailed rules. Read each one when you reach that step, not before, so the rules are fresh when you apply them.

### 1. Preflight

For each source in the config, make one small read to confirm it responds and is signed in as the right person (for example, fetch one open opportunity, one recent email, one upcoming meeting).

If a configured source fails or is missing, stop and ask the user whether to retry, continue without it, or cancel. Say plainly what the report loses without that source (for example, "without the call recorder, last-contact dates rely on email and calendar only, so some deals may be flagged stale that are not"). Do not continue silently. A partial report that looks complete is worse than no report, because stale flags and "no reply found" claims are only as good as the sources behind them.

A source the config marks as not available is different: that was decided at setup. Run without it and list it under "Not checked" in the report header.

### 2. Pull the pipeline

Query the CRM for every open opportunity in the configured scope. For each one, capture all the fields you can read: name, account, stage, amount, close date, forecast category, the Next Step field and when it was last changed, contact roles (name, title, email, role), logged activities, and open tasks.

If the scope returns more than about 30 opportunities, tell the user the count and offer to run in batches by close date. Quality drops when too many deals share one pass.

### 3. Build an evidence log for each account

Group opportunities by account. For each account, collect within the config's `context_days` window (default 90 days, or since the opportunity was created if that is more recent):

- **Email:** every thread between the user and anyone at the account. Match on contact-role email addresses first, then on the account's email domain.
- **Calls and meetings:** dates, attendees, the recorder's summary and stated next steps, and transcripts. Read full transcripts for the two most recent calls per deal and summaries for older ones, unless an older call is where a commitment was made.
- **Calendar:** upcoming meetings with anyone at the account.
- **Chat:** messages to or from account contacts in shared channels, and internal messages that name the account.
- **CRM:** logged calls and meetings, tasks, and notes.

Write the log as a dated list: date, source, who said it, what was said, and whether it is firm or soft (see the evidence rules). Keep these logs as working notes and finish one account before starting the next, so details from one deal never bleed into another. If the environment supports parallel workers, one worker per account is a good split.

When a message could belong to more than one account (a shared domain, a parent company, a partner or agency on the thread), attribute it to the opportunity whose contacts are on it. If that still does not settle it, do not guess. List it under Notes in the report.

### 4. Review each opportunity

Read `references/pipeline-review.md`. For each opportunity, decide whether the Next Step field still matches the evidence, write a replacement if not, and check for a past-due close date, missing contact roles, and empty critical fields.

### 5. Check for stale deals

Read `references/stale-deals.md`. Find the last two-way contact for each opportunity. Any deal at or past the stale threshold (default 14 days) gets flagged with no exemptions, then matched against the resource library for a re-engagement email. If no resource is a strong fit, say so and do not draft an email.

### 6. Sweep for owes and chases

Read `references/owes-and-chases.md`. Sweep the whole inbox, sent mail, chat, and CRM tasks for the sweep window (default 14 days) for anything the user promised or was asked for and has not delivered, and anything the user asked for that has gone unanswered past the chase threshold (default 3 business days).

### 7. Assemble the report

Read `references/report-format.md`. Build the report as structured data first, then render it. If the environment can run Python, write the report JSON and run `scripts/build_report.py`. It computes day counts, sorts by urgency, enforces the length caps and the evidence rules, and writes the markdown and HTML files. Fix every error it reports instead of bypassing it. The checks exist because the two ways this skill has failed in practice are reports that ran long and facts that were stretched.

If the environment cannot run scripts, write the markdown report by hand using the layout in the same reference, apply the same caps yourself, and skip the HTML version.

### 8. Verify before delivering

Do the verification pass at the end of `references/evidence-rules.md`: for each item, go back to the cited source and confirm the date, the person, and the wording. Remove anything that does not hold up. This pass is where stretched facts get caught, so do not skip it when the run is long.

### 9. Deliver

Give the user the report files and a summary of no more than five lines in the conversation: how many accounts need action today, the single most time-sensitive item, how many deals are stale, and anything that could not be checked. Do not repeat the report in chat.

Afterwards the user may ask for more on any item: a longer email, the full evidence trail for a claim, a draft reply for something they owe. Those follow-ups are fine and the same three rules apply.

## Reference files

| File | Read it when |
| --- | --- |
| `references/setup.md` | Running first-time setup or changing settings |
| `references/demo.md` | Running on the bundled sample data |
| `references/evidence-rules.md` | Before writing anything about a deal, and again for the final verification pass |
| `references/pipeline-review.md` | Step 4: Next Step suggestions and CRM hygiene checks |
| `references/stale-deals.md` | Step 5: the stale check, resource matching, and the email draft |
| `references/owes-and-chases.md` | Step 6: the sweep |
| `references/report-format.md` | Step 7: urgency tiers, length caps, report data format, and layout |
| `assets/config-template.md` | Writing or reading the saved config |
| `scripts/build_report.py` | Validating and rendering the report |
