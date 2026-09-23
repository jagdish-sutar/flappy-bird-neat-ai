from __future__ import print_function

import copy
import warnings

import matplotlib.pyplot as plt
import numpy as np
import graphviz


# ============================================================
# PLOT FITNESS
# ============================================================

def plot_stats(
    statistics,
    ylog=False,
    view=False,
    filename="fitness.svg"
):
    """
    Plot average and best fitness over generations.
    """

    generation = range(
        len(statistics.most_fit_genomes)
    )

    best_fitness = [
        genome.fitness
        for genome in statistics.most_fit_genomes
    ]

    avg_fitness = np.array(
        statistics.get_fitness_mean()
    )

    stdev_fitness = np.array(
        statistics.get_fitness_stdev()
    )

    plt.figure()

    plt.plot(
        generation,
        avg_fitness,
        "b-",
        label="Average"
    )

    plt.plot(
        generation,
        avg_fitness - stdev_fitness,
        "g--",
        label="-1 SD"
    )

    plt.plot(
        generation,
        avg_fitness + stdev_fitness,
        "g--",
        label="+1 SD"
    )

    plt.plot(
        generation,
        best_fitness,
        "r-",
        label="Best"
    )

    plt.title(
        "Flappy Bird NEAT Fitness"
    )

    plt.xlabel(
        "Generation"
    )

    plt.ylabel(
        "Fitness"
    )

    plt.grid()

    plt.legend(
        loc="best"
    )

    if ylog:

        plt.gca().set_yscale(
            "symlog"
        )

    plt.savefig(
        filename
    )

    if view:

        plt.show()

    plt.close()


# ============================================================
# PLOT SPECIES
# ============================================================

def plot_species(
    statistics,
    view=False,
    filename="species.svg"
):
    """
    Plot species population over generations.
    """

    species_sizes = (
        statistics.get_species_sizes()
    )

    if not species_sizes:

        warnings.warn(
            "No species data available."
        )

        return

    num_generations = len(
        species_sizes
    )

    curves = np.array(
        species_sizes
    ).T

    fig, ax = plt.subplots()

    ax.stackplot(
        range(num_generations),
        *curves
    )

    plt.title(
        "NEAT Species Evolution"
    )

    plt.ylabel(
        "Population"
    )

    plt.xlabel(
        "Generation"
    )

    plt.savefig(
        filename
    )

    if view:

        plt.show()

    plt.close()


# ============================================================
# DRAW NEURAL NETWORK
# ============================================================

def draw_net(
    config,
    genome,
    view=False,
    filename="network",
    node_names=None,
    show_disabled=True,
    prune_unused=False,
    node_colors=None,
    fmt="svg"
):
    """
    Draw the neural network represented by a genome.
    """

    if node_names is None:

        node_names = {}

    if node_colors is None:

        node_colors = {}

    node_attrs = {
        "shape": "circle",
        "fontsize": "9",
        "height": "0.2",
        "width": "0.2",
    }

    dot = graphviz.Digraph(
        format=fmt,
        node_attr=node_attrs
    )

    # --------------------------------------------------------
    # INPUT NODES
    # --------------------------------------------------------

    inputs = set()

    for key in config.genome_config.input_keys:

        inputs.add(key)

        name = node_names.get(
            key,
            str(key)
        )

        attrs = {
            "style": "filled",
            "shape": "box",
            "fillcolor": node_colors.get(
                key,
                "lightgray"
            ),
        }

        dot.node(
            name,
            _attributes=attrs
        )

    # --------------------------------------------------------
    # OUTPUT NODES
    # --------------------------------------------------------

    outputs = set()

    for key in config.genome_config.output_keys:

        outputs.add(key)

        name = node_names.get(
            key,
            str(key)
        )

        attrs = {
            "style": "filled",
            "fillcolor": node_colors.get(
                key,
                "lightblue"
            ),
        }

        dot.node(
            name,
            _attributes=attrs
        )

    # --------------------------------------------------------
    # DETERMINE USED NODES
    # --------------------------------------------------------

    if prune_unused:

        connections = set()

        for connection in genome.connections.values():

            if (
                connection.enabled
                or show_disabled
            ):

                connections.add(
                    (
                        connection.key[0],
                        connection.key[1]
                    )
                )

        used_nodes = copy.copy(
            outputs
        )

        pending = copy.copy(
            outputs
        )

        while pending:

            new_pending = set()

            for a, b in connections:

                if (
                    b in pending
                    and a not in used_nodes
                ):

                    new_pending.add(a)

                    used_nodes.add(a)

            pending = new_pending

    else:

        used_nodes = set(
            genome.nodes.keys()
        )

    # --------------------------------------------------------
    # HIDDEN NODES
    # --------------------------------------------------------

    for node in used_nodes:

        if (
            node in inputs
            or node in outputs
        ):

            continue

        attrs = {
            "style": "filled",
            "fillcolor": node_colors.get(
                node,
                "white"
            ),
        }

        dot.node(
            str(node),
            _attributes=attrs
        )

    # --------------------------------------------------------
    # CONNECTIONS
    # --------------------------------------------------------

    for connection in genome.connections.values():

        if (
            not connection.enabled
            and not show_disabled
        ):

            continue

        input_node, output_node = (
            connection.key
        )

        if prune_unused:

            if (
                input_node not in used_nodes
                and input_node not in inputs
            ):

                continue

            if (
                output_node not in used_nodes
                and output_node not in outputs
            ):

                continue

        a = node_names.get(
            input_node,
            str(input_node)
        )

        b = node_names.get(
            output_node,
            str(output_node)
        )

        style = (
            "solid"
            if connection.enabled
            else "dotted"
        )

        color = (
            "green"
            if connection.weight > 0
            else "red"
        )

        width = str(
            0.1
            + abs(
                connection.weight / 5.0
            )
        )

        dot.edge(
            a,
            b,
            _attributes={
                "style": style,
                "color": color,
                "penwidth": width,
            }
        )

    dot.render(
        filename,
        view=view
    )

    return dot