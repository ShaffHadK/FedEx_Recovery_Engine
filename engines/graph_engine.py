import networkx as nx
import pandas as pd


def build_case_graph(df: pd.DataFrame, signals: dict) -> nx.Graph:
    G = nx.Graph()

    # Add Case Nodes
    for cid in df["case_id"]:
        G.add_node(f"CASE_{cid}", node_type="case")

    # Add Signals
    for cid, sigs in signals.items():
        case_node = f"CASE_{cid}"
        if not G.has_node(case_node):
            continue

        for idx, (name, weight) in enumerate(sigs):
        
            sig_node = f"SIG_{name}_{idx}_{cid}"

            G.add_node(sig_node, node_type="signal", signal=name)
            G.add_edge(
                case_node,
                sig_node,
                weight=float(weight)
            )

    return G


def compute_case_rank(G: nx.Graph) -> dict:
    """
    Returns raw momentum per case by summing connected signal weights.
    """
    momentum = {}

    for node, data in G.nodes(data=True):
        if data.get("node_type") != "case":
            continue

        total_weight = 0.0
        for neighbor in G.neighbors(node):
            edge_data = G.get_edge_data(node, neighbor)
            total_weight += edge_data.get("weight", 0.0)

        momentum[node.replace("CASE_", "")] = total_weight

    return momentum
