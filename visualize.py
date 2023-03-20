import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from math import ceil, sqrt

fig = None
ax = None
cols = None
rows = None

def init_graph(num_axs):
    global fig, axs, cols, rows
    fig = plt.figure()
    cols = ceil(sqrt(num_axs))
    rows = ceil(num_axs/ceil(sqrt(num_axs)))
    axs = np.array([[fig.add_subplot(rows, cols, x+1+(y*cols), projection='3d') for x in range(cols)] for y in range(rows)])
    plt.ion()
    plt.show(block=None)

def clear_axs(idxs):
    for idx in idxs:
        ax = axs[idx//cols, idx%cols]
        ax.cla()
        _format_axes(ax)

def create_graph(axons):
    return nx.Graph(axons)

def _format_axes(ax):
        """Visualization options for the 3D axes."""
        # Turn gridlines off
        ax.grid(False)
        # Suppress tick labels
        for dim in (ax.xaxis, ax.yaxis, ax.zaxis):
            dim.set_ticks([])
        # Set axes labels
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")

def render_graph(idx, graph, axon_activations, node_activations, node_info):
    global fig, axs
    ax = axs[idx//cols, idx%cols]
    # 3d spring layout
    pos = nx.spring_layout(graph, dim=3, seed=1)
    # Extract node and edge positions from the layout
    node_xyz = np.array([pos[v] for v in sorted(graph)])

    node_colors = [(
            -x if x<0 else 0,
            x if x>0 else 0,
            0,
        ) for x in node_activations]
    # Plot the nodes - alpha is scaled by "depth" automatically
    ax.cla()
    ax.scatter(*node_xyz.T, s=100, ec="w", c=node_colors)

    # Plot the edges with colors based on activations
    for i, (u, v, d) in enumerate(graph.edges(data=True)):
        color = (
            -axon_activations[i] if axon_activations[i]<0 else 0,
            axon_activations[i] if axon_activations[i]>0 else 0,
            0,
        )
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], [pos[u][2], pos[v][2]],
                color=color, linewidth=2)

    _format_axes(ax)
    ax.set_title(node_info)

    fig.tight_layout()

    plt.draw()
    plt.pause(0.0001)
