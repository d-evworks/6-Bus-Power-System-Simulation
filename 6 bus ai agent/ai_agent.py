"""
Two report-generation "workflows" over the same simulation results:

1. traditional_report()  - what an engineer manually reading pandapower's raw
   output tables would produce: a plain numeric dump, no interpretation.
2. ai_agent_report()      - an AI-agent-assisted workflow: interprets the same
   numbers, flags risk, and proposes mitigations in natural language.
   Uses the Claude API if ANTHROPIC_API_KEY is set in the environment,
   otherwise falls back to a rule-based agent so the demo always runs
   standalone with no API key required.

This mirrors the comparison described in the Dassault Systemes SIMULIA
"Working Student - AI-Powered Research on Electromagnetic Simulation" role:
testing an AI agent's performance against a traditional workflow by measuring
efficiency, accuracy, and how much manual interpretation it saves the engineer.
"""
import os
import time


def traditional_report(results: dict) -> str:
    """Simulates the manual workflow: raw tables, no synthesis, no prioritization."""
    lines = ["# Traditional Workflow Output (raw results)\n"]
    for scenario, r in results.items():
        lines.append(f"## {scenario}")
        lines.append(f"- Converged: {r['converged']}")
        lines.append(f"- Min voltage (pu): {r['min_voltage_pu']}")
        lines.append(f"- Max voltage (pu): {r['max_voltage_pu']}")
        lines.append(f"- Weak buses (outside 0.95-1.05 pu): {r['weak_buses']}")
        lines.append(f"- Max line loading (%): {r['max_line_loading_pct']}")
        lines.append(f"- Overloaded lines (>100%): {r['overloaded_lines']}")
        lines.append(f"- Total active losses (MW): {r['total_active_losses_mw']}")
        lines.append("")
    lines.append(
        "\n*(An engineer must manually read every scenario above, cross-reference "
        "thresholds themselves, and decide what's actionable. No prioritization or "
        "recommendations are provided by this workflow.)*"
    )
    return "\n".join(lines)


def _rule_based_agent_summary(results: dict) -> str:
    """Fallback 'agent': a small rules engine that mimics what an LLM agent
    would flag and recommend, without requiring an API key."""
    out = ["# AI-Agent Workflow Output (rule-based fallback mode)\n"]
    baseline = results["Baseline"]
    out.append(
        f"Baseline network is healthy: voltages stay within "
        f"{baseline['min_voltage_pu']}-{baseline['max_voltage_pu']} pu and losses "
        f"are {baseline['total_active_losses_mw']} MW.\n"
    )

    for scenario, r in results.items():
        if scenario == "Baseline":
            continue
        risk_notes = []
        if r["weak_buses"]:
            names = ", ".join(b for b, v in r["weak_buses"])
            risk_notes.append(f"voltage violations at {names}")
        if r["overloaded_lines"]:
            names = ", ".join(l for l, p in r["overloaded_lines"])
            risk_notes.append(f"line overloads on {names}")
        loss_delta_pct = round(
            100 * (r["total_active_losses_mw"] - baseline["total_active_losses_mw"])
            / baseline["total_active_losses_mw"], 1
        )

        out.append(f"## {scenario}")
        if risk_notes:
            out.append(f"**Risk detected:** {'; '.join(risk_notes)}.")
        else:
            out.append("**Risk detected:** none - network remains within limits.")
        out.append(f"Losses shift {loss_delta_pct:+.1f}% vs. baseline.")

        if r["weak_buses"]:
            out.append(
                "Recommendation: deploy local reactive power compensation "
                "(capacitor bank or BESS in Q-support mode) at the affected bus(es) "
                "to pull voltage back within limits."
            )
        if r["overloaded_lines"]:
            out.append(
                "Recommendation: reconfigure network topology or reinforce the "
                "overloaded feeder(s); consider curtailing non-critical load during "
                "this contingency."
            )
        out.append("")

    out.append(
        "\n*(Generated automatically by a rules-based agent. Set ANTHROPIC_API_KEY "
        "to switch to full LLM-generated narrative analysis instead.)*"
    )
    return "\n".join(out)


def _llm_agent_summary(results: dict) -> str:
    """Real LLM-powered agent, used automatically if ANTHROPIC_API_KEY is set."""
    import anthropic

    client = anthropic.Anthropic()
    prompt = f"""You are an AI agent assisting a power systems engineer who just ran
a Newton-Raphson load flow on a 6-bus meshed network across a baseline case and four
N-1 contingency scenarios (load +20%, line impedance +30%, PV removal, combined
stress). Here is the structured simulation output:

{results}

Write a concise engineering summary (under 300 words) that:
1. States whether each scenario is safe or at risk (voltage limits 0.95-1.05 pu, line loading under 100%)
2. Highlights the most severe scenario and why
3. Proposes concrete mitigation strategies (e.g. reactive power compensation, network reconfiguration)
Write it the way a colleague would explain it in a stand-up, not a raw data dump."""

    msg = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    return "# AI-Agent Workflow Output (Claude-generated)\n\n" + msg.content[0].text


def ai_agent_report(results: dict) -> str:
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return _llm_agent_summary(results)
        except Exception as e:
            return (
                f"*(LLM call failed: {e} - falling back to rule-based agent)*\n\n"
                + _rule_based_agent_summary(results)
            )
    return _rule_based_agent_summary(results)


def timed(fn, *args):
    start = time.perf_counter()
    output = fn(*args)
    elapsed = time.perf_counter() - start
    return output, elapsed
