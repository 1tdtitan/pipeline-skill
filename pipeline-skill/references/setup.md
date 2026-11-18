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
