# Workflow Comparison Summary

AI-agent mode used: **rule-based fallback**

| Metric | Traditional Workflow | AI-Agent Workflow |
|---|---|---|
| Generation time | 0.0001s | 0.0000s |
| Output format | Raw numeric tables per scenario | Prioritized natural-language risk summary + recommendations |
| Requires manual interpretation | Yes | No |
| Actionable recommendations included | No | Yes |

Both reports were generated from the *identical* simulation output
(`run_all_scenarios()` in `contingency.py`) - only the reporting layer differs.
See `traditional_report.md` and `ai_agent_report.md` for full output.
