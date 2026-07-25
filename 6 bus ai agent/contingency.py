"""
Runs Newton-Raphson AC load flow for the baseline case and four N-1 contingency
scenarios against the 6-bus network, and returns structured results usable by
both the traditional (raw-numbers) workflow and the AI-agent workflow.
"""
import pandapower as pp
from network import build_network

VOLTAGE_LOW = 0.95
VOLTAGE_HIGH = 1.05
LINE_OVERLOAD_PCT = 100.0


def _analyze(net) -> dict:
    """Run NR load flow and extract the metrics an engineer would check by hand."""
    pp.runpp(net, algorithm="nr")

    vm = net.res_bus.vm_pu
    weak_buses = [
        (net.bus.name[i], round(float(vm[i]), 4))
        for i in vm.index
        if vm[i] < VOLTAGE_LOW or vm[i] > VOLTAGE_HIGH
    ]

    loading = net.res_line.loading_percent
    overloaded_lines = [
        (net.line.name[i], round(float(loading[i]), 1))
        for i in loading.index
        if loading[i] > LINE_OVERLOAD_PCT
    ]

    return {
        "converged": bool(net["converged"]),
        "min_voltage_pu": round(float(vm.min()), 4),
        "max_voltage_pu": round(float(vm.max()), 4),
        "weak_buses": weak_buses,
        "max_line_loading_pct": round(float(loading.max()), 1),
        "overloaded_lines": overloaded_lines,
        "total_active_losses_mw": round(float(net.res_line.pl_mw.sum()), 5),
    }


def run_all_scenarios() -> dict:
    results = {}

    # --- Baseline ---
    net = build_network()
    results["Baseline"] = _analyze(net)

    # --- Scenario 1: Load +20% ---
    net = build_network()
    net.load["p_mw"] *= 1.20
    net.load["q_mvar"] *= 1.20
    results["Load +20%"] = _analyze(net)

    # --- Scenario 2: Line impedance +30% (aged / degraded conductors) ---
    net = build_network()
    net.line["r_ohm_per_km"] *= 1.30
    net.line["x_ohm_per_km"] *= 1.30
    results["Impedance +30%"] = _analyze(net)

    # --- Scenario 3: PV removal (solar outage, e.g. cloud cover) ---
    net = build_network()
    net.sgen["p_mw"] = 0.0
    results["PV Removal"] = _analyze(net)

    # --- Scenario 4: Combined stress ---
    net = build_network()
    net.load["p_mw"] *= 1.20
    net.load["q_mvar"] *= 1.20
    net.line["r_ohm_per_km"] *= 1.30
    net.line["x_ohm_per_km"] *= 1.30
    net.sgen["p_mw"] = 0.0
    results["Combined Stress"] = _analyze(net)

    return results


if __name__ == "__main__":
    import json
    r = run_all_scenarios()
    print(json.dumps(r, indent=2))
