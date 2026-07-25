"""
6-bus meshed AC distribution network with renewable (solar PV) integration.
Built with pandapower. Mirrors the network described in the BTU Cottbus
academic project: 4 load buses, 2 generator buses, 500 kW solar PV.
"""
import pandapower as pp


def build_network():
    net = pp.create_empty_network(name="6-Bus Meshed Distribution Network", sn_mva=10)

    # Buses (20 kV distribution level)
    b0 = pp.create_bus(net, vn_kv=20, name="Bus 0 - Slack/Grid")
    b1 = pp.create_bus(net, vn_kv=20, name="Bus 1 - Generator")
    b2 = pp.create_bus(net, vn_kv=20, name="Bus 2 - Load + Solar PV")
    b3 = pp.create_bus(net, vn_kv=20, name="Bus 3 - Load")
    b4 = pp.create_bus(net, vn_kv=20, name="Bus 4 - Load")
    b5 = pp.create_bus(net, vn_kv=20, name="Bus 5 - Load")

    # Slack / external grid at Bus 0
    pp.create_ext_grid(net, bus=b0, vm_pu=1.02, name="Grid Connection")

    # Generator at Bus 1 - fixed PQ output (not voltage-controlled), so the
    # network voltage profile actually responds to loading/topology stress
    pp.create_sgen(net, bus=b1, p_mw=0.8, q_mvar=0.15, name="Gen 1", type="Sync")

    # Loads
    pp.create_load(net, bus=b2, p_mw=0.20, q_mvar=0.05, name="Load 2")
    pp.create_load(net, bus=b3, p_mw=0.60, q_mvar=0.15, name="Load 3")
    pp.create_load(net, bus=b4, p_mw=0.30, q_mvar=0.08, name="Load 4")
    pp.create_load(net, bus=b5, p_mw=0.90, q_mvar=0.22, name="Load 5")

    # 500 kW Solar PV at Bus 2
    pp.create_sgen(net, bus=b2, p_mw=0.5, q_mvar=0.0, name="Solar PV", type="PV")

    # Meshed line topology (loop + cross-brace so N-1 contingencies don't island the network)
    line_params = dict(r_ohm_per_km=0.42, x_ohm_per_km=0.38, c_nf_per_km=230,
                        max_i_ka=0.035)
    pp.create_line_from_parameters(net, from_bus=b0, to_bus=b1, length_km=4.5,
                                    name="Line 0-1", **line_params)
    pp.create_line_from_parameters(net, from_bus=b1, to_bus=b2, length_km=5.0,
                                    name="Line 1-2", **line_params)
    pp.create_line_from_parameters(net, from_bus=b2, to_bus=b3, length_km=3.5,
                                    name="Line 2-3", **line_params)
    pp.create_line_from_parameters(net, from_bus=b3, to_bus=b4, length_km=4.0,
                                    name="Line 3-4", **line_params)
    pp.create_line_from_parameters(net, from_bus=b4, to_bus=b5, length_km=9.5,
                                    name="Line 4-5", **line_params)
    pp.create_line_from_parameters(net, from_bus=b5, to_bus=b0, length_km=5.5,
                                    name="Line 5-0", **line_params)
    pp.create_line_from_parameters(net, from_bus=b1, to_bus=b4, length_km=11.0,
                                    name="Line 1-4 (cross-brace)", **line_params)

    return net


def renewable_penetration_pct(net):
    total_load = net.load.p_mw.sum()
    total_pv = net.sgen.loc[net.sgen.name == "Solar PV", "p_mw"].sum()
    return 100 * total_pv / total_load


if __name__ == "__main__":
    net = build_network()
    pp.runpp(net)
    print(net.res_bus)
    print(f"\nRenewable penetration: {renewable_penetration_pct(net):.1f}% of total load")
