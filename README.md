# 6-Bus Power System Simulation with Renewable Integration

**Author:** Dev Kanwar | M.Sc. Power Engineering, BTU Cottbus  
**Tools:** Python · Pandapower · pandas · matplotlib  
**Topic:** AC Power Flow Analysis · Voltage Stability · Renewable Grid Integration

---

## Overview

This project models a **6-bus AC power distribution network** using [Pandapower](https://www.pandapower.org/), an open-source Python library for power system analysis. A **solar PV generator** is integrated at Bus 2 to study the behaviour of renewable generation in a meshed grid.

The simulation performs **Newton-Raphson load flow analysis** under a baseline operating condition and three stress-test scenarios to evaluate how changes in load demand, network impedance, and renewable generation affect **bus voltages**, **line loading**, and overall **grid stability**.

---

## Network Topology

```
Bus 0 (Slack/Grid) ──── Bus 1 (Load) ──── Bus 2 (Solar PV + Load)
        │                    │                        │
        └──── Bus 3 ──── Bus 4 (Mixed) ──── Bus 5 (Light Load)
           (Industrial)
```

| Bus | Type | Description |
|-----|------|-------------|
| 0 | Slack | External grid connection — voltage reference (1.02 p.u.) |
| 1 | PQ Load | Residential / commercial load (30 MW) |
| 2 | PQ Load + Generator | Load (20 MW) + Solar PV (25 MW) |
| 3 | PQ Load | Industrial load (50 MW) |
| 4 | PQ Load | Mixed load (25 MW) |
| 5 | PQ Load | Light load (15 MW) |

**Lines:** 7 transmission lines, 10–30 km each, r = 0.1 Ω/km, x = 0.4 Ω/km, thermal limit = 600 A

---

## Project Structure

```
6-Bus-Power-System-Simulation/
│
├── 6bus_network.py          # Main simulation script
├── requirements.txt         # Python dependencies
├── README.md
│
├── results/
│   ├── bus_results_baseline.csv
│   ├── line_results_baseline.csv
│   ├── bus_results_mod1_increased_load.csv
│   ├── line_results_mod1_increased_load.csv
│   ├── bus_results_mod2_weak_network.csv
│   ├── line_results_mod2_weak_network.csv
│   ├── bus_results_mod3_no_solar.csv
│   └── line_results_mod3_no_solar.csv
│
└── diagrams/
    ├── network_diagram.png
    ├── voltage_comparison.png
    └── line_loading_comparison.png
```

---

## Scenarios

### Baseline
Standard operating condition. All loads active, solar PV generating 25 MW.  
All bus voltages expected within the acceptable range of **0.95–1.05 p.u.**

### Modification 1 — Stress Test (Increased Load)
All loads increased by **50%** to simulate peak demand conditions.  
**Purpose:** Identify voltage collapse risk and overloaded lines under high demand.  
**Expected outcome:** Voltage drop at remote buses (4, 5), potential line overloading.

### Modification 2 — Weak Network (Increased Line Length)
All line lengths **doubled**, increasing total impedance (R and X).  
**Purpose:** Simulate a geographically spread or poorly interconnected grid.  
**Expected outcome:** Higher resistive losses, greater voltage deviation from Bus 0.

### Modification 3 — Renewable Dependency (Solar Generator Removed)
Solar PV generator at Bus 2 taken offline (`in_service = False`).  
**Purpose:** Quantify the grid's dependency on renewable generation; study what happens when intermittent sources drop out.  
**Expected outcome:** Bus 2 voltage drops, external grid must supply additional power, line loading increases.

---

## How to Run

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/6-Bus-Power-System-Simulation.git
cd 6-Bus-Power-System-Simulation
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the simulation**
```bash
python 6bus_network.py
```

Results are saved automatically to `results/` and `diagrams/`.

---

## Key Concepts

| Term | Meaning |
|------|---------|
| **Bus** | A node in the power network — a point where lines, loads, or generators connect |
| **Slack bus** | The reference bus — fixes voltage magnitude and angle; supplies or absorbs any power imbalance |
| **Load flow / Power flow** | Mathematical calculation of voltages, currents, and power at every point in the grid |
| **Newton-Raphson** | Iterative numerical method used to solve the nonlinear power flow equations |
| **p.u. (per unit)** | Normalised voltage — 1.0 p.u. = nominal voltage; acceptable range is typically 0.95–1.05 p.u. |
| **Line loading %** | How much of a line's maximum current capacity is being used; >100% = overloaded |
| **sgen (static generator)** | Pandapower element for renewable generators (PV, wind) — injects real power |
| **Voltage stability** | The grid's ability to maintain acceptable voltages under varying load and generation conditions |

---

## Results Summary

> Run the script to generate your own results. Typical findings:

- **Baseline:** All voltages within 0.95–1.05 p.u., no lines overloaded.
- **Mod 1 (High Load):** Voltages at remote buses drop below 0.95 p.u.; lines near industrial bus approach thermal limits.
- **Mod 2 (Long Lines):** Increased impedance causes higher voltage drops proportional to distance from slack bus.
- **Mod 3 (No Solar):** Bus 2 voltage decreases; grid import from slack bus increases; highlights solar contribution to local voltage support.

---

## Technologies

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Pandapower](https://img.shields.io/badge/Pandapower-2.13%2B-green)
![Pandas](https://img.shields.io/badge/pandas-1.5%2B-lightblue?logo=pandas)
![Matplotlib](https://img.shields.io/badge/matplotlib-3.6%2B-orange)

---

## Contact

**Dev Kanwar**  
M.Sc. Power Engineering — Brandenburg University of Technology Cottbus  
devkanwar0515@gmail.com · [LinkedIn](https://linkedin.com/in/dev-kanwar-b8729124b)
