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
