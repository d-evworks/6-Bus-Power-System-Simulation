# AI-Agent-Assisted Power System Contingency Analysis

A small demo built to directly mirror the responsibilities in Dassault Systèmes'
**"Working Student (m/f/d) – AI-Powered Research on Electromagnetic Simulation"**
(SIMULIA Electromagnetics, Darmstadt) posting — specifically this line from the JD:

> "You will test the AI agent's performance on 3DEXPERIENCE by comparing
> traditional simulation workflows with AI-enhanced processes, measuring
> improvements in efficiency, accuracy, and user satisfaction."

This project runs that exact comparison, just on a power-system simulation
instead of an electromagnetic one (matching my actual background), to show the
methodology transfers directly.

## What it does

1. Builds a 6-bus meshed AC distribution network in **pandapower** — 4 load
   buses, 2 generator buses, 500 kW solar PV (~25–35% renewable penetration
   depending on scenario), 7 lines including a cross-brace so N-1 contingencies
   don't island the network. This extends the 6-bus network from my BTU Cottbus
   academic project (`github.com/d-evworks`).
2. Runs a **Newton-Raphson load flow** across a baseline case plus four N-1
   contingency scenarios: load +20%, line impedance +30% (aged conductors),
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
| `contingency.py` | Runs baseline + 4 N-1 scenarios, extracts risk metrics |
| `ai_agent.py` | Traditional vs. AI-agent report generation (LLM or rule-based) |
| `compare_workflows.py` | Ties it together, times both workflows, writes `results/` |

## Next steps if this goes further

- Swap the rule-based fallback's thresholds for a proper anomaly-detection
  model trained on a wider scenario sweep.
- Extend `ai_agent.py` to also *propose* which additional contingency
  scenarios are worth testing next, not just summarize the ones already run —
  closer to an autonomous agent than a report generator.
- Port the same pattern to an actual electromagnetic simulation (e.g. a motor
  or antenna model) once I have hands-on time with SIMULIA's EM tools.
