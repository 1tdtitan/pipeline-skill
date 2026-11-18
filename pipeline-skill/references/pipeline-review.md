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
