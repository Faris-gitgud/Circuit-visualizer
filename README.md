# DC Resistor Network Solver and Visualizer

A Python project that uses nodal analysis to calculate node voltages and branch currents in a two-node DC resistor network. It constructs a conductance matrix, solves the resulting linear system, verifies the numerical solution, and visualizes the circuit using Matplotlib.

## Project Overview

Solving electrical circuits by hand is useful for understanding circuit theory, but repetitive calculations can become tedious. This project applies Python and numerical linear algebra to automate the solution of a simple DC resistor network.

The project combines electrical engineering concepts with computational methods to demonstrate how mathematical circuit models can be translated into working code.

## Concepts Used

- Ohm's law
- Kirchhoff's Current Law (KCL)
- Nodal analysis
- Electrical conductance
- Matrix equations and numerical linear algebra
- Branch-current calculations
- Numerical verification and error checking

## How It Works

### 1. Define the circuit

The circuit is represented using a list of resistors. Each resistor is described by its two endpoints and resistance in ohms. `None` represents ground.

For example:

```python
resistors = [
    (0, None, 1000),
    (1, None, 2000),
    (0, 1, 2000)
]
```

The current-injection vector specifies the current entering each node.

### 2. Construct the conductance matrix

Each resistance is converted into conductance:

\[
G = \frac{1}{R}
\]

The circuit equations are assembled into the matrix system:

\[
GV=I
\]

where:

- \(G\) is the conductance matrix
- \(V\) is the vector of unknown node voltages
- \(I\) is the vector of injected currents

### 3. Solve for node voltages

NumPy's `np.linalg.solve()` calculates the unknown node voltages from the matrix equation.

### 4. Calculate branch currents

Ohm's law is used to calculate the current through each resistor from the voltage difference across it.

### 5. Verify the solution

The program checks the calculated solution against the original current vector and evaluates the net current at each node to verify Kirchhoff's Current Law.

### 6. Visualize the circuit

Matplotlib displays the resistor network, node voltages, component values, current sources, and calculated branch currents.

## Technologies

- Python
- NumPy
- Matplotlib

## How to Run

1. Install Python 3.
2. Install the required libraries:

   ```bash
   pip install numpy matplotlib
   ```

3. Run the Python script:

   ```bash
   python circuit_visualizer.py
   ```

   Replace `circuit_visualizer.py` with the actual name of your Python file if it differs.

## Example Results

For a circuit with:

- \(R_A = 1\,\text{k}\Omega\)
- \(R_B = 2\,\text{k}\Omega\)
- \(R_{AB} = 2\,\text{k}\Omega\)
- Current injections of 3 mA at node A and 1 mA at node B

The calculated results are:

| Quantity | Result |
|---|---:|
| Node voltage \(V_A\) | 2.800 V |
| Node voltage \(V_B\) | 2.400 V |
| Current through \(R_A\) | 2.800 mA |
| Current through \(R_B\) | 1.200 mA |
| Current from A to B | 0.200 mA |

The matrix residual and KCL checks are approximately zero within numerical precision.

Changing the connecting resistance changes the node voltages and branch currents, demonstrating that the program recalculates the circuit solution.

## Assumptions and Limitations

- The circuit uses ideal DC current sources and resistors.
- The current implementation targets a two-node network with resistors connected between nodes or ground.
- Ground is the reference voltage.
- Inductors, capacitors, AC behavior, and nonlinear components are not modelled.
- The current implementation is not a general-purpose circuit simulator or graphical circuit builder.

## Future Improvements

Possible extensions include:

- Support for larger resistor networks
- More automated circuit validation
- A user-friendly interface for defining circuits
- Additional test cases and visualizations

## Learning Outcomes

This project explores how circuit laws, matrix methods, and Python can work together to solve and verify an engineering problem. It also demonstrates the importance of testing a computational model against electrical principles rather than relying only on its numerical output.
