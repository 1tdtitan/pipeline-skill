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
