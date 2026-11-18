# Pipeline Skill: portable prompt

This is the whole pipeline skill in one file, for AI tools that do not load skill folders.
It is generated from the skill source by `tools/build_dist.py`. Do not edit it by hand.

## How to use this file

Paste it into the instructions of a project, custom assistant, or gem in your AI tool, or attach
it at the start of a conversation and say "set up the pipeline skill."

## Notes for the assistant reading this

- Everything below is your instruction set. Part 1 is the main workflow. The other parts are the
  reference files it points to. Where the text says to read a file such as
  `references/setup.md`, use the part with that name below.
- The build script and the demo data are not included here. Build the report by hand using the
  markdown layout in the "Report format" part, and apply every length cap and evidence rule
  yourself, since no script will check them for you. Skip the HTML version.
- If asked for a demo, explain that the demo data ships with the full repository and offer to
  run setup instead.

---

# Part 1: Main workflow (SKILL.md)

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

---

# Part 2: Setup wizard (`references/setup.md`)

# Setup wizard

Setup runs once, then again whenever the user wants to change something. Its job is to find out which tools this environment can reach, confirm they work, collect a few preferences, and save a config so later runs start immediately.

This skill works with whatever the user has. It thinks in roles, not products: a CRM, an email account, a calendar, a call recorder, a chat tool, and a resource library. The wizard maps each role to a real tool.

## How to run the conversation

- Detect before asking. Never ask the user something you can find out by looking at your available tools or making a read.
- Ask one question at a time, most important first.
- Offer a recommended default with every question so the user can accept it in one click or one word. If the environment has a way to present clickable choices, use it.
- Keep the whole wizard under about ten questions. Accepting every default should produce a working config.

## Step 1: Take inventory

List every tool, connector, integration, plugin, or MCP server available in this environment, and sort each into a role.

| Role | What it provides | Common examples | Fallback if missing |
| --- | --- | --- | --- |
| CRM | Open opportunities, fields, contact roles, activities, tasks | Salesforce, HubSpot, Dynamics 365, Pipedrive | A CSV or spreadsheet export of the open pipeline report, attached to the conversation |
| Email | Inbox and sent mail | Outlook / Microsoft 365, Gmail | None. Email is the core evidence source. |
| Calendar | Upcoming and past meetings | Outlook, Google Calendar (often the same connector as email) | Meeting data from the call recorder, or skip |
| Call recorder | Call dates, attendees, summaries, transcripts | Gong, Chorus, Fathom, Fireflies, meeting transcripts from Zoom or Teams | Skip. Calendar and CRM activities cover call dates. |
| Chat | Customer and internal messages | Slack, Microsoft Teams | Skip |
| Resource library | Shareable documents | SharePoint, Google Drive, OneDrive, Highspot, Seismic, Notion, a public resources page | A pasted list of titles, links, and one-line descriptions |

Show the user the result as a short table: role, tool found, and status. For each role with nothing found, offer the three choices: connect a tool now (and name the kind of connector to look for), use the fallback, or skip the role.

The CRM and email roles are required. Without either, the skill cannot do its job, so say so and stop until one is connected or a CRM export is provided. Every other role is optional. For each one skipped, tell the user in one line what the report will not be able to see.

## Step 2: Confirm access and identity

For each connected source, make one small read and show the user what came back (one opportunity name, the subject of the latest email, the next meeting). This catches expired sign-ins and wrong accounts before a full run.

Confirm who the user is in each system: their CRM owner name, and every email address they send from. The skill needs these to tell inbound from outbound, which the stale check depends on.

Then state the read-only commitment plainly: "I will only read from these tools. I will not update the CRM, send or draft email, post in chat, or change your calendar, even though some of these connectors would let me." If a connector exposes write actions, name them and confirm they will go unused.

## Step 3: Scope

Ask which opportunities to review. Defaults:

- **Owner:** the user
- **Stages:** all open stages
- **Close dates:** any
- **Other filters:** none (offer record type, region, or product line if the CRM has them)

Run the scoped query and tell the user how many opportunities it returns, so they can adjust before the first run.

## Step 4: CRM details

- **Next Step field:** find the field on the opportunity and its character limit. Default is `Next Step` with 255 characters.
- **Critical fields:** which fields should never be empty. Default is amount and close date. Offer forecast category and any required custom fields the CRM shows.
- **Initials** for the Next Step prefix, taken from the user's name, and their name as they sign emails.
- **Next-call line:** whether every Next Step ends with the next scheduled call. Default yes.
- **Date format:** default M/D.
- **What the user calls the other side:** default "Customer." Channel teams usually say "Partner," and services firms often say "Client." The Next Step text and the report use this word.

## Step 5: Resource library

Ask where shareable resources live, then build an index. For each document, open it and record:

- Title and type (case study, guide, one-pager, worksheet)
- Link
- Who it is best for (role, industry, deal stage)
- The problems it addresses, in the customer's kind of language
- Its main sections, so an email can point to a specific part

Show the index and ask the user to remove anything outdated or not approved for customers. If the library is large, index the 20 to 30 documents the user shares most and note that the rest can be added later.

## Step 6: Thresholds and output

Confirm or change:

- **Stale threshold:** 14 days with no two-way contact
- **Sweep window:** 14 days
- **Chase threshold:** 3 business days
- **Context window:** 90 days of history per deal
- **Where to save reports,** and whether to produce the HTML version alongside the markdown (default yes when the environment can run the build script)
- **Tier names.** The report sorts actions into Critical, Important, and Routine. Offer to rename them if the team uses other words.
- **Report theme** for the HTML version. Offer the built-in themes (`paper`, a light neutral that follows the reader's dark mode setting, `graphite`, a near-black theme with soft color glows, and `midnight`, the same style in deep navy), or the user's own brand: ask for an accent color as a hex value and, if they want one, a font name and a link to its stylesheet. A fully custom look is a new CSS file in `assets/themes/`, copied from `graphite.css`.

## Step 7: Save and hand off

Fill in `assets/config-template.md` with the answers and save it as `pipeline-config.md`:

- If the environment has a file system or project files, save it in the working folder.
- If it has memory or project instructions, save it there.
- If it has neither, show the config in a code block and ask the user to keep it and paste it at the start of future runs.

Show a five-line summary of the setup, then offer the next step: run the demo first, or run on the real pipeline now.

## Changing settings later

When the user asks to change one thing ("make the stale threshold 21 days," "add Slack"), update that part of the config, confirm the change in one line, and leave the rest alone. Rebuild the resource index only when asked or when it is more than 30 days old.

---

# Part 3: Evidence rules (`references/evidence-rules.md`)

# Evidence rules

The user acts on this report without re-reading every thread. That only works if every line is true. These rules exist because the most damaging failure of a tool like this is a confident statement that the source does not support: a commitment nobody made, a date nobody said, a "probably" written down as a "will."

## The rules

**1. No source, no statement.** Every claim about a deal needs a date, a source type (email, call, chat, calendar, CRM), and a person. If you cannot point to all three, leave the claim out.

**2. Quote or stay close to the wording. Never upgrade it.** Use the speaker's own words where they fit in one line. When you paraphrase, keep the same strength. "We'll try to get to it next week" does not become "Customer will review next week."

**3. Sort every commitment into firm or soft.**

- **Firm:** a specific action with an owner, and either a date or explicit agreement. "Send the redlined MSA by 11/20 and we'll return the signature packet by 12/4."
- **Soft:** hedged, conditional, or undated. Watch for maybe, probably, hopefully, should be able to, could, might, "I don't know yet," "if all goes well," "sometime in," "early December," and anything relayed secondhand.

Soft statements can appear in the report, labeled as soft, because they are useful context. They are never written into a Next Step as a commitment and never treated as a deadline.

**4. Dates come only from sources.** Use a date only if someone stated it or it is a system fact (a meeting on the calendar, a CRM field value). Resolve relative dates against the date of the message and show the result in brackets: "by Tuesday [11/17]." If no date was agreed, write "no date set." Never fill in a reasonable-sounding one.

**5. "Nothing found" is a claim about the sources you checked.** "No reply found in email or chat since 11/10" is accurate. "The customer has not responded" claims more than you know, since they may have called or replied somewhere you cannot see. Word absences as what was searched and what was not found.

**6. Names and titles come from records.** Use CRM contact records, email signatures, and call attendee lists. Do not guess a title or a role from the tone of a message.

**7. Numbers come from the CRM or from someone's mouth.** Amounts, counts, and percentages are reported as stated, with the source. Do not calculate savings, ROI, or probabilities, and do not round a stated figure into a different one.

**8. Claims about a resource come from reading the resource.** Before recommending a document or describing it in an email draft, open it. A title is not enough to know what it says.

**9. Report facts, not readings of intent.** "No inbound message since 10/27" is a fact. "The champion is losing interest" and "they are going dark" are guesses. Leave them out.

**10. Rep notes are evidence of what the rep recorded.** A CRM note that says "customer agreed to pilot" shows that the rep wrote that. It is weaker than the customer saying it in an email or on a call. Label it as a rep note, and prefer the customer's own words when both exist.

**11. When sources conflict, the most recent dated evidence wins.** Use it, and record the disagreement under Notes in the report with both versions and their dates, so the user can see what changed. A CRM field with no modification date loses to any dated message.

**12. If you cannot confirm something was done, say that.** Attachments you cannot open, a spreadsheet you cannot see, a phone call that may have happened: write "could not confirm" and name what you could not check. Do not assume it was done, and do not assume it was not.

## Final verification pass

Do this after the report is drafted and before it is delivered. It is the last line of defense against stretched facts, and it matters most on long runs when early details have faded.

For each item in the report:

1. Reopen the cited source. Confirm the date, the person, and the wording match what the report says.
2. Check every date in a Next Step or email draft against the evidence listed under it. A date with no evidence comes out.
3. Check that nothing soft has been written as firm.
4. Check that the item could only describe this deal. If it would read the same pasted under a different account, it is too generic: add the specific person, date, number, or deliverable, or cut it.
5. For any "you owe" or "chase" item, search once more for a later message in any channel that resolves it.

Remove or correct anything that fails. A shorter report that is fully true is the goal.

---

# Part 4: Pipeline review (`references/pipeline-review.md`)

# Pipeline review: Next Step and CRM hygiene

For each open opportunity, compare what the CRM says with what the evidence log shows, and suggest only the changes needed to make the record accurate.

## The Next Step field

The Next Step field is a status report for anyone reading the pipeline: a manager, a forecast call, the rep in three weeks. It should say what is agreed to happen next, who owns it, and when. It records the state of the deal. It is not advice on what the rep ought to do.

### Decide whether it needs changing

Read the current value and the date it was last modified, then look at the evidence since that date.

- **Keep it** if it still describes the next agreed step, its dates are in the future, and its next-call line matches the calendar. Do not rewrite an accurate entry in different words. List the deal under "Reviewed, no action" if nothing else needs attention.
- **Replace it** if the step it describes has already happened, a newer commitment exists, its dates have passed, it is too vague to tell anyone anything ("follow up," "send proposal," "awaiting feedback"), its next-call line is missing or wrong, or it is empty.

### Format

```
M/D INITIALS: [the rep's next action] by M/D.
Customer to [the customer's next action] by M/D.
Next call scheduled M/D.
```

Use the config's `counterparty_label` in place of "Customer" on line two. Teams that sell through a channel usually say "Partner," and agencies and services firms often say "Client."

- The prefix is today's date and the user's initials from the config, so readers can see when the entry was written and by whom.
- Line one is what the rep owns. Line two is what the customer owns. Leave out a line if that side has no agreed action.
- The last line is the next meeting with the account that is on the calendar: `Next call scheduled 11/20.` A short note in parentheses can say what it is: `Next call scheduled 11/20 (technical review).` Take the date only from a calendar entry, never from a mention in an email that a call "should" happen. If nothing is booked, write `Next call: not scheduled.` and say so in the item's detail line, because a deal with no next call on the calendar is worth noticing. This line is on by default and controlled by `next_call_line` in the config.
- Stay within the field's character limit from the config (255 by default, which is the standard Salesforce limit).
- Name people and deliverables: "Send revised pricing with the 60-device tier to Dana Whitfield," not "Send pricing."
- If a meeting is the next step, state it as a fact with its date: "Technical review with Hannah Liu 11/20."

### What goes in it

Only firm commitments and scheduled events from the evidence log. Follow `evidence-rules.md` closely here, because this text gets pasted into a system of record.

- Every date after the prefix must appear in the evidence listed under the item. The build script rejects a Next Step containing a date its evidence does not show.
- A soft statement never appears as a commitment. If the customer said they "might revisit in early December," that does not go in the Next Step. It can go in the item's detail line, marked soft.
- If an action is agreed but has no date, write "(no date set)" instead of choosing one.

### When there is no agreed next step

Say so. An honest "no next step" is more useful to a pipeline review than an invented one.

```
11/17 RB: No agreed next step. Last customer reply 10/27 (Priya Raman); follow-ups sent 11/3 and 11/10 with no reply.
Next call: not scheduled.
```

### What the report shows for each suggestion

- The current value, so the user can see what is being replaced
- The suggested value in a copy block
- One to three lines of evidence: date, source, person, and the words that support it

## Hygiene checks

Run these three checks on every opportunity. Report only what fails.

### Past-due close date

Flag when the close date is earlier than today.

Also flag when the close date is still in the future but dated evidence from the customer contradicts it, for example the customer said no decision is possible before a board meeting that falls after the close date.

Do not pick a new close date. State what the evidence supports and let the user choose:

- If the customer gave a date or a constraint: "No decision before the 12/9 budget review (Elena Vasquez, 11/5 email). Set a close date after 12/9."
- If nothing in the evidence points to a date: "Close date passed 10/31. No decision timing found in email, calls, or chat. Needs a new date from the customer."

### Missing contact roles

Flag a person when all three are true:

1. They are at the customer (their email domain matches the account, or a customer contact introduced them).
2. They took part within the context window: sent or were copied on a deal thread, attended a call, or posted in a shared channel.
3. They are not listed as a contact role on the opportunity.

Give the name, email, title, and role in the deal only as far as the evidence shows them (a signature, an introduction like "our controller, who will handle the PO," a call attendee list). If the title is unknown, say "title not found" instead of guessing. Skip people who appear once on a large cc line with no part in the conversation.

### Critical field gaps

Flag any field on the config's `critical_fields` list that is empty, zero, or a placeholder. The default list is amount and close date. An empty Next Step is handled by the Next Step review above and does not need a second flag.

Do not suggest a value unless the evidence states one. For a missing amount, the item says the field is empty and, if a figure was discussed, cites where: "Amount is empty. No pricing found in email or calls yet."

## What this step does not do

- It does not judge whether the stage is right. Stage definitions vary by company and the call belongs to the rep.
- It does not score deal health or predict outcomes.
- It does not suggest sales tactics.

---

# Part 5: Stale deals (`references/stale-deals.md`)

# Stale deals and the re-engagement email

A deal is stale when nobody at the account has been in two-way contact with the user for the stale threshold (14 calendar days by default). Stale deals inflate a forecast and are easy to miss, because a rep who has been sending follow-ups feels like the deal is active.

## Find the last two-way contact

For each opportunity, find the most recent date on which someone at the account communicated back. These count:

- **An inbound email** from anyone at the account to the user
- **A held meeting or call** where at least one person from the account attended
- **A chat message** from a customer contact in a shared channel or direct message
- **A logged CRM activity** recording a call or meeting that took place

These do not count:

- Anything the user sent. Outbound follow-ups with no reply are the definition of one-way.
- Automatic replies and out-of-office notices
- Calendar accept, decline, and tentative notices, which are system-generated
- Marketing email opens, link clicks, and website visits
- A CRM activity that only logs an outbound email or a voicemail
- A meeting that was scheduled but cancelled or never held

If no two-way contact exists at all, the deal is stale from its created date.

Record the date and what it was ("10/27 email from Priya Raman"). The build script computes the day count from that date, so do not do the arithmetic yourself.

## Flag every stale deal

There are no exemptions. A deal in legal review, a deal where the customer said they would come back next month, and a deal with a meeting on the calendar are all flagged if the threshold has passed. The user asked for this deliberately: the report shows the silence and the context, and the user decides whether it matters.

Add the context that changes how the flag should be read:

- **A meeting is booked.** Note the date. The draft becomes a short pre-meeting note that shares the resource ahead of the conversation, instead of a re-engagement email.
- **The customer set expectations.** If they said when they would return or why they are quiet, cite it, and mark it soft if it was hedged.
- **The user has been trying.** Note the outbound attempts and their dates.

## Choose a resource

Use the resource index from the config. Read the candidate documents themselves before choosing. A title is not enough to know what a document says.

A resource is a strong fit only when both are true:

1. **Two customer-stated points.** You can cite at least two specific things the customer said (dated, in the evidence log) that the resource directly addresses. The points must come from the customer. Something the rep said or assumed does not count.
2. **Not already sent.** Search the user's sent mail to this account for the resource's title and link.

Matching on industry, company size, or product alone is not a fit. A healthcare brief is not a fit for a healthcare prospect who has not named a problem it answers. This rule is what keeps the emails from reading as generic, since an email built on two things the customer said is specific by construction.

If two resources both qualify, pick the one that answers the most recent customer statement.

## When nothing fits

Do not draft an email and do not fall back to the closest match. In the report:

- State that no resource is a strong fit and why, in one line. If there was a near miss, name it and say what was missing.
- Offer one re-engagement angle taken from the evidence, such as an open question from the last conversation or a soft timing the customer mentioned. Keep it to one line and label soft statements as soft.

## Recommend a recipient

Suggest one recipient with a one-line reason and list the alternates. The user makes the choice. Usually the best recipient is the person who raised the points the resource answers, or the person who most recently replied. Say which reasoning you used.

Only suggest people with a known email address from the CRM or the threads.

## Write the draft

The draft goes in the report for the user to review, edit, and send themselves.

**Structure**

1. One line of context that ties to the last real exchange
2. The resource, as a link, with a few words on what it is
3. Two short points, each connecting something the customer said to a specific part of the resource
4. An offer of help with one easy, concrete next step

**Limits**

- Body of 120 words or fewer. Busy people read short emails.
- A subject line under 80 characters that names the topic, not the follow-up
- Plain text with no formatting beyond a short list

**Voice**

Read two or three of the user's sent emails to this contact and match their greeting, sign-off, and level of formality. Sign with the user's name from the config.

**Keep out**

- Filler openers and closers: "just checking in," "touching base," "circling back," "hope this finds you well"
- Urgency the evidence does not support, such as discounts, deadlines, or "limited availability"
- Guilt about the silence ("I haven't heard back")
- Anything about the resource that is not in the resource
- Numbers the customer did not state and the resource does not contain

**Pre-meeting variant**

When a meeting is already booked, open with the meeting and its date, share the resource as preparation, and close by asking whether there is anything else they want covered. If the user owes this contact something that is still outstanding, it is honest and useful to say where that stands.

## What the report shows

For each stale deal: the last two-way contact and the day count, any context from above, then either the draft (recipient, reason, alternates, resource, subject, body) or the no-fit note. The evidence lines list the customer statements the two points were built on.

---

# Part 6: Owes and chases (`references/owes-and-chases.md`)

# Owes and chases sweep

Deals slip on small things: a promised document that never went out, a question from a customer that got buried, a request to legal that nobody answered. This sweep finds them.

## What to search

Cover the sweep window from the config (14 days by default) across:

- **The whole inbox and sent mail,** including threads with no link to any account
- **Chat:** direct messages, shared customer channels, and internal channels where the user is addressed
- **CRM:** open tasks assigned to the user
- **Calls in the window:** commitments made out loud that the transcript or summary captured

Also include any open commitment you found while building the evidence logs, even if it was made before the sweep window. A promise from three weeks ago that is still open matters more than one from yesterday.

## What counts as an owe

The user owes something when any of these is true and nothing later resolves it:

1. **The user committed to it.** "I'll send revised pricing by Tuesday." "Let me get that from legal."
2. **Someone asked the user directly** for an answer, a document, or an action, and the user has not responded.
3. **A CRM task** assigned to the user is open and due or overdue.

For each, capture who is waiting, what they are waiting for, when it was asked or promised, and the due date if one was stated. For a request that came in from someone else, record the date it was asked so the report can show how long they have waited.

## What counts as a chase

The user needs to chase when they asked someone for something specific (an answer, a document, a decision, an introduction) and no reply has arrived after the chase threshold (3 business days by default).

A message from the user that asks for nothing does not create a chase. "Thanks, talk soon" has nothing to chase. Record the date of the ask. The build script counts the business days.

## Check whether it is already resolved

Before listing anything, look for a later message that closes it, in any channel. Promises made on a call are often kept by email. Questions asked by email are often answered in chat. Check:

- Later messages in the same thread
- Other threads with the same person
- Chat with the same person
- A sent email with an attachment whose name matches the promised item
- A calendar invite, if the promise was to schedule something

If something was probably done but you cannot see proof (a shared spreadsheet you cannot open, a phone call), list it and mark it "could not confirm," naming what you could not check. This follows rule 12 in `evidence-rules.md`.

## Filter out noise

A whole-inbox sweep picks up a lot that is not a real obligation. Leave out:

- Newsletters, marketing email, and vendor cold outreach, even when they ask a question
- Automated notifications: system alerts, calendar notices, automatic replies, delivery receipts, CRM digests
- Threads where the user is only copied and nobody addresses them
- Rhetorical or social questions ("How was the weekend?")
- Anything resolved, per the check above

When unsure whether something is a real ask, include it only if a specific person is waiting on a specific thing from the user.

## Where each item goes in the report

- **Tied to an account** (a customer contact, or an internal thread about that deal, such as a request from a sales engineer or to legal): list it under that account, so the user sees everything for the deal in one place.
- **Not tied to an account** (a manager's request, a colleague's question, personal admin): list it under "Internal and other."

When the user both owes a customer something and is chasing a colleague for the thing they owe, write one item, not two: "Chase Dev Malhotra for the security questionnaire. You told Hannah Liu on 10/30 you would send it." One action clears both.

## Keep each item to one action

Lead with the verb and name the person and the thing: "Send the Q3 restore test report to Kofi Mensah." Add the due date if one was stated and the evidence line underneath. Do not draft the reply in the report. The user can ask for a draft of any item afterwards, and leaving drafts out keeps the report short enough to read.

---

# Part 7: Report format (`references/report-format.md`)

# Report format

The report is one ordered checklist. A seller should be able to open it, work top to bottom, and paste each suggestion into its destination without reading anything twice.

## Contents

1. Urgency tiers
2. Ordering
3. Length caps
4. Wording
5. Report data (JSON)
6. Building the report
7. Markdown layout, for writing by hand

## 1. Urgency tiers

Each item gets an urgency. Each account is placed in the tier of its most urgent item, and all of that account's items appear together there, so the user handles a deal once.

| Tier | An item belongs here when |
| --- | --- |
| **Critical** | A deadline (the user's or the customer's) is missed, due today, or due the next business day. Or a customer has waited 3 or more business days on a direct question. |
| **Important** | A deadline falls within 7 days. Or the item is a chase, a stale deal, or a close date that needs correcting. |
| **Routine** | CRM upkeep with no deadline attached (a Next Step refresh, a contact role, an empty field), or an owe with no date where nobody outside the company is waiting. |

Deadlines must be real: a date someone stated or a meeting on the calendar. Do not create urgency from deal size or from a sense that something has dragged on.

## 2. Ordering

Within a tier, accounts are ordered by these, in sequence:

1. Earliest explicit deadline among the account's items
2. Nearest close date
3. Most days since two-way contact
4. Largest amount, as the tiebreaker

The build script applies this order. When writing by hand, apply it yourself.

## 3. Length caps

These are hard limits. They exist because a report that runs long does not get read.

| Element | Cap |
| --- | --- |
| Items per account | 6. If there are more, keep the 6 most urgent and add a note with the count left out. |
| Item title | 110 characters. Start with a verb, unless the label already is the action (Add contact role, Fill empty field), in which case the title names the person or field. |
| Item detail line | 220 characters, optional |
| Evidence lines per item | 1 to 3, each 220 characters or fewer |
| Next Step text | The field's character limit (255 by default) |
| Email subject | 80 characters |
| Email body | 120 words |
| "Reviewed, no action" entry | 140 characters, one line per account |
| Notes section | 5 notes, each 240 characters or fewer |
| Internal and other items | 8 |
| Chat summary on delivery | 5 lines |

Deals with nothing to do appear only in the one-line "Reviewed, no action" list at the end. That list matters: it shows the user that every deal was checked.

## 4. Wording

- **One action per item,** verb first, naming the person and the thing. "Send the Q3 restore test report to Kofi Mensah," not "Follow up with Ridgeline."
- **Specific to this deal.** Every Next Step and every email must contain something that could only be true here: a person, a date, a number, a named deliverable. If the sentence would work under a different account, rewrite or cut it.
- **No filler.** Leave out "just checking in," "touching base," "circling back," "hope this finds you well," "move the deal forward," "continue discussions," and "align on next steps." The build script rejects these in paste text and email drafts.
- **No coaching, no deal recap, no strategy.** The report says what to record and what to send.
- **No hedging on facts you verified,** and plain "could not confirm" on facts you could not.

## 5. Report data (JSON)

Write the report as one JSON file. Dates are `YYYY-MM-DD`. The script formats them for display and does all date arithmetic, so never put a day count in the data.

```json
{
  "meta": {
    "report_date": "2026-11-17",
    "prepared_for": "Riley Bennett",
    "initials": "RB",
    "mode": "live",
    "scope": "Open opportunities owned by Riley Bennett, all stages",
    "next_step_char_limit": 255,
    "next_call_line": true,
    "theme": "paper",
    "thresholds": { "stale_days": 14, "sweep_days": 14, "chase_business_days": 3 },
    "sources": [
      { "role": "CRM", "tool": "Salesforce", "status": "checked", "detail": "8 open opportunities" },
      { "role": "Chat", "tool": "", "status": "not_checked",
        "impact": "Customer messages in chat are not reflected in last-contact dates." }
    ]
  },
  "accounts": [
    {
      "account": "Northgate IT Partners",
      "opportunities": [
        {
          "name": "Northgate IT - Fleet migration (38 devices)",
          "amount": 86400,
          "stage": "Negotiation",
          "close_date": "2026-11-30",
          "last_two_way": { "date": "2026-11-13", "what": "call with Dana Whitfield and Marcus Oyelaran" }
        }
      ],
      "items": []
    }
  ],
  "other_items": [],
  "no_action": [ { "account": "Tall Pine Tech", "amount": 29900, "note": "Next Step current as of 11/12. Demo booked 11/24." } ],
  "notes": []
}
```

- `mode` is `live` or `demo`.
- `tier_labels` is optional and renames the tiers in the report, for a team with its own vocabulary: `{ "critical": "Today", "important": "This week", "routine": "Backlog" }`. The `urgency` values on items do not change.
- `theme` styles the HTML version and is optional. Use the value from the config. It is a theme name (`paper` is the default, `graphite` and `midnight` are dark themes, and any file in `assets/themes/` works), or an object that adds brand overrides: `{ "name": "paper", "accent": "#0f766e", "font_family": "Inter", "font_import": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" }`. The markdown version is not affected.
- `sources[].status` is `checked` or `not_checked`. A source that was not checked needs an `impact` line saying what the report cannot see as a result.
- `amount` is a number, or `null` when the field is empty.
- `last_two_way.date` is `null` when no two-way contact exists.
- Every account under `accounts` has at least one item. Deals with nothing to do go in `no_action`, with their `amount` so the pipeline total in the header stays complete.
- `other_items` holds owes and chases not tied to any account. They use the same item shape.

### Items

```json
{
  "type": "next_step",
  "urgency": "routine",
  "title": "Update Next Step",
  "detail": "Optional single line of context.",
  "where": "CRM: Next Step",
  "current": "Send proposal",
  "paste": "11/17 RB: Send revised pricing with 60-device tier to Dana Whitfield and Marcus Oyelaran by 11/17.\nPartner to review pricing with ownership 11/19.\nNext call scheduled 11/20 (pricing follow-up).",
  "evidence": [
    { "date": "2026-11-13", "source": "call", "who": "Dana Whitfield",
      "text": "\"They've got it on the agenda for the nineteenth [11/19].\"", "soft": false }
  ]
}
```

| Field | Used by | Meaning |
| --- | --- | --- |
| `type` | all | One of the types below |
| `urgency` | all | `critical`, `important`, or `routine` |
| `title` | all | The action, verb first. Use `Update Next Step` for a `next_step` item, and the person or field name for `contact_role` and `field_gap`. |
| `detail` | optional | One line of context |
| `where` | all | Where the user does it: `Email`, `Chat`, `CRM: Next Step`, `CRM: Close Date`, `CRM: Contact Roles`, `CRM: Amount`, and so on |
| `due` | optional | A stated deadline |
| `asked_on` | `chase` (required), `owe` (when someone asked) | The date of the ask. The script counts the business days waited. |
| `current` | `next_step`, `close_date`, `field_gap` | The value in the CRM now. Use an empty string for an empty field. |
| `paste` | `next_step` (required), others optional | Text ready to copy into the destination |
| `email` | `reengage` | The draft, described below |
| `evidence` | all | 1 to 3 entries with `date`, `source`, `who`, `text`, and `soft` |

| Type | Label in the report | Notes |
| --- | --- | --- |
| `owe` | You owe | Something the user promised or was asked for |
| `chase` | Chase | Something the user asked for, unanswered past the threshold |
| `reengage` | Send re-engagement email | A stale deal with a resource that fits. Needs `email`. |
| `stale_no_fit` | Stale, no resource fit | A stale deal with no qualifying resource. Put the one-line angle in `detail`. |
| `close_date` | Fix close date | Do not include a new date unless the customer stated one |
| `next_step` | Update Next Step | `paste` must start with today's date and the user's initials |
| `contact_role` | Add contact role | Put name, title, and email in `paste` |
| `field_gap` | Fill empty field | Name the field in `where` |

The email draft for a `reengage` item:

```json
"email": {
  "to": "Priya Raman",
  "to_email": "priya.raman@blueheronit.example",
  "why": "Last to reply (10/27) and asked for something to show her owner.",
  "alternates": ["Tom Becker (Lead Engineer)"],
  "resource_title": "Case study: Fenwick IT",
  "resource_link": "https://pellmoor.example/resources/fenwick-it-case-study",
  "subject": "Migration example for your owner",
  "body": "Hi Priya,\n\n..."
}
```

### Evidence entries

`source` is one of `email`, `call`, `chat`, `calendar`, `crm`. `text` is a short quote in quotation marks or a close paraphrase. Put resolved relative dates in brackets inside the text, for example `"by Tuesday [11/17]"`, so the script can trace the date. Set `soft` to `true` for hedged statements. They are shown with a "soft" label.

## 6. Building the report

```
python scripts/build_report.py report.json --out-dir <folder>
```

This writes `pipeline-actions-YYYY-MM-DD.md` and `.html` into the folder. Add `--no-html` for markdown only.

Before writing anything, the script checks the data and stops on any error. It checks that:

- Every item has evidence with a date, a source, and a person
- Every date inside a Next Step, close-date paste, or email draft appears in that item's evidence
- A Next Step starts with today's date and the right initials, fits the character limit, and is not built only on soft statements
- A Next Step ends with its next-call line, and a scheduled date has a matching calendar entry in the evidence
- Email drafts have a recipient, a reason, a subject, and a body within the word cap
- No filler phrases appear in paste text or email drafts
- Every stale opportunity has a `reengage` or `stale_no_fit` item, and no deal that is not stale has one
- Every chase has waited at least the chase threshold
- An item due today or the next business day is marked `today`
- All length caps hold

When it reports an error, fix the data. If a date fails the trace check, either add the evidence that states it or remove the date. The script's errors are the same checks a careful reviewer would make, so passing them by loosening the data defeats the point.

## 7. Markdown layout, for writing by hand

Use this layout when the environment cannot run the script.

````markdown
# Pipeline actions: Tuesday, November 17, 2026

Prepared for Riley Bennett · 8 open opportunities · $509,550 open pipeline

**Checked:** CRM (8 open opportunities) · Email (14-day sweep, 90-day deal history) · Calendar · Calls (4 with transcripts) · Chat
**Not checked:** none

**Critical:** 2 accounts · **Important:** 4 accounts · **Routine:** 1 account · **No action:** 1 account

---

## Critical

### Northgate IT Partners
$86,400 · Negotiation · closes 11/30 · last two-way contact 11/13 (4 days ago), call with Dana Whitfield and Marcus Oyelaran

- [ ] **You owe:** Send revised pricing with the 60-device tier to Dana Whitfield and Marcus Oyelaran · due 11/17 (today) · Email
  - Evidence: 11/13 email, Riley Bennett: "I'll send revised pricing with the 60-device tier next to the 38-device quote by Tuesday 11/17."
- [ ] **Update Next Step** · CRM: Next Step
  - Current: `Send proposal`
  - Paste:
    ```
    11/17 RB: Send revised pricing with 60-device tier to Dana Whitfield and Marcus Oyelaran by 11/17.
    Partner to review pricing with ownership 11/19.
    Next call scheduled 11/20 (pricing follow-up).
    ```
  - Evidence: 11/13 call, Dana Whitfield: "They've got it on the agenda for the nineteenth [11/19]."

## Important

## Routine

## Internal and other

## Reviewed, no action

- **Tall Pine Tech:** Next Step current as of 11/12. Demo booked 11/24.

## Notes
````

For a re-engagement email, list the recipient with the reason and alternates, then the resource, the subject, and the body in a code block, followed by the evidence lines.

---

# Part 8: Config template (`assets/config-template.md`)

# Pipeline skill config

Saved by the setup wizard. Edit by hand or ask to change a setting.

last_updated: YYYY-MM-DD

## User

- name:
- initials:
- signs_emails_as:
- email_addresses:
- company:
- company_email_domains:

## Sources

Status is one of: connected, file (manual export), or not available.

| Role | Tool | Status | Notes |
| --- | --- | --- | --- |
| CRM | | | |
| Email | | | |
| Calendar | | | |
| Call recorder | | | |
| Chat | | | |
| Resource library | | | |

## Scope

- owner: me
- stages: all open
- close_dates: any
- other_filters: none
- context_days: 90

## CRM fields

- next_step_field: Next Step
- next_step_char_limit: 255
- critical_fields: Amount, Close Date
- next_call_line: yes
- date_format: M/D
- counterparty_label: Customer

## Thresholds

- stale_days: 14
- sweep_days: 14
- chase_business_days: 3

## Output

- save_reports_to:
- html_version: yes
- tier_labels: Critical, Important, Routine
- theme: paper
- theme_accent:
- theme_font_family:
- theme_font_import:

## Resource index

index_built: YYYY-MM-DD

| Title | Type | Link | Best for | Problems it addresses | Main sections |
| --- | --- | --- | --- | --- | --- |
| | | | | | |
