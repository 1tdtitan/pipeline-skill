#!/usr/bin/env python3
"""Check the sample report against the demo fixtures.

This recomputes, straight from the fixture files, the facts the sample report
depends on, and fails if the two disagree:

  1. Last two-way contact date for every account
  2. Every quoted piece of evidence appears word for word in a fixture
  3. Every open opportunity is accounted for, and the pipeline total matches
  4. Every suggested contact role is missing from the CRM and present in the data
  5. Each re-engagement email only mentions resource sections that exist

Run from the repository root:
    python tools/check_demo.py
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "pipeline-skill" / "demo"
REPORT = ROOT / "examples" / "sample-report.json"

SYSTEM_SUBJECT = re.compile(r"^(automatic reply|accepted|declined|tentative|out of office)\b", re.I)


def load(name):
    return json.loads((DEMO / name).read_text(encoding="utf-8"))


def addr(field: str) -> str:
    m = re.search(r"<([^>]+)>", field)
    return (m.group(1) if m else field).strip().lower()


def main() -> int:
    crm, emails, calls, chat = load("crm.json"), load("emails.json"), load("calls.json"), load("chat.json")
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    problems = []

    # ---- 1. last two-way contact, derived from fixtures
    derived = {}
    for opp in crm["opportunities"]:
        domain, account = opp["account_domain"], opp["account"]
        dates = []
        for msg in emails["messages"]:
            sender = addr(msg["from"])
            if sender.endswith("@" + domain) and not SYSTEM_SUBJECT.match(msg["subject"]):
                dates.append(date.fromisoformat(msg["date"][:10]))
        for call in calls["calls"]:
            if any(a["email"].lower().endswith("@" + domain) for a in call["attendees"]):
                dates.append(date.fromisoformat(call["date"]))
        for msg in chat["messages"]:
            if f"({account})" in msg["from"]:
                dates.append(date.fromisoformat(msg["date"][:10]))
        for act in opp["activities"]:
            if act["type"] in ("Call", "Meeting"):
                dates.append(date.fromisoformat(act["date"]))
        derived[account] = max(dates) if dates else None

    reported = {}
    for acct in report["accounts"]:
        for opp in acct["opportunities"]:
            reported[acct["account"]] = opp["last_two_way"]["date"]
    for account, value in reported.items():
        want = derived.get(account)
        if want is None or value != want.isoformat():
            problems.append(f"last two-way contact for {account}: report says {value}, fixtures say {want}")

    # ---- 2. quoted evidence appears in the fixtures
    corpus_parts = [m["body"] for m in emails["messages"]]
    corpus_parts += [line["text"] for c in calls["calls"] for line in c["transcript"]]
    corpus_parts += [m["text"] for m in chat["messages"]]
    corpus = " ".join(" ".join(part.split()) for part in corpus_parts).lower()

    def all_items():
        for acct in report["accounts"]:
            for item in acct["items"]:
                yield acct["account"], item
        for item in report["other_items"]:
            yield "other", item

    quotes = 0
    for account, item in all_items():
        for ev in item["evidence"]:
            for quote in re.findall(r"\"([^\"]+)\"", ev["text"]):
                clean = re.sub(r"\s*\[[^\]]*\]", "", quote)
                clean = " ".join(clean.split()).lower()
                quotes += 1
                if clean not in corpus:
                    problems.append(f"{account}: quote not found in fixtures: {quote!r}")
    for note in report["notes"]:
        for quote in re.findall(r"\"([^\"]+)\"", note):
            quotes += 1
            if " ".join(quote.split()).lower() not in corpus:
                problems.append(f"notes: quote not found in fixtures: {quote!r}")

    # ---- 3. coverage and totals
    covered = set(reported) | {e["account"] for e in report["no_action"]}
    for opp in crm["opportunities"]:
        if opp["account"] not in covered:
            problems.append(f"{opp['account']} is in the CRM but not in the report")
    crm_total = sum(o["amount"] or 0 for o in crm["opportunities"])
    report_total = sum(o["amount"] or 0 for a in report["accounts"] for o in a["opportunities"])
    report_total += sum(e.get("amount") or 0 for e in report["no_action"])
    if crm_total != report_total:
        problems.append(f"pipeline total: CRM {crm_total}, report {report_total}")
    for acct in report["accounts"]:
        for opp in acct["opportunities"]:
            match = next(o for o in crm["opportunities"] if o["name"] == opp["name"])
            for key in ("amount", "stage", "close_date"):
                if match[key] != opp[key]:
                    problems.append(f"{opp['name']}: {key} is {opp[key]!r} in the report, {match[key]!r} in the CRM")
        for item in acct["items"]:
            if item["type"] == "next_step":
                match = next(o for o in crm["opportunities"] if o["account"] == acct["account"])
                if match["next_step"] != item["current"]:
                    problems.append(f"{acct['account']}: 'current' Next Step does not match the CRM")

    # ---- 4. contact roles
    all_addresses = set()
    for msg in emails["messages"]:
        for field in [msg["from"], *msg["to"], *msg["cc"]]:
            all_addresses.add(addr(field))
    for acct in report["accounts"]:
        roles = {r["email"].lower() for o in crm["opportunities"] if o["account"] == acct["account"] for r in o["contact_roles"]}
        for item in acct["items"]:
            if item["type"] == "contact_role":
                email = item["paste"].split("\n")[-1].strip().lower()
                if email in roles:
                    problems.append(f"{acct['account']}: {email} is already a contact role")
                if email not in all_addresses:
                    problems.append(f"{acct['account']}: {email} does not appear in any email")

    # ---- 5. resource sections named in email drafts exist in the resource
    library = {p.name: p.read_text(encoding="utf-8") for p in (DEMO / "library").glob("*.md")}
    index = library["index.md"]
    for account, item in all_items():
        email = item.get("email")
        if not email:
            continue
        row = next((line for line in index.splitlines() if email["resource_link"] in line), None)
        if not row:
            problems.append(f"{account}: resource link is not in the library index")
            continue
        doc = library[re.search(r"`([^`]+)`", row).group(1)]
        for section in re.findall(r"\"([^\"]+)\"", email["body"]):
            if f"## {section}" not in doc:
                problems.append(f"{account}: email names a section {section!r} that the resource does not have")

    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(
        f"Sample report matches the fixtures: {len(reported)} last-contact dates, {quotes} quotes, "
        f"{len(crm['opportunities'])} opportunities, ${crm_total:,} pipeline total."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
