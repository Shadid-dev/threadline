# Shadid Alam Al Huda: Correlator

**My agent's job:** decide which incident (thread) each new signal belongs to. Rule: same service, and at most 30 minutes after the thread's last activity, otherwise open a new thread. A signal with no service opens a thread marked for human review. Text inside a signal is never treated as an instruction.

## My work so far (for teammates who want to understand it)

| Lab | What it is | Where |
|---|---|---|
| Lab 2 | Correlator prompt contract | `labs/INSE691_Lab2_40334643.pdf` |
| Lab 3 | Correlator with 5 custom tools + Gemini code execution | `lab3_correlator/` (report: `lab3_correlator/REPORT.pdf`) |
| Lab 4 | Full prototype: 4 agents + supervisor, static/dynamic orchestration, 9 scenarios, 18 tests | `lab4/` (report: `lab4/REPORT.pdf`) |
| Lab 5 | Design review of my Lab 4 prototype (by Sohana and Ishavjot) | `labs/Lab5_FDR_Report_Shadid_ThreadLine.docx` |

**Where to start reading the code:** `lab4/system.py`. Each agent is one class (`Correlator`, `Narrator`, `GroundingValidator`, `ActionDrafter`), and `Orchestrator` is the supervisor that decides what runs next.

## Next steps
See `docs/team-roles-and-next-steps.md`, Section 4 (Shadid).
