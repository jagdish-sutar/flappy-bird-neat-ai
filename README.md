# 🐦 Flappy Bird NEAT AI

An evolutionary AI agent that learns to play **Flappy Bird using NEAT (NeuroEvolution of Augmenting Topologies)**.

Instead of manually programming the bird's movement, the project evolves neural networks over multiple generations. Each network receives information about the bird and the upcoming pipe, decides whether to **FLAP**, and is rewarded based on how long it survives and how many pipes it passes.

The project also visualizes the evolution of the neural network across generations.

---

## 🧠 How It Works

The AI follows an evolutionary loop:

```text
                 ┌─────────────────────┐
                 │   Flappy Bird Game  │
                 └──────────┬──────────┘
                            │
                            ▼
                  Game State / Inputs
                            │
             ┌──────────────┴──────────────┐
             │                             │
          Bird Y                       Velocity
          Pipe Distance                Gap Distance
             │                             │
             └──────────────┬──────────────┘
                            │
                            ▼
                  ┌─────────────────┐
                  │  NEAT Network   │
                  └────────┬────────┘
                           │
                           ▼
                    ┌────────────┐
                    │   FLAP?    │
                    └─────┬──────┘
                          │
                          ▼
                  Bird interacts
                    with pipes
                          │
                          ▼
                       Fitness
                          │
                          ▼
                 Evolution / Mutation
                          │
                          ▼
                  Next Generation
```

The process repeats until the population evolves networks capable of surviving for extended periods.

---

## 🎯 Neural Network Inputs

Each bird's neural network receives **four inputs**:

| Input             | Description                                                       |
| ----------------- | ----------------------------------------------------------------- |
| **Bird Y**        | The bird's vertical position                                      |
| **Velocity**      | The bird's current vertical velocity                              |
| **Pipe Distance** | Horizontal distance to the next pipe                              |
| **Gap Distance**  | Vertical distance between the bird and the center of the pipe gap |

The network produces one output:

```text
Output > 0.5  → FLAP
Output ≤ 0.5  → DO NOTHING
```

---

## 🧬 NEAT Evolution

The project uses **NEAT — NeuroEvolution of Augmenting Topologies**.

Unlike a fixed neural network, NEAT can evolve both:

* Connection weights
* Neural network topology
* Hidden nodes
* Connections between nodes

The initial configuration starts without hidden nodes, while mutations can add or remove nodes and connections during evolution.

This allows the structure of the neural network itself to evolve alongside its weights.

---

## 🏆 Fitness Function

The AI is evaluated using a simple fitness function:

| Event                    | Fitness |
| ------------------------ | ------: |
| Survive one frame        |  **+1** |
| Successfully pass a pipe | **+10** |
| Die                      |  **−5** |

Therefore, the basic fitness calculation rewards both survival and successful navigation through the pipes.

---

## ⚙️ Training Configuration

The current NEAT configuration uses:

```text
Population Size:       50
Generations:           100

Inputs:                4
Outputs:               1
Initial Hidden Nodes:  0

Activation:            Sigmoid
Network Type:          Feed Forward

Node Add Probability:      0.2
Node Delete Probability:   0.2

Connection Add Probability:    0.5
Connection Delete Probability: 0.5
```

The network can therefore develop more complex topologies as evolution progresses.

---

## 📊 Neural Network Visualization

The best-performing network from each generation can be visualized and saved in the `networks/` directory.

Example:

```text
networks/
├── generation_001.svg
├── generation_010.svg
├── generation_025.svg
├── generation_050.svg
└── generation_100.svg
```

These diagrams allow the evolution of the neural network topology and connection weights to be examined across generations.

### Network Visualization

* **Green connections** represent positive weights.
* **Red connections** represent negative weights.
* **Thicker connections** represent stronger weights.
* **Hidden nodes** can appear as the topology evolves.
* Unused nodes can be removed from the visualization.

See [`networks/README.md`](networks/README.md) for more information.

---

## 📈 Training Statistics

The project also generates visualizations for:

### Fitness

The fitness visualization shows:

* Best fitness
* Average fitness
* Fitness standard deviation

### Species

The species visualization shows how the NEAT population is divided into different species throughout evolution.

Generated files include:

```text
fitness.svg
species.svg
```

---

## 🎮 Game Environment

The game is implemented using **Pygame**.

The environment includes:

* Bird physics
* Gravity
* Jump/flap mechanics
* Pipe generation
* Collision detection
* Animated bird sprites
* Game rendering
* Training HUD

The AI agents are evaluated simultaneously within the game environment.

---

## 💾 Checkpointing

Training checkpoints are automatically created during evolution.

The current configuration saves a checkpoint every **10 generations**.

This makes it possible to preserve the evolutionary state during longer training runs.

---

## 📁 Project Structure

```text
flappy-bird-neat-ai/
│
├── imgs/
│   ├── bg.png
│   ├── ground.png
│   ├── pipe.png
│   ├── bird1.png
│   ├── bird2.png
│   └── bird3.png
│
├── networks/
│   ├── README.md
│   └── generation_*.svg
│
├── flappy_bird_(AI version).py
├── visualize.py
├── config-feedforward.txt
└── README.md
```

---

## 🛠️ Technologies

* **Python**
* **Pygame**
* **NEAT-Python**
* **NumPy**
* **Matplotlib**
* **Graphviz**

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/jagdish-sutar/flappy-bird-neat-ai.git
```

Enter the project directory:

```bash
cd flappy-bird-neat-ai
```

Install the required Python packages:

```bash
pip install pygame neat-python numpy matplotlib graphviz
```

Make sure **Graphviz** is installed and available in your system PATH if you want to generate neural-network diagrams.

---

## ▶️ Run the AI

Start training with:

```bash
python "flappy_bird_(AI version).py"
```

The game window will display the evolutionary training process.

During training, the HUD displays information such as:

```text
Generation
Alive
Best Fitness
Frame
```

---

## 🔬 What This Project Demonstrates

This project demonstrates the practical application of:

* Evolutionary algorithms
* Neuroevolution
* Neural network topology evolution
* Genetic mutation
* Fitness-based selection
* Speciation
* Artificial intelligence agents
* Game-based AI environments
* Neural network visualization

Rather than directly training a neural network with a traditional gradient-descent approach, the project uses **evolutionary selection and mutation to discover increasingly effective network configurations**.

---

## 📌 Future Improvements

Potential extensions include:

* Real-time neural-network visualization during training
* Live visualization of network weights
* Improved fitness shaping
* Best-genome replay mode
* Training/resume from checkpoints
* Training statistics dashboard
* Comparison of different NEAT configurations
* Recording training runs as GIFs or videos

