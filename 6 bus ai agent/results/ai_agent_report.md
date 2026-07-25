# AI-Agent Workflow Output (rule-based fallback mode)

Baseline network is healthy: voltages stay within 1.0165-1.0229 pu and losses are 0.00943 MW.

## Load +20%
**Risk detected:** none - network remains within limits.
Losses shift +33.5% vs. baseline.

## Impedance +30%
**Risk detected:** none - network remains within limits.
Losses shift +30.0% vs. baseline.

## PV Removal
**Risk detected:** none - network remains within limits.
Losses shift +76.7% vs. baseline.

## Combined Stress
**Risk detected:** line overloads on Line 0-1, Line 5-0.
Losses shift +213.8% vs. baseline.
Recommendation: reconfigure network topology or reinforce the overloaded feeder(s); consider curtailing non-critical load during this contingency.


*(Generated automatically by a rules-based agent. Set ANTHROPIC_API_KEY to switch to full LLM-generated narrative analysis instead.)*