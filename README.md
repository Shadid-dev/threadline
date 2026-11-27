# ThreadLine

**INSE 691 (Foundations of AI Agent Systems), Fall 2026, Concordia University. Team project.**

When software breaks, the evidence is scattered: a code release on GitHub, a crash in Sentry, an alert from the monitor, a customer ticket in Jira, worried messages in Slack. ThreadLine collects all of those signals into **one shared record per incident, called a thread**. Then a small team of AI agents reads that thread, writes a summary in which every sentence points back to its evidence, and proposes a next step. **Nothing is ever done without a human approving it.**

> New here? Read this page top to bottom (5 minutes). Then open the guide for your own role in [`team/`](team/).

---

## 1. Where the project stands (November 26 2026)

| Part | Status |
|---|---|
| Correlator (groups signals into threads) | Working |
| Narrator (cited summary) | Simple version working in the prototype; full version built and tested by Anirudh (68 tests) |
| Grounding Validator (checks the summary) | Working in the prototype |
| Action Drafter (proposes a next step) | Simple version working in the prototype; full version built and tested by Kameshwar |
| Supervisor (decides which agent runs next) | Working (static and dynamic modes) |
| Change Attributor (finds the code change that caused it) | Built and tested by Ahmed as a separate prototype; not yet connected |
| Connecting all agents into one pipeline | Next step |
| Source adapters / MCP server, database, dashboard, evaluation | Not started |
| Design specification (group submission) | First draft, updated with every member's Lab 2–5 work: [`docs/design-spec/`](docs/design-spec/) |

The full plan, with who does what next, is in **[docs/team-roles-and-next-steps.md](docs/team-roles-and-next-steps.md)**.

---

## 2. Start here (in this order)

1. **[docs/how-to-use-github-desktop.md](docs/how-to-use-github-desktop.md)**: how to download this project, upload your files and share changes. No command line needed.
2. **[docs/team-roles-and-next-steps.md](docs/team-roles-and-next-steps.md)**: who owns which agent, what is finished, what each person does next.
3. **Your own folder in [`team/`](team/)**: what to upload and what your agent must do.
4. **[docs/design-spec/](docs/design-spec/)**: the group design document (Word + PDF). Check the section about your agent.

---

## 3. What is in this repository

```
threadline/
├── README.md                  ← you are here
├── docs/                      ← documents to READ
│   ├── how-to-use-github-desktop.md
│   ├── team-roles-and-next-steps.md
│   ├── design-spec/           ← group design specification (Word + PDF)
│   ├── proposal/              ← our approved project proposal (PDF)
│   └── ThreadLine_Team_Starter_Guide.pdf
├── team/                      ← one folder per person: UPLOAD your work here
│   ├── ahmed-hantoor_change-attributor/
│   ├── anirudh-parole-preeth_narrator/
│   ├── afsana-tasnim-nishat_grounding-validator/
│   ├── kameshwar-arora_action-drafter/
│   └── shadid-alam-al-huda_correlator/
├── lab4/                      ← CURRENT PROTOTYPE: 4 agents + supervisor, tests, traces
├── lab3_correlator/           ← earlier one-agent version (Correlator with tools)
└── utilities/                 ← small helper scripts (check your Gemini key, list models)
```

**Rule of thumb:** read in `docs/`, upload in `team/<your-folder>/`, and leave `lab4/` and `lab3_correlator/` to their owners unless the team agrees on a change.

---

## 4. Run the prototype (optional)

Open the `threadline` folder in VS Code, then **Terminal → New Terminal**, and paste:

```sh
python3 -m lab4.run --mode dynamic
python3 -m unittest lab4.test_system lab4.test_concordia
```

You should see nine scenario lines (for example `attach attach awaiting_approval`) and then `Ran 18 tests ... OK`. This needs no API key. Using a real AI model (Gemini or Concordia's Qwen) is explained in [lab4/README.md](lab4/README.md).

The very first version, which shows the core idea in 50 lines with no AI at all:

```sh
python3 lab3_correlator/correlator.py
```

It prints `Found 2 threads`: six checkout signals in one incident and two login signals in another.

---

## 5. Team

| Member | Agent owned | Other responsibility |
|---|---|---|
| Ahmed Hantoor | Change Attributor | Test data, source adapters, MCP server |
| Anirudh Parole Preeth | Narrator | Supervisor routing and integration |
| Afsana Tasnim Nishat | Grounding Validator | Approval dashboard, documentation |
| Kameshwar Arora | Action Drafter | Safety tests, evaluation, CartNow demo shop |
| Shadid Alam Al Huda | Correlator | Prototype integration, repository |

---

## 6. Three rules

1. **Never upload a `.env` file, an API key or a password.** The `.gitignore` file already blocks `.env`, but check the file list before every commit.
2. **Always click Fetch origin, then Pull, before you start working**, so you have everyone's latest files.
3. **All data is invented (synthetic).** Never put real customer or company data in this repository.
