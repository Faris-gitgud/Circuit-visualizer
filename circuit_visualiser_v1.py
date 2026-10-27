
import numpy as np
import matplotlib.pyplot as plt
# Unknown nodes: A = 0, B = 1
G = np.zeros((2, 2))

# Resistors: (node 1, node 2, resistance in ohms)
# None represents ground
resistors = [
    (0, None, 1000),
    (1, None, 2000),
    (0, 1, 2000)
]

for node1, node2, resistance in resistors:
    if resistance <= 0:
        raise ValueError(
            "Resistance must be greater than zero."
        )

    conductance = 1 / resistance

    G[node1, node1] += conductance

    if node2 is not None:
        G[node2, node2] += conductance
        G[node1, node2] -= conductance
        G[node2, node1] -= conductance

# Current injected into each node, in amperes
I = np.array([0.003, 0.001])

V = np.linalg.solve(G, I)
print("DEBUG - G:", G)
print("DEBUG - I:", I)
print("DEBUG - V:", V)
print("DEBUG - G @ V:", G @ V)

# Verify that our solution satisfies G @ V = I
calculated_currents = G @ V

print("\nVerification:")
print("Expected current vector:", I)
print("Calculated current vector:", calculated_currents)

print("Maximum error:", np.max(np.abs(calculated_currents - I)))
print("Conductance matrix:")
print(G)

print("Node voltages:")
print(f"VA = {V[0]:.3f} V")
print(f"VB = {V[1]:.3f} V")


# Calculate current through each resistor
for node1, node2, resistance in resistors:
    voltage1 = V[node1]
    voltage2 = 0 if node2 is None else V[node2]

    current = (voltage1 - voltage2) / resistance

    print(
        f"Current from node {node1} to "
        f"{'ground' if node2 is None else 'node ' + str(node2)}: "
        f"{current * 1000:.3f} mA"
    )
# Verify Kirchhoff's Current Law at every node
print("\nKCL verification:")

for node in range(len(V)):
    net_current = I[node]

    for node1, node2, resistance in resistors:
        conductance = 1 / resistance

        if node1 == node:
            voltage2 = 0 if node2 is None else V[node2]
            net_current -= (V[node1] - voltage2) / resistance

        elif node2 == node:
            net_current -= (V[node2] - V[node1]) / resistance

    print(
        f"Node {node}: net current = "
        f"{net_current * 1000:.12f} mA"
    )






# ==========================================
# Circuit Visualization
# ==========================================

fig, ax = plt.subplots(figsize=(12, 7))

# ------------------------------------------
# Read component values from the circuit
# ------------------------------------------

r_a = next(
    r for n1, n2, r in resistors
    if n1 == 0 and n2 is None
)

r_b = next(
    r for n1, n2, r in resistors
    if n1 == 1 and n2 is None
)

r_ab = next(
    r for n1, n2, r in resistors
    if (n1 == 0 and n2 == 1)
    or (n1 == 1 and n2 == 0)
)

# Branch currents, in amperes
current_a = V[0] / r_a
current_b = V[1] / r_b
current_ab = (V[0] - V[1]) / r_ab

# Current injections, in amperes
source_a = I[0]
source_b = I[1]

# ------------------------------------------
# Layout
# ------------------------------------------

x_a = 2.0
x_b = 6.0
y_node = 5.0
y_bus = 4.5
y_ground = 1.3

# Each node has two parallel branches:
# a resistor and a current source.

branches = [
    {
        "node_x": x_a,
        "resistor_x": 1.2,
        "source_x": 2.8,
        "resistance": r_a,
        "branch_current": current_a,
        "source_current": source_a,
        "node_voltage": V[0],
        "node_name": "A",
        "resistor_name": "RA",
        "source_name": "IA",
    },
    {
        "node_x": x_b,
        "resistor_x": 5.2,
        "source_x": 6.8,
        "resistance": r_b,
        "branch_current": current_b,
        "source_current": source_b,
        "node_voltage": V[1],
        "node_name": "B",
        "resistor_name": "RB",
        "source_name": "IB",
    },
]

# ------------------------------------------
# Main wire and connecting resistor RAB
# ------------------------------------------

ax.plot(
    [x_a, 3.5], [y_node, y_node],
    color="black", linewidth=2
)

ax.plot(
    [4.5, x_b], [y_node, y_node],
    color="black", linewidth=2
)

# Zigzag resistor symbol
ax.plot(
    [3.5, 3.65, 3.8, 3.95, 4.1, 4.25, 4.4, 4.5],
    [5.0, 5.18, 4.82, 5.18, 4.82, 5.18, 4.82, 5.0],
    color="black", linewidth=2
)

# Resistor label
ax.text(
    4.0, 5.72,
    f"RAB = {r_ab / 1000:g} kΩ\n"
    f"I = {current_ab * 1000:.3f} mA",
    ha="center", va="center", fontsize=10
)

# Current arrow through RAB
if abs(current_ab) > 1e-12:
    if current_ab > 0:
        arrow_start, arrow_end = 3.65, 4.35
    else:
        arrow_start, arrow_end = 4.35, 3.65

    ax.annotate(
        "",
        xy=(arrow_end, 4.35),
        xytext=(arrow_start, 4.35),
        arrowprops=dict(
            arrowstyle="->", color="blue", linewidth=1.8
        )
    )

# ------------------------------------------
# Draw resistor and current-source branches
# ------------------------------------------

for branch in branches:
    node_x = branch["node_x"]
    resistor_x = branch["resistor_x"]
    source_x = branch["source_x"]
    resistance = branch["resistance"]
    branch_current = branch["branch_current"]
    source_current = branch["source_current"]

    # Node wire down to the branch connection bus
    ax.plot(
        [node_x, node_x], [y_node, y_bus],
        color="black", linewidth=2
    )

    # Horizontal bus connects both parallel branches
    ax.plot(
        [resistor_x, source_x], [y_bus, y_bus],
        color="black", linewidth=2
    )

    # Wire from bus to resistor
    ax.plot(
        [resistor_x, resistor_x], [y_bus, 3.9],
        color="black", linewidth=2
    )

    # Zigzag vertical resistor
    ax.plot(
        [
            resistor_x,
            resistor_x - 0.16,
            resistor_x + 0.16,
            resistor_x - 0.16,
            resistor_x + 0.16,
            resistor_x - 0.16,
            resistor_x
        ],
        [3.9, 3.73, 3.56, 3.39, 3.22, 3.05, 2.88],
        color="black", linewidth=2
    )

    # Wire from resistor to ground rail
    ax.plot(
        [resistor_x, resistor_x],
        [2.88, y_ground],
        color="black", linewidth=2
    )

    # Resistor label, positioned to the left
    ax.text(
        resistor_x - 0.28, 3.4,
        f'{branch["resistor_name"]}\n'
        f'{resistance / 1000:g} kΩ\n'
        f'{branch_current * 1000:.3f} mA',
        ha="right", va="center", fontsize=9
    )

    # Current direction through resistor
    if abs(branch_current) > 1e-12:
        if branch_current > 0:
        # Positive current flows from node toward ground
            y_start, y_end = 3.35, 2.65
        else:
        # Negative current flows from ground toward node
            y_start, y_end = 2.65, 3.35

    ax.annotate(
        "",
        xy=(resistor_x + 0.27, y_end),
        xytext=(resistor_x + 0.27, y_start),
        arrowprops=dict(
            arrowstyle="->", color="blue", linewidth=1.5
        )
    )

    # Wire from bus to current source
    ax.plot(
        [source_x, source_x], [y_bus, 3.65],
        color="black", linewidth=2
    )

    # Current-source circle
    ax.add_patch(
        plt.Circle(
            (source_x, 3.3), 0.35,
            fill=False, edgecolor="black", linewidth=2
        )
    )

    # Current arrow: upward means positive injection
    if source_current >= 0:
        arrow_start, arrow_end = 3.08, 3.52
    else:
        arrow_start, arrow_end = 3.52, 3.08

    ax.annotate(
        "",
        xy=(source_x, arrow_end),
        xytext=(source_x, arrow_start),
        arrowprops=dict(arrowstyle="->", linewidth=1.5)
    )

    # Source current label, placed away from wires
    ax.text(
        source_x + 0.42, 3.3,
        f'{branch["source_name"]}\n'
        f'{abs(source_current) * 1000:g} mA',
        ha="left", va="center", fontsize=9
    )

    # Wire from source to ground rail
    ax.plot(
        [source_x, source_x],
        [2.95, y_ground],
        color="black", linewidth=2
    )

# ------------------------------------------
# Shared ground rail
# ------------------------------------------

ax.plot(
    [0.7, 7.3], [y_ground, y_ground],
    color="black", linewidth=2
)

# Ground symbol
ax.plot([3.7, 4.3], [1.1, 1.1],
        color="black", linewidth=2)
ax.plot([3.8, 4.2], [0.95, 0.95],
        color="black", linewidth=2)
ax.plot([3.9, 4.1], [0.8, 0.8],
        color="black", linewidth=2)

# ------------------------------------------
# Node markers and voltage labels
# ------------------------------------------

ax.scatter(
    [x_a, x_b], [y_node, y_node],
    color="red", s=60, zorder=5
)

ax.text(
    x_a - 0.15, 5.25,
    f"A = {V[0]:.3f} V",
    ha="right", va="bottom", fontsize=10
)

ax.text(
    x_b + 0.15, 5.25,
    f"B = {V[1]:.3f} V",
    ha="left", va="bottom", fontsize=10
)

# ------------------------------------------
# Final formatting
# ------------------------------------------

ax.set_title(
    "DC Resistor Network — Nodal Analysis",
    fontsize=14, pad=20
)

ax.set_xlim(-0.2, 8.3)
ax.set_ylim(0.5, 6.3)
ax.set_aspect("equal")
ax.axis("off")

plt.tight_layout()
plt.show()


