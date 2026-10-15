# AI-Assisted Reporting for Power-Flow Studies

A small side experiment: run the same pandapower load-flow study twice and
compare two ways of reporting it. One is the usual raw tables you read by
hand, the other is an "agent" layer that interprets the numbers, flags risks
and suggests mitigations. I wanted to see how much interpretation work that
saves, and whether the conclusions stay correct.

## What it does

1. Builds a 6-bus meshed 20 kV network in **pandapower**: 4 load buses
   (2.0 MW total), one 0.8 MW conventional generator and 500 kW of solar PV
   (25 % of load at baseline), 7 lines including a cross-brace so a single
   line outage doesn't island the network. It is a smaller 20 kV
   variant of the 110 kV network in the main project one folder up.
2. Runs a **Newton-Raphson load flow** for a baseline case plus four stress
   scenarios (not N-1 outages): load +20%, line impedance +30% (aged conductors),
   PV removal (solar outage), and combined stress.
3. Generates **two reports from the identical simulation output**:
   - `traditional_report.md` — a raw numeric dump, the way you'd read
     pandapower's output tables by hand. No interpretation, no prioritization.
   - `ai_agent_report.md` — an AI-agent-style workflow that interprets the same
     numbers, flags which scenarios are actually at risk (voltage violations,
     line overloads), quantifies the loss impact, and proposes concrete
     mitigations (reactive power compensation, network reconfiguration).
4. Writes a side-by-side comparison (`comparison_summary.md`) — generation time,
   output format, and how much manual interpretation each workflow still
   requires.

The AI-agent layer runs in one of two modes:
- **Rule-based fallback** (default, no setup required) — a small rules engine
  that flags thresholds and recommends mitigations, so the demo always runs
  standalone.
- **LLM-powered** (set the `ANTHROPIC_API_KEY` environment variable) — calls
  Claude to generate the same risk analysis as natural-language prose instead
  of templated text. Falls back automatically to rule-based mode if the API
  call fails for any reason.

## Why the network is built this way

The first version of this network was too electrically "stiff" — a
voltage-controlled generator bus and short lines meant every contingency
scenario converged safely with no violations, which made for a boring (and
dishonest) demo. I deliberately re-tuned it — longer feeder lengths, a
fixed-output (non-voltage-regulated) generator, tighter cable ratings — so that
the **Combined Stress** scenario produces genuine overloaded lines (~102–108%
loading) and a 3x rise in losses versus baseline. That's the point: the AI
agent needs something real to catch, or the comparison is meaningless.

## Running it

```bash
pip install -r requirements.txt
python compare_workflows.py
```

Outputs are written to `results/`. To use the LLM-powered agent instead of the
rule-based fallback:

```bash
export ANTHROPIC_API_KEY="your-key-here"
python compare_workflows.py
```

## Files

| File | Purpose |
|---|---|
| `network.py` | Builds the 6-bus meshed pandapower network |
| `contingency.py` | Runs baseline + 4 stress scenarios, extracts risk metrics |
| `ai_agent.py` | Traditional vs. AI-agent report generation (LLM or rule-based) |
| `compare_workflows.py` | Ties it together, times both workflows, writes `results/` |

## Next steps if this goes further

- Swap the rule-based fallback's thresholds for a proper anomaly-detection
  model trained on a wider scenario sweep.
- Extend `ai_agent.py` to also *propose* which additional contingency
  scenarios are worth testing next, not just summarize the ones already run —
  closer to an autonomous agent than a report generator.
- Add a real N-1 loop (each line out of service in turn) like in my
  [Netzplanung project](https://github.com/d-evworks/Netzplanung-hosting-capacity).
