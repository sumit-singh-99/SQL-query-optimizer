# visualizer.py

import matplotlib.pyplot as plt
import networkx as nx


def visualize_ast(ast):
    """
    Visualizes the Abstract Syntax Tree (AST) using networkx and matplotlib.
    """
    if not ast:
        print("No AST to visualize.")
        return

    graph = nx.DiGraph()
    node_count = [0]

    def add_nodes_edges(node, parent=None):
        node_id = node_count[0]
        node_count[0] += 1
        label = f"{node['type']}\n{node.get('value', '')}"
        graph.add_node(node_id, label=label)

        if parent is not None:
            graph.add_edge(parent, node_id)

        for child in node.get("children", []):
            add_nodes_edges(child, node_id)

    add_nodes_edges(ast)

    pos = nx.spring_layout(graph)
    labels = nx.get_node_attributes(graph, 'label')
    nx.draw(graph, pos, labels=labels, with_labels=True, node_color='skyblue',
            node_size=3000, font_size=9, font_weight='bold', arrows=True)

    plt.title("Abstract Syntax Tree (AST)")
    plt.tight_layout()
    plt.show()


def print_tree_structure(ast, indent=0):
    """
    Prints a tree-style structure of the AST in the console (text-based visualization).
    """
    if not ast:
        print("No AST to print.")
        return

    print(' ' * indent + f"- {ast['type']}: {ast.get('value', '')}")
    for child in ast.get("children", []):
        print_tree_structure(child, indent + 4)
