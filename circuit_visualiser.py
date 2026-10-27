"""
DC Resistor Network Solver using Nodal Analysis.

What this script does:-

1. Describes a circuit as a list of resistors and the current injected into each node.
2. Builds the conductance matrix G (the "stamping" method) and solves G @ V = I.
3. Computes every branch current from Ohm's law.
4. Checks the answer (see the checks section of the README).
5. Runs a small test suite on circuits with known answers.
6. Draws the two-node example circuit with Matplotlib.

Node numbering: unknown nodes are 0, 1, 2, ...   Ground is written as None.
A resistor is written as (node_a, node_b, ohms).  Use None for ground.
"""

import numpy as np
import matplotlib.pyplot as plt


# ----------------------------------------------------------------------
# 1. Solver
# ----------------------------------------------------------------------
def clean_resistors(resistors, num_nodes):
    """Check the input and put every resistor in the form (real_node, other, ohms)."""
    cleaned = []
    for a, b, ohms in resistors:
        if ohms <= 0:
            raise ValueError("Resistance must be greater than zero.")
        if a is None and b is None:
            raise ValueError("A resistor cannot connect ground to ground.")
        if a is None:               # always list the real node first
            a, b = b, a
        if a == b:
            raise ValueError("A resistor cannot connect a node to itself.")
        for node in (a, b):
            if node is not None and not 0 <= node < num_nodes:
                raise ValueError(f"Node {node} does not exist.")
        cleaned.append((a, b, ohms))
    return cleaned


def build_conductance_matrix(resistors, num_nodes):
    """Stamp each resistor into the conductance matrix G.

    For a resistor with conductance g = 1/R between nodes a and b:
        G[a, a] += g      G[b, b] += g
        G[a, b] -= g      G[b, a] -= g
    If b is ground, only G[a, a] += g is needed.
    """
    G = np.zeros((num_nodes, num_nodes))
    for a, b, ohms in resistors:
        g = 1.0 / ohms
        G[a, a] += g
        if b is not None:
            G[b, b] += g
            G[a, b] -= g
            G[b, a] -= g
    return G


def solve_dc(resistors, injections):
    """Return (node_voltages, G, cleaned_resistors) for G @ V = I."""
    injections = np.asarray(injections, dtype=float)
    num_nodes = len(injections)
    resistors = clean_resistors(resistors, num_nodes)
    G = build_conductance_matrix(resistors, num_nodes)
    try:
        V = np.linalg.solve(G, injections)
    except np.linalg.LinAlgError:
        raise ValueError(
            "The matrix is singular: part of the circuit has no path to ground."
        )
    return V, G, resistors


def branch_currents(resistors, V):
    """Current through each resistor, from node a toward node b (Ohm's law)."""
    currents = []
    for a, b, ohms in resistors:
        v_b = 0.0 if b is None else V[b]
        currents.append((V[a] - v_b) / ohms)
    return currents


def kcl_residuals(resistors, injections, V):
    """Net current left over at each node. It should be ~0 everywhere.

    This is built from the branch currents (Ohm's law on each resistor), NOT from
    the matrix G, so it can catch a mistake in how G was built.
    """
    residual = np.array(injections, dtype=float)
    for (a, b, _), i in zip(resistors, branch_currents(resistors, V)):
        residual[a] -= i            # current leaves node a through this resistor
        if b is not None:
            residual[b] += i        # and arrives at node b
    return residual


# ----------------------------------------------------------------------
# 2. Tests on circuits with answers we can work out by hand
# ----------------------------------------------------------------------
def run_tests():
    # Test 1: one resistor to ground. Ohm's law: V = I * R.
    V, _, _ = solve_dc([(0, None, 500)], [0.002])
    assert np.isclose(V[0], 1.0)

    # Test 2: two resistors in series. 1 mA through 1 kOhm then 2 kOhm.
    # V1 = 1 mA * 2k = 2 V, V0 = V1 + 1 mA * 1k = 3 V.
    V, _, _ = solve_dc([(0, 1, 1000), (1, None, 2000)], [0.001, 0.0])
    assert np.allclose(V, [3.0, 2.0])

    # Test 3: the main two-node example, solved by hand: VA = 2.8 V, VB = 2.4 V.
    V, _, _ = solve_dc(
        [(0, None, 1000), (1, None, 2000), (0, 1, 2000)], [0.003, 0.001]
    )
    assert np.allclose(V, [2.8, 2.4])

    # Test 4: balanced Wheatstone bridge. When R1/R3 == R2/R4, the two middle
    # nodes are at the same voltage, so no current flows in the bridge resistor.
    # Nodes: 0 = top (current in), 1 = left, 2 = right. Ground is the bottom.
    bridge = [(0, 1, 100), (0, 2, 300), (1, None, 200), (2, None, 600), (1, 2, 50)]
    V, _, res = solve_dc(bridge, [0.01, 0.0, 0.0])
    assert abs(V[1] - V[2]) < 1e-9
    assert abs(branch_currents(res, V)[4]) < 1e-9

    # Test 5: change one resistor and the bridge must become unbalanced.
    unbalanced = [(0, 1, 100), (0, 2, 300), (1, None, 200), (2, None, 900), (1, 2, 50)]
    V, _, _ = solve_dc(unbalanced, [0.01, 0.0, 0.0])
    assert abs(V[1] - V[2]) > 1e-3

    # Test 6: bad input is rejected.
    for bad in ([(0, None, 0)], [(0, None, -5)], [(0, 3, 100)]):
        try:
            solve_dc(bad, [0.001])
        except ValueError:
            continue
        raise AssertionError("Bad input was not rejected.")

    print("All tests passed (6 of 6).")


# ----------------------------------------------------------------------
# 3. Drawing (written for the two-node example: nodes A and B)
# ----------------------------------------------------------------------
def draw_two_node_circuit(resistors, injections, V, save_as=None, show=True):
    fig, ax = plt.subplots(figsize=(12, 7))

    r_a = next(r for n1, n2, r in resistors if n1 == 0 and n2 is None)
    r_b = next(r for n1, n2, r in resistors if n1 == 1 and n2 is None)
    r_ab = next(r for n1, n2, r in resistors if n1 == 0 and n2 == 1)

    current_a = V[0] / r_a
    current_b = V[1] / r_b
    current_ab = (V[0] - V[1]) / r_ab
    source_a, source_b = injections

    x_a, x_b = 2.0, 6.0
    y_node, y_bus, y_ground = 5.0, 4.5, 1.3

    branches = [
        {"node_x": x_a, "resistor_x": 1.2, "source_x": 2.8, "resistance": r_a,
         "branch_current": current_a, "source_current": source_a,
         "resistor_name": "RA", "source_name": "IA"},
        {"node_x": x_b, "resistor_x": 5.2, "source_x": 6.8, "resistance": r_b,
         "branch_current": current_b, "source_current": source_b,
         "resistor_name": "RB", "source_name": "IB"},
    ]

    # Main wire and connecting resistor RAB
    ax.plot([x_a, 3.5], [y_node, y_node], color="black", linewidth=2)
    ax.plot([4.5, x_b], [y_node, y_node], color="black", linewidth=2)
    ax.plot([3.5, 3.65, 3.8, 3.95, 4.1, 4.25, 4.4, 4.5],
            [5.0, 5.18, 4.82, 5.18, 4.82, 5.18, 4.82, 5.0],
            color="black", linewidth=2)
    ax.text(4.0, 5.72,
            f"RAB = {r_ab / 1000:g} kΩ\nI = {current_ab * 1000:.3f} mA",
            ha="center", va="center", fontsize=10)
    if abs(current_ab) > 1e-12:
        start, end = (3.65, 4.35) if current_ab > 0 else (4.35, 3.65)
        ax.annotate("", xy=(end, 4.35), xytext=(start, 4.35),
                    arrowprops=dict(arrowstyle="->", color="blue", linewidth=1.8))

    # Resistor and current-source branches
    for br in branches:
        node_x, res_x, src_x = br["node_x"], br["resistor_x"], br["source_x"]

        ax.plot([node_x, node_x], [y_node, y_bus], color="black", linewidth=2)
        ax.plot([res_x, src_x], [y_bus, y_bus], color="black", linewidth=2)
        ax.plot([res_x, res_x], [y_bus, 3.9], color="black", linewidth=2)
        ax.plot([res_x, res_x - 0.16, res_x + 0.16, res_x - 0.16,
                 res_x + 0.16, res_x - 0.16, res_x],
                [3.9, 3.73, 3.56, 3.39, 3.22, 3.05, 2.88],
                color="black", linewidth=2)
        ax.plot([res_x, res_x], [2.88, y_ground], color="black", linewidth=2)
        ax.text(res_x - 0.28, 3.4,
                f'{br["resistor_name"]}\n{br["resistance"] / 1000:g} kΩ\n'
                f'{br["branch_current"] * 1000:.3f} mA',
                ha="right", va="center", fontsize=9)

        if abs(br["branch_current"]) > 1e-12:
            y_start, y_end = (3.35, 2.65) if br["branch_current"] > 0 else (2.65, 3.35)
            ax.annotate("", xy=(res_x + 0.27, y_end), xytext=(res_x + 0.27, y_start),
                        arrowprops=dict(arrowstyle="->", color="blue", linewidth=1.5))

        ax.plot([src_x, src_x], [y_bus, 3.65], color="black", linewidth=2)
        ax.add_patch(plt.Circle((src_x, 3.3), 0.35, fill=False,
                                edgecolor="black", linewidth=2))
        a_start, a_end = (3.08, 3.52) if br["source_current"] >= 0 else (3.52, 3.08)
        ax.annotate("", xy=(src_x, a_end), xytext=(src_x, a_start),
                    arrowprops=dict(arrowstyle="->", linewidth=1.5))
        ax.text(src_x + 0.42, 3.3,
                f'{br["source_name"]}\n{abs(br["source_current"]) * 1000:g} mA',
                ha="left", va="center", fontsize=9)
        ax.plot([src_x, src_x], [2.95, y_ground], color="black", linewidth=2)

    # Ground rail and symbol
    ax.plot([0.7, 7.3], [y_ground, y_ground], color="black", linewidth=2)
    ax.plot([3.7, 4.3], [1.1, 1.1], color="black", linewidth=2)
    ax.plot([3.8, 4.2], [0.95, 0.95], color="black", linewidth=2)
    ax.plot([3.9, 4.1], [0.8, 0.8], color="black", linewidth=2)

    # Node markers and voltage labels
    ax.scatter([x_a, x_b], [y_node, y_node], color="red", s=60, zorder=5)
    ax.text(x_a - 0.15, 5.25, f"A = {V[0]:.3f} V", ha="right", va="bottom", fontsize=10)
    ax.text(x_b + 0.15, 5.25, f"B = {V[1]:.3f} V", ha="left", va="bottom", fontsize=10)

    ax.set_title("DC Resistor Network — Nodal Analysis", fontsize=14, pad=20)
    ax.set_xlim(-0.2, 8.3)
    ax.set_ylim(0.5, 6.3)
    ax.set_aspect("equal")
    ax.axis("off")
    plt.tight_layout()
    if save_as:
        fig.savefig(save_as, dpi=200)
    if show:
        plt.show()


# ----------------------------------------------------------------------
# 4. Main: solve the example circuit, check it, draw it
# ----------------------------------------------------------------------
def main():
    run_tests()

    # Example circuit. Nodes: A = 0, B = 1. Ground = None.
    resistors = [
        (0, None, 1000),   # RA : node A to ground, 1 kOhm
        (1, None, 2000),   # RB : node B to ground, 2 kOhm
        (0, 1, 2000),      # RAB: node A to node B, 2 kOhm
    ]
    injections = [0.003, 0.001]   # amperes injected into A and B

    V, G, resistors = solve_dc(resistors, injections)

    print("\nConductance matrix G (siemens):")
    print(G)
    print("\nNode voltages:")
    print(f"  VA = {V[0]:.3f} V")
    print(f"  VB = {V[1]:.3f} V")

    print("\nBranch currents (positive = from first node toward second):")
    for (a, b, ohms), i in zip(resistors, branch_currents(resistors, V)):
        target = "ground" if b is None else f"node {b}"
        print(f"  node {a} -> {target} ({ohms:g} ohm): {i * 1000:.3f} mA")

    print("\nCheck 1 - matrix residual |G@V - I| (tests the solver only):")
    print(f"  max = {np.max(np.abs(G @ V - injections)):.3e} A")

    print("\nCheck 2 - KCL from branch currents (tests the matrix building):")
    for node, r in enumerate(kcl_residuals(resistors, injections, V)):
        print(f"  node {node}: leftover current = {r * 1000:.12f} mA")

    draw_two_node_circuit(resistors, injections, V, save_as="circuit_diagram.png")


if __name__ == "__main__":
    main()
