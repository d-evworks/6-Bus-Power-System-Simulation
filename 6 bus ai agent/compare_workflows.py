"""
Main entry point: runs the 6-bus network + 4 N-1 contingency scenarios, then
generates BOTH the traditional (raw numeric) report and the AI-agent-assisted
report from the SAME underlying simulation results, times each, and writes
both to results/ for side-by-side comparison.

This directly mirrors the responsibility described in the Dassault Systemes
SIMULIA "Working Student - AI-Powered Research on Electromagnetic Simulation"
posting: "test the AI agent's performance ... by comparing traditional
simulation workflows with AI-enhanced processes, measuring improvements in
efficiency, accuracy, and user satisfaction."
"""
import os
from contingency import run_all_scenarios
from ai_agent import traditional_report, ai_agent_report, timed

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("Running Newton-Raphson load flow: baseline + 4 N-1 contingency scenarios...")
    results = run_all_scenarios()

    trad_text, trad_time = timed(traditional_report, results)
    ai_text, ai_time = timed(ai_agent_report, results)

    with open(os.path.join(RESULTS_DIR, "traditional_report.md"), "w") as f:
        f.write(trad_text)
    with open(os.path.join(RESULTS_DIR, "ai_agent_report.md"), "w") as f:
        f.write(ai_text)

    mode = "LLM (Claude)" if os.environ.get("ANTHROPIC_API_KEY") else "rule-based fallback"
    summary = f"""# Workflow Comparison Summary

AI-agent mode used: **{mode}**

| Metric | Traditional Workflow | AI-Agent Workflow |
|---|---|---|
| Generation time | {trad_time:.4f}s | {ai_time:.4f}s |
| Output format | Raw numeric tables per scenario | Prioritized natural-language risk summary + recommendations |
| Requires manual interpretation | Yes | No |
| Actionable recommendations included | No | Yes |

Both reports were generated from the *identical* simulation output
(`run_all_scenarios()` in `contingency.py`) - only the reporting layer differs.
See `traditional_report.md` and `ai_agent_report.md` for full output.
"""
    with open(os.path.join(RESULTS_DIR, "comparison_summary.md"), "w") as f:
        f.write(summary)

    print(summary)
    print(f"Full reports written to {RESULTS_DIR}/")


if __name__ == "__main__":
    main()
