#!/usr/bin/env python3
"""Validate a pipeline report and render it as markdown and HTML.

Usage:
    python build_report.py report.json --out-dir ./reports
    python build_report.py report.json --check          # validate only
    python build_report.py report.json --no-html        # markdown only

The report data format is described in references/report-format.md.

This script does three jobs that are easy to get wrong by hand:
  1. Date arithmetic: days since contact, business days waited, stale flags.
  2. Ordering: accounts sorted into urgency tiers by deadline, close date,
     days of silence, then amount.
  3. Checks: length caps, evidence on every item, and a trace check that
     rejects any date in a Next Step or email draft that the item's own
     evidence does not show.

Standard library only. Python 3.9+.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

TIERS = ["critical", "important", "routine"]
# Display names. A report can rename them with meta.tier_labels; the keys stay the same.
TIER_LABEL = {"critical": "Critical", "important": "Important", "routine": "Routine"}

TYPES = {
    "owe": "You owe",
    "chase": "Chase",
    "reengage": "Send re-engagement email",
    "stale_no_fit": "Stale, no resource fit",
    "close_date": "Fix close date",
    "next_step": "Update Next Step",
    "contact_role": "Add contact role",
    "field_gap": "Fill empty field",
}
TYPE_ORDER = list(TYPES)
SOURCES = {"email", "call", "chat", "calendar", "crm"}

CAPS = {
    "items_per_account": 6,
    "title": 110,
    "detail": 220,
    "evidence_per_item": 3,
    "evidence_text": 220,
    "email_subject": 80,
    "email_words": 120,
    "no_action_note": 140,
    "notes": 5,
    "note_text": 240,
    "other_items": 8,
}

FILLER = [
    "just checking in",
    "checking in",
    "touching base",
    "touch base",
    "circling back",
    "circle back",
    "hope this finds you well",
    "hope you're doing well",
    "hope you are doing well",
    "move the deal forward",
    "continue discussions",
    "align on next steps",
]

DATE_TOKEN = re.compile(r"(?<![\d/])(\d{1,2})/(\d{1,2})(?![\d/])")
NEXT_STEP_PREFIX = re.compile(r"^(\d{1,2}/\d{1,2}) ([A-Z]{2,4}): \S")
NEXT_CALL_SET = re.compile(r"^Next call scheduled (\d{1,2}/\d{1,2})( \([^()]{1,80}\))?\.$")
NEXT_CALL_NONE = "Next call: not scheduled."


# ---------------------------------------------------------------- dates

def parse_date(value, where, errors):
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        errors.append(f"{where}: '{value}' is not a YYYY-MM-DD date")
        return None


def md(d: date) -> str:
    """11/17"""
    return f"{d.month}/{d.day}"


def short(d: date, ref: date) -> str:
    """11/17, or 1/29/27 when the year differs from the report year."""
    return md(d) if d.year == ref.year else f"{d.month}/{d.day}/{d.year % 100:02d}"


def long_date(d: date) -> str:
    return f"{d.strftime('%A')}, {d.strftime('%B')} {d.day}, {d.year}"


def next_business_day(d: date) -> date:
    n = d + timedelta(days=1)
    while n.weekday() >= 5:
        n += timedelta(days=1)
    return n


def business_days_between(start: date, end: date) -> int:
    """Weekdays after `start`, up to and including `end`. Holidays are not excluded."""
    count, cur = 0, start
    while cur < end:
        cur += timedelta(days=1)
        if cur.weekday() < 5:
            count += 1
    return count


def date_tokens(text: str) -> set[str]:
    found = set()
    for m in DATE_TOKEN.finditer(text or ""):
        month, day = int(m.group(1)), int(m.group(2))
        if 1 <= month <= 12 and 1 <= day <= 31:
            found.add(f"{month}/{day}")
    return found


def money(amount) -> str:
    if amount is None:
        return "amount empty"
    return f"${amount:,.0f}"


def plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


# ---------------------------------------------------------------- validation

def check_item(item, where, meta, report_date, errors, allowed_types=None):
    itype = item.get("type")
    if itype not in TYPES:
        errors.append(f"{where}: type '{itype}' is not one of {', '.join(TYPES)}")
        return
    if allowed_types and itype not in allowed_types:
        errors.append(f"{where}: type '{itype}' is not allowed here (use {', '.join(allowed_types)})")
    if item.get("urgency") not in TIERS:
        errors.append(f"{where}: urgency must be one of {', '.join(TIERS)}")
        return

    title = (item.get("title") or "").strip()
    if not title:
        errors.append(f"{where}: missing title")
    elif len(title) > CAPS["title"]:
        errors.append(f"{where}: title is {len(title)} characters (cap {CAPS['title']})")
    detail = item.get("detail") or ""
    if len(detail) > CAPS["detail"]:
        errors.append(f"{where}: detail is {len(detail)} characters (cap {CAPS['detail']})")
    if not (item.get("where") or "").strip():
        errors.append(f"{where}: missing 'where' (the destination for this action)")

    # Evidence: every item needs a dated, sourced, attributed line.
    evidence = item.get("evidence") or []
    if not evidence:
        errors.append(f"{where}: no evidence. Every item needs at least one dated source.")
    if len(evidence) > CAPS["evidence_per_item"]:
        errors.append(f"{where}: {len(evidence)} evidence lines (cap {CAPS['evidence_per_item']})")
    traceable = {md(report_date)}
    for j, ev in enumerate(evidence):
        ew = f"{where} evidence {j + 1}"
        ev_date = parse_date(ev.get("date"), ew, errors)
        if ev.get("date") is None:
            errors.append(f"{ew}: missing date")
        if ev_date:
            traceable.add(md(ev_date))
            if ev_date > report_date:
                if ev.get("source") != "calendar":
                    errors.append(f"{ew}: dated in the future but is not a calendar entry")
        if ev.get("source") not in SOURCES:
            errors.append(f"{ew}: source must be one of {', '.join(sorted(SOURCES))}")
        if not (ev.get("who") or "").strip():
            errors.append(f"{ew}: missing 'who'")
        text = (ev.get("text") or "").strip()
        if not text:
            errors.append(f"{ew}: missing text")
        elif len(text) > CAPS["evidence_text"]:
            errors.append(f"{ew}: text is {len(text)} characters (cap {CAPS['evidence_text']})")
        traceable |= date_tokens(text)

    # Deadlines and urgency.
    due = parse_date(item.get("due"), f"{where} due", errors)
    if due:
        if due <= next_business_day(report_date) and item["urgency"] != "critical":
            errors.append(f"{where}: due {md(due)} is today or the next business day, so urgency must be 'critical'")
        elif due <= report_date + timedelta(days=7) and item["urgency"] == "routine":
            errors.append(f"{where}: due {md(due)} is within 7 days, so urgency cannot be 'routine'")
    if itype in ("chase", "reengage", "stale_no_fit", "close_date") and item["urgency"] == "routine":
        errors.append(f"{where}: a {itype} item is at least 'important'")

    asked = parse_date(item.get("asked_on"), f"{where} asked_on", errors)
    if itype == "chase":
        if not asked:
            errors.append(f"{where}: a chase needs 'asked_on', the date of the user's ask")
        else:
            waited = business_days_between(asked, report_date)
            need = meta["thresholds"]["chase_business_days"]
            if waited < need:
                errors.append(f"{where}: asked {md(asked)}, only {plural(waited, 'business day')} ago (chase threshold is {need})")

    # Text that gets pasted or sent.
    outgoing = []
    paste = item.get("paste")
    if paste:
        outgoing.append(("paste", paste))
    if itype == "next_step":
        if not paste:
            errors.append(f"{where}: a next_step item needs 'paste'")
        else:
            limit = meta.get("next_step_char_limit", 255)
            if len(paste) > limit:
                errors.append(f"{where}: Next Step is {len(paste)} characters (field limit {limit})")
            m = NEXT_STEP_PREFIX.match(paste)
            if not m:
                errors.append(f"{where}: Next Step must start with 'M/D INITIALS: ' (for example '{md(report_date)} {meta['initials']}: ...')")
            else:
                if m.group(1) != md(report_date):
                    errors.append(f"{where}: Next Step prefix date {m.group(1)} is not the report date {md(report_date)}")
                if m.group(2) != meta["initials"]:
                    errors.append(f"{where}: Next Step initials {m.group(2)} do not match {meta['initials']}")
            if evidence and all(ev.get("soft") for ev in evidence):
                errors.append(f"{where}: Next Step rests only on soft statements. Soft statements are not commitments.")
            if meta.get("next_call_line", True):
                last_line = paste.strip().split("\n")[-1].strip()
                booked = NEXT_CALL_SET.match(last_line)
                if booked:
                    on_calendar = [
                        ev for ev in evidence
                        if ev.get("source") == "calendar" and ev.get("date")
                        and date.fromisoformat(ev["date"]) >= report_date and md(date.fromisoformat(ev["date"])) == booked.group(1)
                    ]
                    if not on_calendar:
                        errors.append(f"{where}: 'Next call scheduled {booked.group(1)}' needs a calendar entry for that date in the evidence")
                elif last_line != NEXT_CALL_NONE:
                    errors.append(
                        f"{where}: Next Step must end with 'Next call scheduled M/D.' (a short note in parentheses is allowed) "
                        f"or '{NEXT_CALL_NONE}'"
                    )
        if "current" not in item:
            errors.append(f"{where}: a next_step item needs 'current' (use an empty string for an empty field)")

    email = item.get("email")
    if itype == "reengage":
        if not email:
            errors.append(f"{where}: a reengage item needs an 'email' draft")
        else:
            for key in ("to", "to_email", "why", "resource_title", "resource_link", "subject", "body"):
                if not (email.get(key) or "").strip():
                    errors.append(f"{where}: email is missing '{key}'")
            subject, body = email.get("subject") or "", email.get("body") or ""
            if len(subject) > CAPS["email_subject"]:
                errors.append(f"{where}: email subject is {len(subject)} characters (cap {CAPS['email_subject']})")
            words = len(body.split())
            if words > CAPS["email_words"]:
                errors.append(f"{where}: email body is {words} words (cap {CAPS['email_words']})")
            if len(evidence) < 2:
                errors.append(f"{where}: a resource fit needs at least two customer statements as evidence")
            outgoing.append(("email subject", subject))
            outgoing.append(("email body", body))
    elif email:
        errors.append(f"{where}: only reengage items carry an email draft")

    for label, text in outgoing:
        lowered = text.lower()
        for phrase in FILLER:
            if phrase in lowered:
                errors.append(f"{where}: {label} contains filler phrase '{phrase}'")
                break
        for token in sorted(date_tokens(text) - traceable):
            errors.append(
                f"{where}: {label} mentions {token}, which none of this item's evidence shows. "
                "Add the evidence that states it or remove the date."
            )


def validate(report):
    errors = []
    meta = report.get("meta") or {}
    for key in ("report_date", "prepared_for", "initials", "scope", "thresholds", "sources"):
        if key not in meta:
            errors.append(f"meta: missing '{key}'")
    if errors:
        return errors, None
    report_date = parse_date(meta["report_date"], "meta.report_date", errors)
    if not report_date:
        return errors, None
    if meta.get("mode", "live") not in ("live", "demo"):
        errors.append("meta.mode must be 'live' or 'demo'")
    labels = meta.get("tier_labels")
    if labels is not None:
        if not isinstance(labels, dict) or set(labels) - set(TIERS):
            errors.append(f"meta.tier_labels must be an object with keys from: {', '.join(TIERS)}")
        else:
            for key, value in labels.items():
                if not isinstance(value, str) or not (1 <= len(value.strip()) <= 24):
                    errors.append(f"meta.tier_labels.{key} must be 1 to 24 characters")
                else:
                    TIER_LABEL[key] = value.strip()
    for key in ("stale_days", "sweep_days", "chase_business_days"):
        if not isinstance(meta["thresholds"].get(key), int):
            errors.append(f"meta.thresholds: missing integer '{key}'")
    if errors:
        return errors, None

    for i, src in enumerate(meta["sources"]):
        sw = f"meta.sources[{i}] ({src.get('role', '?')})"
        if not src.get("role"):
            errors.append(f"{sw}: missing role")
        if src.get("status") not in ("checked", "not_checked"):
            errors.append(f"{sw}: status must be 'checked' or 'not_checked'")
        if src.get("status") == "not_checked" and not (src.get("impact") or "").strip():
            errors.append(f"{sw}: a source that was not checked needs an 'impact' line")

    stale_days = meta["thresholds"]["stale_days"]
    for a, acct in enumerate(report.get("accounts") or []):
        name = acct.get("account") or f"accounts[{a}]"
        items = acct.get("items") or []
        if not items:
            errors.append(f"{name}: no items. Deals with nothing to do belong in 'no_action'.")
        if len(items) > CAPS["items_per_account"]:
            errors.append(f"{name}: {len(items)} items (cap {CAPS['items_per_account']}). Keep the most urgent and note the rest.")
        any_stale = False
        for o, opp in enumerate(acct.get("opportunities") or []):
            ow = f"{name} opportunity {o + 1}"
            for key in ("name", "stage"):
                if not opp.get(key):
                    errors.append(f"{ow}: missing '{key}'")
            if "amount" not in opp:
                errors.append(f"{ow}: missing 'amount' (use null when the field is empty)")
            close = parse_date(opp.get("close_date"), f"{ow} close_date", errors)
            ltw = opp.get("last_two_way") or {}
            last = parse_date(ltw.get("date"), f"{ow} last_two_way.date", errors)
            if last and last > report_date:
                errors.append(f"{ow}: last two-way contact {md(last)} is after the report date")
            if last and not (ltw.get("what") or "").strip():
                errors.append(f"{ow}: last_two_way needs 'what' (for example 'email from Priya Raman')")
            days = (report_date - last).days if last else None
            opp["_close"], opp["_last"], opp["_days"] = close, last, days
            opp["_stale"] = last is None or days >= stale_days
            any_stale = any_stale or opp["_stale"]
            if close and close < report_date and not any(it.get("type") == "close_date" for it in items):
                errors.append(f"{ow}: close date {md(close)} has passed but there is no close_date item")
        if not acct.get("opportunities"):
            errors.append(f"{name}: no opportunities listed")
        has_stale_item = any(it.get("type") in ("reengage", "stale_no_fit") for it in items)
        if any_stale and not has_stale_item:
            errors.append(f"{name}: an opportunity is stale ({stale_days}+ days without two-way contact) but there is no reengage or stale_no_fit item")
        if has_stale_item and not any_stale:
            errors.append(f"{name}: has a stale-deal item but no opportunity is past the {stale_days}-day threshold")
        for i, item in enumerate(items):
            check_item(item, f"{name} item {i + 1} ({item.get('type', '?')})", meta, report_date, errors)

    other = report.get("other_items") or []
    if len(other) > CAPS["other_items"]:
        errors.append(f"other_items: {len(other)} items (cap {CAPS['other_items']})")
    for i, item in enumerate(other):
        check_item(item, f"other_items {i + 1} ({item.get('type', '?')})", meta, report_date, errors, allowed_types=("owe", "chase"))

    for i, entry in enumerate(report.get("no_action") or []):
        if not entry.get("account") or not entry.get("note") or "amount" not in entry:
            errors.append(f"no_action[{i}]: needs 'account', 'amount' (null if empty), and 'note'")
        elif len(entry["note"]) > CAPS["no_action_note"]:
            errors.append(f"no_action[{i}] ({entry['account']}): note is {len(entry['note'])} characters (cap {CAPS['no_action_note']})")
    notes = report.get("notes") or []
    if len(notes) > CAPS["notes"]:
        errors.append(f"notes: {len(notes)} notes (cap {CAPS['notes']})")
    for i, note in enumerate(notes):
        if len(note) > CAPS["note_text"]:
            errors.append(f"notes[{i}]: {len(note)} characters (cap {CAPS['note_text']})")
    return errors, report_date


# ---------------------------------------------------------------- ordering

def item_sort_key(item):
    due = item.get("due") or "9999-12-31"
    return (TIERS.index(item["urgency"]), due, TYPE_ORDER.index(item["type"]))


def organize(report, report_date):
    far = date(9999, 12, 31)
    tiers = {t: [] for t in TIERS}
    for acct in report.get("accounts") or []:
        acct["items"].sort(key=item_sort_key)
        tier = min((it["urgency"] for it in acct["items"]), key=TIERS.index)
        dues = [date.fromisoformat(it["due"]) for it in acct["items"] if it.get("due")]
        closes = [o["_close"] for o in acct["opportunities"] if o["_close"]]
        days = [o["_days"] for o in acct["opportunities"] if o["_days"] is not None]
        amounts = [o["amount"] or 0 for o in acct["opportunities"]]
        acct["_key"] = (min(dues, default=far), min(closes, default=far), -max(days, default=0), -sum(amounts))
        tiers[tier].append(acct)
    for accounts in tiers.values():
        accounts.sort(key=lambda a: a["_key"])
    report["other_items"] = sorted(report.get("other_items") or [], key=item_sort_key)
    return tiers


def stats(report, tiers):
    opps = [o for a in report.get("accounts") or [] for o in a["opportunities"]]
    no_action = report.get("no_action") or []
    open_count = len(opps) + sum(int(e.get("opportunities", 1)) for e in no_action)
    total = sum(o["amount"] or 0 for o in opps) + sum(e.get("amount") or 0 for e in no_action)
    return {
        "open_count": open_count,
        "total": total,
        "stale": sum(1 for o in opps if o["_stale"]),
        "items": sum(len(a["items"]) for a in report.get("accounts") or []) + len(report.get("other_items") or []),
        "tier_counts": {t: len(tiers[t]) for t in TIERS},
        "no_action": len(no_action),
    }


# ---------------------------------------------------------------- shared text

def opp_line(opp, report_date, stale_days):
    parts = [money(opp["amount"]), opp["stage"]]
    close = opp["_close"]
    if close:
        label = f"closes {short(close, report_date)}"
        if close < report_date:
            label = f"close date {short(close, report_date)} has passed"
        parts.append(label)
    if opp["_last"]:
        ago = "today" if opp["_days"] == 0 else f"{plural(opp['_days'], 'day')} ago"
        parts.append(f"last two-way contact {short(opp['_last'], report_date)} ({ago}), {opp['last_two_way']['what']}")
    else:
        parts.append("no two-way contact on record")
    return parts, opp["_stale"]


def item_meta(item, report_date):
    bits = []
    if item.get("due"):
        due = date.fromisoformat(item["due"])
        tag = f"due {short(due, report_date)}"
        if due < report_date:
            tag += " (overdue)"
        elif due == report_date:
            tag += " (today)"
        bits.append(tag)
    if item.get("asked_on"):
        asked = date.fromisoformat(item["asked_on"])
        waited = business_days_between(asked, report_date)
        bits.append(f"asked {short(asked, report_date)}, waiting {plural(waited, 'business day')}")
    bits.append(item["where"])
    return bits


def item_heading(item):
    label, title = TYPES[item["type"]], item["title"].strip()
    if title.lower().rstrip(".") == label.lower():
        return label, ""
    return label, title


def evidence_source(ev, report_date):
    """'11/13 call, Dana Whitfield', or just '11/19 calendar' for system entries."""
    d = date.fromisoformat(ev["date"])
    who = ev["who"].strip()
    source = "CRM" if ev["source"] == "crm" else ev["source"]
    label = f"{short(d, report_date)} {source}"
    return label if who.lower().startswith(ev["source"]) else f"{label}, {who}"


def evidence_line(ev, report_date):
    soft = " (soft)" if ev.get("soft") else ""
    return f"{evidence_source(ev, report_date)}{soft}: {ev['text']}"


def source_lines(meta):
    checked, missing = [], []
    for src in meta["sources"]:
        name = src["role"]
        if src.get("tool"):
            name += f" ({src['tool']})"
        if src["status"] == "checked":
            checked.append(name + (f": {src['detail']}" if src.get("detail") else ""))
        else:
            missing.append(f"{name}: {src['impact']}")
    return checked, missing


# ---------------------------------------------------------------- markdown

def md_item(item, report_date):
    label, title = item_heading(item)
    head = f"**{label}:** {title}" if title else f"**{label}**"
    out = [f"- [ ] {head} · " + " · ".join(item_meta(item, report_date))]
    if item.get("detail"):
        out.append(f"  - {item['detail']}")
    if "current" in item:
        current = item["current"].replace("\n", " / ") if item["current"] else "(empty)"
        out.append(f"  - Current: `{current}`")
    email = item.get("email")
    if email:
        alts = f" Alternates: {', '.join(email['alternates'])}." if email.get("alternates") else ""
        out.append(f"  - To: {email['to']} <{email['to_email']}>. {email['why']}{alts}")
        out.append(f"  - Resource: [{email['resource_title']}]({email['resource_link']})")
        out.append(f"  - Subject: `{email['subject']}`")
        out.append("  - Body:")
        out.append("    ```")
        out.extend(("    " + line).rstrip() for line in email["body"].split("\n"))
        out.append("    ```")
    if item.get("paste"):
        out.append("  - Paste:")
        out.append("    ```")
        out.extend(("    " + line).rstrip() for line in item["paste"].split("\n"))
        out.append("    ```")
    for ev in item["evidence"]:
        out.append(f"  - Evidence: {evidence_line(ev, report_date)}")
    return out


def render_markdown(report, tiers, report_date):
    meta = report["meta"]
    s = stats(report, tiers)
    stale_days = meta["thresholds"]["stale_days"]
    lines = [f"# Pipeline actions: {long_date(report_date)}", ""]
    if meta.get("mode") == "demo":
        lines += ["> **Demo.** All data in this report is fictional.", ""]
    opp_word = "open opportunity" if s["open_count"] == 1 else "open opportunities"
    lines.append(
        f"Prepared for {meta['prepared_for']} · {s['open_count']} {opp_word}"
        f" · {money(s['total'])} open pipeline"
    )
    lines.append("")
    lines.append(f"Scope: {meta['scope']}")
    lines.append("")
    checked, missing = source_lines(meta)
    lines.append("**Checked:** " + " · ".join(checked))
    lines.append("")
    lines.append("**Not checked:** " + (" · ".join(missing) if missing else "none"))
    lines.append("")
    counts = " · ".join(f"**{TIER_LABEL[t]}:** {plural(s['tier_counts'][t], 'account')}" for t in TIERS)
    lines.append(f"{counts} · **No action:** {plural(s['no_action'], 'account')} · **Stale deals:** {s['stale']}")
    lines += ["", "---", ""]

    for tier in TIERS:
        lines += [f"## {TIER_LABEL[tier]}", ""]
        if not tiers[tier]:
            lines += ["Nothing in this tier.", ""]
        for acct in tiers[tier]:
            lines.append(f"### {acct['account']}")
            multi = len(acct["opportunities"]) > 1
            for opp in acct["opportunities"]:
                parts, stale = opp_line(opp, report_date, stale_days)
                text = " · ".join(parts)
                if stale:
                    text += f" · **stale ({stale_days}+ days)**"
                lines.append((f"{opp['name']}: " if multi else "") + text + ("  " if multi else ""))
            lines.append("")
            for item in acct["items"]:
                lines += md_item(item, report_date)
            lines.append("")

    lines += ["## Internal and other", ""]
    if report.get("other_items"):
        for item in report["other_items"]:
            lines += md_item(item, report_date)
    else:
        lines.append("Nothing found.")
    lines += ["", "## Reviewed, no action", ""]
    if report.get("no_action"):
        for entry in report["no_action"]:
            lines.append(f"- **{entry['account']}:** {entry['note']}")
    else:
        lines.append("Every open opportunity has at least one action above.")
    if report.get("notes"):
        lines += ["", "## Notes", ""]
        lines += [f"- {note}" for note in report["notes"]]
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------- html

def e(text) -> str:
    return html.escape(str(text), quote=True)


def html_copy_block(label, text):
    return (
        f'<div class="block"><div class="block-head"><span>{e(label)}</span>'
        f'<button type="button" class="copy" data-copy="{e(text)}">Copy</button></div>'
        f"<pre>{e(text)}</pre></div>"
    )


def html_item(item, report_date, index):
    """One checklist row. Context and evidence go in the main column; anything to copy goes in the side column."""
    label, title = item_heading(item)
    meta_bits = "".join(f'<span class="chip">{e(bit)}</span>' for bit in item_meta(item, report_date))
    main = [f'<div class="chips">{meta_bits}</div>']
    side = []
    if item.get("detail"):
        main.append(f'<p class="detail">{e(item["detail"])}</p>')
    if "current" in item:
        current = item["current"] if item["current"] else "(empty)"
        main.append(f'<p class="current"><span>Current</span><code>{e(current)}</code></p>')
    email = item.get("email")
    if email:
        alts = f" Alternates: {e(', '.join(email['alternates']))}." if email.get("alternates") else ""
        main.append(
            f'<p class="recipient"><span>To</span><strong>{e(email["to"])}</strong> '
            f'&lt;{e(email["to_email"])}&gt;. {e(email["why"])}{alts}</p>'
        )
        main.append(
            f'<p class="recipient"><span>Resource</span>'
            f'<a href="{e(email["resource_link"])}">{e(email["resource_title"])}</a></p>'
        )
        side.append(html_copy_block("Subject", email["subject"]))
        side.append(html_copy_block("Body", email["body"]))
    if item.get("paste"):
        side.append(html_copy_block(f"Paste into {item['where']}", item["paste"]))
    main.append('<ul class="evidence">')
    for ev in item["evidence"]:
        soft = '<span class="soft">soft</span>' if ev.get("soft") else ""
        main.append(
            f'<li><span class="ev-src">{e(evidence_source(ev, report_date))}</span>'
            f'{soft} {e(ev["text"])}</li>'
        )
    main.append("</ul>")
    body_class = "item-body has-side" if side else "item-body"
    parts = [
        f'<li class="item type-{e(item["type"])}">',
        f'<label class="item-head"><input type="checkbox" data-key="item-{index}">',
        f'<span class="item-text"><span class="label">{e(label)}</span>',
        f'<span class="title">{e(title)}</span>' if title else "",
        "</span></label>",
        f'<div class="{body_class}"><div class="item-main">{"".join(main)}</div>',
        f'<div class="item-side">{"".join(side)}</div>' if side else "",
        "</div></li>",
    ]
    return "".join(parts)


def render_html(report, tiers, report_date, template, theme=("paper", "", "")):
    meta = report["meta"]
    s = stats(report, tiers)
    stale_days = meta["thresholds"]["stale_days"]
    counter = [0]

    def next_index():
        counter[0] += 1
        return counter[0]

    body = []
    if meta.get("mode") == "demo":
        body.append('<div class="banner">Demo: all data in this report is fictional.</div>')
    body.append('<header class="top">')
    body.append('<p class="eyebrow">Pipeline actions</p>')
    body.append(f"<h1>{e(long_date(report_date))}</h1>")
    opp_word = "open opportunity" if s["open_count"] == 1 else "open opportunities"
    body.append(
        f'<p class="sub">Prepared for {e(meta["prepared_for"])} · {s["open_count"]} {opp_word} · '
        f'{e(money(s["total"]))} open pipeline</p>'
    )
    body.append('<div class="tallies">')
    for tier in TIERS:
        body.append(
            f'<a class="tally tier-{tier}" href="#{tier}"><strong>{s["tier_counts"][tier]}</strong>'
            f"<span>{e(TIER_LABEL[tier])}</span></a>"
        )
    body.append(f'<div class="tally"><strong>{s["stale"]}</strong><span>Stale deals</span></div>')
    body.append(f'<div class="tally"><strong>{s["no_action"]}</strong><span>No action</span></div>')
    body.append("</div>")
    checked, missing = source_lines(meta)
    body.append(f'<p class="sources"><strong>Scope</strong> {e(meta["scope"])}</p>')
    body.append(f'<p class="sources"><strong>Checked</strong> {e(" · ".join(checked))}</p>')
    body.append(f'<p class="sources"><strong>Not checked</strong> {e(" · ".join(missing) if missing else "none")}</p>')
    body.append('<p class="progress"><span id="done-count">0</span> of <span id="total-count">0</span> done</p>')
    body.append("</header>")

    for tier in TIERS:
        body.append(f'<section class="tier tier-{tier}" id="{tier}">')
        body.append(f'<h2><span class="dot"></span>{e(TIER_LABEL[tier])}</h2>')
        if not tiers[tier]:
            body.append('<p class="empty">Nothing in this tier.</p>')
        for acct in tiers[tier]:
            body.append('<article class="card">')
            body.append(f"<h3>{e(acct['account'])}</h3>")
            multi = len(acct["opportunities"]) > 1
            for opp in acct["opportunities"]:
                parts, stale = opp_line(opp, report_date, stale_days)
                badge = f'<span class="stale">stale, {stale_days}+ days</span>' if stale else ""
                name = f"<strong>{e(opp['name'])}:</strong> " if multi else ""
                body.append(f'<p class="opp">{name}{e(" · ".join(parts))} {badge}</p>')
            body.append('<ul class="items">')
            for item in acct["items"]:
                body.append(html_item(item, report_date, next_index()))
            body.append("</ul></article>")
        body.append("</section>")

    body.append('<section class="tier tier-other" id="other"><h2><span class="dot"></span>Internal and other</h2>')
    if report.get("other_items"):
        body.append('<article class="card"><ul class="items">')
        for item in report["other_items"]:
            body.append(html_item(item, report_date, next_index()))
        body.append("</ul></article>")
    else:
        body.append('<p class="empty">Nothing found.</p>')
    body.append("</section>")

    body.append('<section class="tier tier-other"><h2><span class="dot"></span>Reviewed, no action</h2>')
    if report.get("no_action"):
        body.append('<ul class="plain">')
        for entry in report["no_action"]:
            body.append(f"<li><strong>{e(entry['account'])}:</strong> {e(entry['note'])}</li>")
        body.append("</ul>")
    else:
        body.append('<p class="empty">Every open opportunity has at least one action above.</p>')
    body.append("</section>")

    if report.get("notes"):
        body.append('<section class="tier tier-other"><h2><span class="dot"></span>Notes</h2><ul class="plain">')
        body += [f"<li>{e(note)}</li>" for note in report["notes"]]
        body.append("</ul></section>")

    title = f"Pipeline actions {md(report_date)}"
    report_id = f"pipeline-{meta['report_date']}-{meta['initials']}-{meta.get('mode', 'live')}"
    theme_name, theme_css, font_link = theme
    return (
        template.replace("{{TITLE}}", e(title))
        .replace("{{REPORT_ID}}", e(report_id))
        .replace("{{THEME_NAME}}", e(theme_name))
        .replace("{{FONT_LINK}}", font_link)
        .replace("{{THEME_CSS}}", theme_css)
        .replace("{{BODY}}", "\n".join(body))
    )


# ---------------------------------------------------------------- themes

THEME_NAME = re.compile(r"^[a-z0-9-]{1,40}$")
HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
FONT_FAMILY = re.compile(r"^[A-Za-z0-9 -]{1,40}$")
FONT_IMPORT = re.compile(r"^https://[A-Za-z0-9./?=&:;@+,%_~-]+$")
FONT_FALLBACK = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif'


def resolve_theme(meta, assets_dir):
    """Return (name, css, font_link, errors) for meta.theme.

    meta.theme is a theme name ("paper", "graphite", or any file in assets/themes/),
    or an object: {"name": "paper", "accent": "#0f766e", "font_family": "Inter",
    "font_import": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap"}.
    Every value is checked against a strict pattern because it is written into the page.
    """
    errors = []
    theme = meta.get("theme") or "paper"
    if isinstance(theme, str):
        theme = {"name": theme}
    name = theme.get("name", "paper")
    if not THEME_NAME.match(str(name)):
        return "paper", "", "", [f"meta.theme: '{name}' is not a valid theme name"]
    path = assets_dir / "themes" / f"{name}.css"
    if not path.exists():
        available = ", ".join(sorted(f.stem for f in (assets_dir / "themes").glob("*.css"))) or "none found"
        return "paper", "", "", [f"meta.theme: no theme named '{name}' (available: {available})"]
    css = path.read_text(encoding="utf-8")
    overrides = []
    accent = theme.get("accent")
    if accent:
        if HEX_COLOR.match(accent):
            overrides.append(f"--accent: {accent};")
        else:
            errors.append("meta.theme.accent must be a six-digit hex color such as #0f766e")
    family = theme.get("font_family")
    if family:
        if FONT_FAMILY.match(family):
            overrides.append(f'--font: "{family}", {FONT_FALLBACK};')
        else:
            errors.append("meta.theme.font_family may contain only letters, digits, spaces, and hyphens")
    font_link = ""
    font_import = theme.get("font_import")
    if font_import:
        if FONT_IMPORT.match(font_import):
            font_link = f'<link rel="stylesheet" href="{html.escape(font_import, quote=True)}">\n'
        else:
            errors.append("meta.theme.font_import must be an https URL to a font stylesheet")
    if overrides:
        css += f"\nhtml.theme-{name} {{ " + " ".join(overrides) + " }\n"
    return name, css, font_link, errors


# ---------------------------------------------------------------- main

def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate and render a pipeline report.")
    parser.add_argument("report", help="Path to the report JSON")
    parser.add_argument("--out-dir", default=".", help="Folder for the rendered files")
    parser.add_argument("--basename", help="File name without extension (default pipeline-actions-YYYY-MM-DD)")
    parser.add_argument("--no-html", action="store_true", help="Write markdown only")
    parser.add_argument("--check", action="store_true", help="Validate only, write nothing")
    parser.add_argument("--template", help="HTML template (default ../assets/report-template.html)")
    args = parser.parse_args(argv)

    try:
        report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read {args.report}: {exc}", file=sys.stderr)
        return 2

    errors, report_date = validate(report)
    template_path = Path(args.template) if args.template else Path(__file__).resolve().parent.parent / "assets" / "report-template.html"
    theme_name, theme_css, font_link, theme_errors = resolve_theme(report.get("meta") or {}, template_path.parent)
    errors += theme_errors
    if errors:
        print(f"{len(errors)} problem(s) to fix before this report can be built:\n", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    tiers = organize(report, report_date)
    s = stats(report, tiers)
    tier_summary = ", ".join(TIER_LABEL[t].lower() + " " + str(s["tier_counts"][t]) for t in TIERS)
    summary = (
        f"OK: {s['items']} items across {sum(s['tier_counts'].values())} accounts "
        f"({tier_summary}), {s['stale']} stale, {s['no_action']} no action."
    )
    if args.check:
        print(summary)
        return 0

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = args.basename or f"pipeline-actions-{report['meta']['report_date']}"
    md_path = out_dir / f"{base}.md"
    md_path.write_text(render_markdown(report, tiers, report_date), encoding="utf-8")
    written = [str(md_path)]
    if not args.no_html:
        if not template_path.exists():
            print(f"HTML template not found at {template_path}. Markdown was written; use --no-html to skip HTML.", file=sys.stderr)
            return 2
        html_path = out_dir / f"{base}.html"
        html_path.write_text(render_html(report, tiers, report_date, template_path.read_text(encoding="utf-8"), (theme_name, theme_css, font_link)), encoding="utf-8")
        written.append(str(html_path))
    print(summary)
    for path in written:
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
