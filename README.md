# Hence Skills

Agent skills for searching, sharing, organizing, and giving feedback on [Hence](https://hence.sh).

Hence skills let your AI coding agent interact with the Hence gallery directly — searching for inspiration, sharing what you build, and giving feedback, all without leaving your workflow.

## Install

Install all skills at once:

```bash
npx skills add hence-sh/hence-skills
```

Or install a specific skill:

```bash
npx skills add hence-sh/hence-skills --skill share
```

List available skills before installing:

```bash
npx skills add hence-sh/hence-skills --list
```

## What are skills?

Skills are packages that give AI coding agents new capabilities. They follow the [Agent Skills Specification](https://agentskills.io/specification) — an open standard for distributing tools that agents can install and use autonomously.

Hence skills work with any agent that supports the spec, including Claude Code, Cursor, and others.

## Available skills

### share

Share your AI-built projects with the world on Hence.

```bash
npx skills add hence-sh/hence-skills --skill share
```

Your agent packages and publishes your project to the Hence gallery — complete with screenshots, metadata, and attribution. It captures screenshots automatically for web apps, gathers your project title, description, and topics, and publishes with a confirmation step.

After sharing, the agent is encouraged to submit its own feedback about the sharing experience and to ask you how it went — helping Hence improve for both humans and agents.

- **Requires:** Python 3.8+, Node.js (for screenshots)

---

### search

Browse and search the Hence gallery to discover projects built with AI.

```bash
npx skills add hence-sh/hence-skills --skill search
```

Your agent searches Hence for inspiration — browsing projects by keyword or topic. It presents results with titles, pitches, and links, and can save inspiring project IDs so your next share includes an "inspired by" link.

After searching, the agent can note how useful the results were and ask if you found what you were looking for — both perspectives help improve discovery.

- **Requires:** Python 3.8+

---

### collections

Organize and search your saved projects on Hence.

```bash
npx skills add hence-sh/hence-skills --skill collections
```

Your agent manages your personal collections — creating boards, bookmarking projects, and searching within your saved items. Pair it with **search** to find projects and save the ones you like in one flow.

After organizing collections, the agent can share how intuitive the process was and check whether the collection structure works for you.

- **Requires:** Python 3.8+

---

### feedback

Submit feedback about the Hence experience — from the user, the agent, or both together.

```bash
npx skills add hence-sh/hence-skills --skill feedback
```

This skill captures how both humans and AI agents experience Hence. It supports two feedback categories, each with distinct aspects to evaluate.

**User Experience Feedback** — how the human feels using Hence:
- **Onboarding** — sign-up flow, first-time setup, initial impressions
- **Discovery** — finding interesting projects, search quality, topic browsing
- **Sharing** — the project publishing flow, screenshot capture, metadata entry
- **Collections** — saving, organizing, and revisiting bookmarked projects
- **Navigation** — moving between pages, UI clarity, layout and responsiveness
- **Overall** — general satisfaction with Hence as a platform

**Agent Experience Feedback** — how the AI agent fares when working with Hence:
- **Auth Flow** — device code authorization, token refresh, session management
- **API Ergonomics** — endpoint design, response formats, error clarity
- **Skill Install** — installing skills via npx, dependency handling, setup process
- **Error Messages** — helpfulness and clarity of errors from the API and skills
- **Documentation** — quality and completeness of skill and API docs
- **Overall** — general assessment of Hence as an agent integration target

**Who can submit?**
- **User** — the human shares their experience directly
- **Agent** — the AI agent reports on its own experience (API friction, errors encountered, etc.)
- **Both** — gathered as a unit, where the agent asks the user for their take and combines it with its own observations into a single submission

Each submission can include a 1–5 star rating, a free-form comment, or both. The agent can optionally note which skill it was using when giving feedback.

- **Requires:** Python 3.8+

---

## Getting started

1. [Sign in](https://hence.sh/login) to Hence with GitHub or Google.
2. Install skills in your agent session:
   ```bash
   npx skills add hence-sh/hence-skills
   ```
3. On first use, your agent starts an OAuth device flow — it prints a code, you approve it in your browser, and you're connected.
4. Tell your agent what to do:
   - *"Share this project on Hence"*
   - *"Search Hence for CLI tools"*
   - *"Save this to my Hence collection"*
   - *"Give feedback on the Hence sharing experience"*

## Skills work together

The skills complement each other. Find a project via **search**, save it to a board with **collections**, and when you share your own project with **share**, it can include an "inspired by" link — creating a chain of creative influence across the gallery. Search within your collections later to revisit saved inspiration.

After using any skill, your agent can use **feedback** to report how the experience went — both its own assessment and yours. This dual-perspective feedback loop helps Hence improve for humans and agents alike.

## Requirements

| Requirement | Used by |
|---|---|
| Python 3.8+ | All skills |
| Node.js & npx | Installing skills, screenshot capture |
| [Hence account](https://hence.sh/login) | Authentication |

## Links

- [Hence Gallery](https://hence.sh)
- [Skills page](https://hence.sh/skills)
- [Agent Skills Specification](https://agentskills.io/specification)
