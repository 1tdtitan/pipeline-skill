# Pipeline skill config (demo)

Fictional config for the demo run. In a real setup the wizard writes this file.

last_updated: 2026-11-17
demo_today: 2026-11-17 (Tuesday)

## User

- name: Riley Bennett
- initials: RB
- signs_emails_as: Riley
- email_addresses: riley.bennett@pellmoor.example
- company: Pellmoor
- company_email_domains: pellmoor.example

## Sources

| Role | Tool | Status | Notes |
| --- | --- | --- | --- |
| CRM | demo/crm.json | connected | Stands in for a CRM connector |
| Email | demo/emails.json | connected | Inbox and sent mail |
| Calendar | demo/calendar.json | connected | |
| Call recorder | demo/calls.json | connected | Summaries and transcript excerpts |
| Chat | demo/chat.json | connected | Direct messages and shared channels |
| Resource library | demo/library/ | connected | Index in demo/library/index.md |

## Scope

- owner: Riley Bennett
- stages: all open
- close_dates: any
- other_filters: none
- context_days: 90

## CRM fields

- next_step_field: Next Step
- next_step_char_limit: 255
- critical_fields: Amount, Close Date
- date_format: M/D
- next_call_line: yes
- counterparty_label: Partner (Pellmoor sells through MSPs and calls them partners)

## Thresholds

- stale_days: 14
- sweep_days: 14
- chase_business_days: 3

## Output

- save_reports_to: working folder
- html_version: yes
- theme: midnight

## Resource index

See `demo/library/index.md`. Read each document before recommending it.
