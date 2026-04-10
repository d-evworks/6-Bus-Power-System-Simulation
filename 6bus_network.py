"""
6-Bus Power System Simulation with Renewable Integration
=========================================================
Author : Dev Kanwar
Tools  : Pandapower, Python (pandas, matplotlib)
Purpose: Model a 6-bus AC distribution network with a solar PV generator,
         perform Newton-Raphson load flow analysis, and run three
         scenario-based stress tests to evaluate voltage stability
         and grid performance.
"""

import pandapower as pp
import pandapower.plotting as plot
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import warnings
warnings.filterwarnings("ignore")

# ── Output folders ─────────────────────────────────────────────────────────────
os.makedirs("results", exist_ok=True)
os.makedirs("diagrams", exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# 1.  NETWORK BUILDER
# ══════════════════════════════════════════════════════════════════════════════

def build_network():
    """
    Build and return a 6-bus AC power network.

    Network topology
    ────────────────
    Bus 0 — Slack bus (external grid / reference bus, 110 kV)
    Bus 1 — Load bus (residential/commercial load)
    Bus 2 — Load bus + Solar PV generator (distributed generation)
    Bus 3 — Load bus (industrial load)
    Bus 4 — Load bus (mixed load)
    Bus 5 — Load bus (light load)

    Lines connect buses in a ring + radial topology to mimic a real
    medium-voltage distribution network.
    """

    net = pp.create_empty_network(name="6-Bus Renewable Integration Network")

    # ── Buses (voltage level: 110 kV) ──────────────────────────────────────
    pp.create_bus(net, vn_kv=110, name="Bus 0 - Slack (Grid)")
    pp.create_bus(net, vn_kv=110, name="Bus 1 - Load")
    pp.create_bus(net, vn_kv=110, name="Bus 2 - Solar + Load")
    pp.create_bus(net, vn_kv=110, name="Bus 3 - Industrial Load")
    pp.create_bus(net, vn_kv=110, name="Bus 4 - Mixed Load")
    pp.create_bus(net, vn_kv=110, name="Bus 5 - Light Load")

    # ── External Grid (slack bus — sets voltage reference) ──────────────────
    pp.create_ext_grid(net, bus=0, vm_pu=1.02, name="Main Grid Connection")

    # ── Loads (active power MW, reactive power MVAr) ────────────────────────
    pp.create_load(net, bus=1, p_mw=30.0,  q_mvar=10.0, name="Load Bus 1")
    pp.create_load(net, bus=2, p_mw=20.0,  q_mvar=7.0,  name="Load Bus 2")
    pp.create_load(net, bus=3, p_mw=50.0,  q_mvar=15.0, name="Load Bus 3 (Industrial)")
    pp.create_load(net, bus=4, p_mw=25.0,  q_mvar=8.0,  name="Load Bus 4")
    pp.create_load(net, bus=5, p_mw=15.0,  q_mvar=5.0,  name="Load Bus 5")

    # ── Solar PV Generator at Bus 2 ─────────────────────────────────────────
    # Modelled as a static generator (sgen) — injects active power, unity p.f.
    pp.create_sgen(net, bus=2, p_mw=25.0, q_mvar=0.0,
                   name="Solar PV Generator", type="PV")

    # ── Transmission Lines ──────────────────────────────────────────────────
    # Standard overhead line type: 240 mm² ACSR conductor
    line_type = "490-AL1/64-ST1A 380.0"   # available in pandapower std library

    # Using custom parameters for clarity and control
    # r_ohm_per_km, x_ohm_per_km, c_nf_per_km, max_i_ka, length_km
    def add_line(fb, tb, length, name):
        pp.create_line_from_parameters(
            net, from_bus=fb, to_bus=tb,
            length_km=length,
            r_ohm_per_km=0.1,      # resistance per km
            x_ohm_per_km=0.4,      # reactance per km
            c_nf_per_km=10.0,      # line capacitance
            max_i_ka=0.6,          # thermal current limit
            name=name
        )

    add_line(0, 1, 20, "Line 0-1")
    add_line(0, 3, 30, "Line 0-3")
    add_line(1, 2, 15, "Line 1-2")
    add_line(1, 4, 25, "Line 1-4")
    add_line(2, 5, 10, "Line 2-5")
    add_line(3, 4, 20, "Line 3-4")
    add_line(4, 5, 15, "Line 4-5")

    return net


# ══════════════════════════════════════════════════════════════════════════════
# 2.  POWER FLOW RUNNER
# ══════════════════════════════════════════════════════════════════════════════

def run_power_flow(net, label="baseline"):
    """
    Run Newton-Raphson AC power flow on the network.
    Saves bus and line results to CSV.
    Returns (bus_results_df, line_results_df).
    """
    pp.runpp(net, algorithm="nr", calculate_voltage_angles=True, verbose=False)

    bus_res  = net.res_bus.copy()
    line_res = net.res_line.copy()

    # Add human-readable names
    bus_res["bus_name"]  = net.bus["name"].values
    line_res["line_name"] = net.line["name"].values

    # Round for readability
    bus_res  = bus_res.round(4)
    line_res = line_res.round(4)

    bus_res.to_csv(f"results/bus_results_{label}.csv",  index_label="bus_id")
    line_res.to_csv(f"results/line_results_{label}.csv", index_label="line_id")

    print(f"\n{'='*60}")
    print(f"  Power Flow Results — {label.upper()}")
    print(f"{'='*60}")
    print("\n  BUS VOLTAGES (p.u.) and Angles (deg):")
    print(bus_res[["bus_name","vm_pu","va_degree"]].to_string(index=False))
    print("\n  LINE LOADING (%):")
    print(line_res[["line_name","loading_percent","p_from_mw","q_from_mvar"]].to_string(index=False))

    return bus_res, line_res


# ══════════════════════════════════════════════════════════════════════════════
# 3.  PLOTTING HELPERS
# ══════════════════════════════════════════════════════════════════════════════

BUS_POSITIONS = {
    0: (0, 2),
    1: (2, 3),
    2: (4, 3),
    3: (2, 1),
    4: (4, 1),
    5: (6, 2),
}

def plot_network_diagram(net, title="6-Bus Network", filename="diagrams/network_diagram.png"):
    """Draw a schematic network diagram with bus labels and line connections."""
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_facecolor("#F7F9FC")
    fig.patch.set_facecolor("#F7F9FC")

    # Draw lines
    for _, line in net.line.iterrows():
        fb, tb = line.from_bus, line.to_bus
        x0, y0 = BUS_POSITIONS[fb]
        x1, y1 = BUS_POSITIONS[tb]
        ax.plot([x0, x1], [y0, y1], color="#8BAABF", linewidth=2.5, zorder=1)
        mx, my = (x0+x1)/2, (y0+y1)/2
        ax.text(mx, my+0.08, f"{line['length_km']} km",
                ha="center", fontsize=7, color="#6688AA")

    # Draw buses
    colors = {0:"#E05C5C", 1:"#5C85E0", 2:"#F0A500", 3:"#5C85E0",
              4:"#5C85E0", 5:"#5C85E0"}
    labels = {0:"Bus 0\nSlack / Grid", 1:"Bus 1\nLoad",
              2:"Bus 2\nSolar+Load", 3:"Bus 3\nIndustrial",
              4:"Bus 4\nMixed", 5:"Bus 5\nLight Load"}

    for bus_id, (x, y) in BUS_POSITIONS.items():
        ax.scatter(x, y, s=500, color=colors[bus_id], zorder=3,
                   edgecolors="white", linewidths=2)
        ax.text(x, y-0.35, labels[bus_id], ha="center",
                fontsize=8, fontweight="bold", color="#1A1A1A")

    # Solar PV marker
    ax.annotate("☀ Solar PV\n25 MW", xy=BUS_POSITIONS[2],
                xytext=(BUS_POSITIONS[2][0]+0.4, BUS_POSITIONS[2][1]+0.55),
                fontsize=8, color="#D48000",
                arrowprops=dict(arrowstyle="->", color="#D48000"))

    # Legend
    patches = [
        mpatches.Patch(color="#E05C5C", label="Slack Bus (Grid Reference)"),
        mpatches.Patch(color="#5C85E0", label="Load Bus"),
        mpatches.Patch(color="#F0A500", label="Solar PV + Load Bus"),
    ]
    ax.legend(handles=patches, loc="lower left", fontsize=8, framealpha=0.9)

    ax.set_title(title, fontsize=13, fontweight="bold", color="#003366", pad=12)
    ax.set_xlim(-0.8, 7.2); ax.set_ylim(0.2, 4.0)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  -> Saved: {filename}")


def plot_voltage_comparison(results_dict, filename="diagrams/voltage_comparison.png"):
    """Bar chart comparing bus voltages across all scenarios."""
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor("#F7F9FC")
    ax.set_facecolor("#F7F9FC")

    bus_labels = [f"Bus {i}" for i in range(6)]
    x = range(6)
    width = 0.18
    colours = ["#003366","#E05C5C","#F0A500","#4CAF50"]
    offsets = [-1.5, -0.5, 0.5, 1.5]

    for i, (label, df) in enumerate(results_dict.items()):
        voltages = df["vm_pu"].values
        bars = ax.bar([xi + offsets[i]*width for xi in x],
                      voltages, width, label=label, color=colours[i], alpha=0.85)

    # Voltage limits
    ax.axhline(0.95, color="red",    linestyle="--", linewidth=1.2, label="Lower limit (0.95 p.u.)")
    ax.axhline(1.05, color="orange", linestyle="--", linewidth=1.2, label="Upper limit (1.05 p.u.)")

    ax.set_xticks(list(x)); ax.set_xticklabels(bus_labels, fontsize=10)
    ax.set_ylabel("Voltage Magnitude (p.u.)", fontsize=10)
    ax.set_title("Bus Voltage Comparison Across Scenarios", fontsize=13,
                 fontweight="bold", color="#003366")
    ax.set_ylim(0.88, 1.07)
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  -> Saved: {filename}")


def plot_line_loading_comparison(results_dict, filename="diagrams/line_loading_comparison.png"):
    """Bar chart comparing line loading % across all scenarios."""
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor("#F7F9FC")
    ax.set_facecolor("#F7F9FC")

    n_lines = 7
    line_labels = [f"Line {i}" for i in range(n_lines)]
    x = range(n_lines)
    width = 0.18
    colours = ["#003366","#E05C5C","#F0A500","#4CAF50"]
    offsets = [-1.5, -0.5, 0.5, 1.5]

    for i, (label, df) in enumerate(results_dict.items()):
        loading = df["loading_percent"].values
        ax.bar([xi + offsets[i]*width for xi in x],
               loading, width, label=label, color=colours[i], alpha=0.85)

    ax.axhline(100, color="red", linestyle="--", linewidth=1.2, label="Thermal limit (100%)")
    ax.set_xticks(list(x)); ax.set_xticklabels(line_labels, fontsize=10)
    ax.set_ylabel("Line Loading (%)", fontsize=10)
    ax.set_title("Line Loading Comparison Across Scenarios", fontsize=13,
                 fontweight="bold", color="#003366")
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  -> Saved: {filename}")


# ══════════════════════════════════════════════════════════════════════════════
# 4.  MAIN — BASELINE + 3 MODIFICATIONS
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("\n" + "="*60)
    print("  6-BUS POWER SYSTEM SIMULATION — Dev Kanwar")
    print("="*60)

    # ── Baseline ───────────────────────────────────────────────────────────
    print("\n[1/4] Running BASELINE scenario...")
    net_base = build_network()
    plot_network_diagram(net_base, title="6-Bus Network — Baseline")
    bus_base, line_base = run_power_flow(net_base, "baseline")

    # ── Modification 1: Increase Load (Stress Test) ────────────────────────
    print("\n[2/4] Running MOD 1 — Increased Load (Stress Test)...")
    net_m1 = build_network()
    for i in net_m1.load.index:
        net_m1.load.at[i, "p_mw"]   *= 1.5   # 50% load increase
        net_m1.load.at[i, "q_mvar"] *= 1.5
    bus_m1, line_m1 = run_power_flow(net_m1, "mod1_increased_load")

    # ── Modification 2: Increase Line Length (Weak Network) ────────────────
    print("\n[3/4] Running MOD 2 — Increased Line Length (Weak Network)...")
    net_m2 = build_network()
    net_m2.line["length_km"] *= 2.0            # double line lengths = higher impedance
    bus_m2, line_m2 = run_power_flow(net_m2, "mod2_weak_network")

    # ── Modification 3: Remove Solar Generator ─────────────────────────────
    print("\n[4/4] Running MOD 3 — Solar Generator Removed...")
    net_m3 = build_network()
    net_m3.sgen.at[0, "in_service"] = False    # take solar offline
    bus_m3, line_m3 = run_power_flow(net_m3, "mod3_no_solar")

    # ── Comparison Plots ───────────────────────────────────────────────────
    print("\nGenerating comparison plots...")
    bus_results = {
        "Baseline":         bus_base,
        "Mod 1 – High Load": bus_m1,
        "Mod 2 – Long Lines": bus_m2,
        "Mod 3 – No Solar":  bus_m3,
    }
    line_results = {
        "Baseline":         line_base,
        "Mod 1 – High Load": line_m1,
        "Mod 2 – Long Lines": line_m2,
        "Mod 3 – No Solar":  line_m3,
    }
    plot_voltage_comparison(bus_results)
    plot_line_loading_comparison(line_results)

    print("\n" + "="*60)
    print("  SIMULATION COMPLETE")
    print("  Results  -> results/")
    print("  Diagrams -> diagrams/")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
