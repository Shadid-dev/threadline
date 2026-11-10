# Ahmed Hantoor: Change Attributor

**Your agent's job:** find which recent code change (deploy or commit) most likely caused the incident, and back it up with evidence (signal IDs). It suggests; a human decides.

**Planned design (from the group spec, Section 4.3):** an LLM with tools `get_recent_deploys(service, since)` and `get_commit_diff(commit_id)`. It ranks at most 3 candidates by (1) deploy before the first error and (2) the crashing file appears in the change. It returns an empty list instead of guessing.

## Please upload to `labs/`
- [ ] Lab 2: your Change Attributor prompt contract
- [ ] Lab 3: your tool-using agent (code + report)
- [ ] Lab 4: your multi-agent work (code + report)

## Next steps
See `docs/team-roles-and-next-steps.md`, Section 4 (Ahmed).
