# Neural Network Evolution

This folder contains neural network visualizations generated during the training of the Flappy Bird AI.

Each diagram represents the **best-performing genome from a particular generation** of the NEAT evolutionary process.

## What the Nodes Represent

### Input Nodes

* **Bird Y** — Vertical position of the bird
* **Velocity** — Current vertical velocity
* **Pipe Distance** — Horizontal distance to the next pipe
* **Gap Distance** — Vertical distance between the bird and the pipe gap

### Output Node

* **FLAP** — Controls whether the bird should flap

## Understanding the Connections

* **Green connections** represent positive weights.
* **Red connections** represent negative weights.
* **Thicker connections** represent stronger weights.
* **Hidden nodes** may appear as NEAT evolves the network topology.
* Disabled or unused connections are excluded from the main visualization.

## Evolution

The diagrams can be compared across generations to observe how the neural network evolves:

```text
Generation 1
     ↓
Initial network
     ↓
Mutation & selection
     ↓
Generation 10
     ↓
New weights / topology
     ↓
Generation 50
     ↓
More refined network
     ↓
Generation 100
     ↓
Final evolved network
```

These visualizations provide a structural view of how NEAT evolves the neural network rather than simply showing the final AI's performance.

