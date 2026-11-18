# Demo mode

The demo runs the full workflow against fictional data in the `demo/` folder, so someone can see what the skill produces before connecting anything. All of it is invented.

## The setup

The demo seller is Riley Bennett, a partner account manager at Pellmoor, a fictional company that sells backup and disaster recovery through managed service providers (MSPs). Riley has eight open opportunities across eight MSP partners.

The scenario is one example. Nothing in the skill itself is specific to MSPs, backup, or channel sales.

| File | Stands in for |
| --- | --- |
| `demo/config.md` | The saved config from setup |
| `demo/crm.json` | The CRM: opportunities, contact roles, logged activities |
| `demo/emails.json` | Riley's inbox and sent mail |
| `demo/calls.json` | The call recorder: summaries and transcripts |
| `demo/calendar.json` | The calendar |
| `demo/chat.json` | Chat: direct messages and shared channels |
| `demo/library/` | The resource library, one file per document |

## How to run it

1. Read `demo/config.md` and use it as the config. Skip setup.
2. Treat today as the `demo_today` date in that config (Tuesday, November 17, 2026). All day counts are measured from that date, so the output is the same on every run.
3. Follow the normal run workflow in `SKILL.md` from step 1, reading the fixture files wherever the workflow says to query a tool. Preflight is simply confirming each file opens.
4. Set `"mode": "demo"` in the report data so the report is labeled as demo data, and `"theme": "midnight"` as the demo config specifies.
5. Apply every rule exactly as in a real run: evidence rules, the stale check, the resource fit test, the sweep filters, and the length caps. The data includes cases that are easy to get wrong on purpose, such as an out-of-office reply, a hedged statement from a partner, and a resource that matches on company size but not on anything the partner said.

Do not look in the repository's `examples/` folder while producing a demo report. It holds a finished sample for readers and reading it would defeat the purpose of the run.

## After the demo

Tell the user the report came from fictional data and offer to run setup against their own tools.
