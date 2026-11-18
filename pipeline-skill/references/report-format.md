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
