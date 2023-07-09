import networkx as nx
import networkx.algorithms.community as nx_comm
from cdlib import evaluation
from cdlib import NodeClustering


def conductance(G,comm):
    return evaluation.conductance(G,comm)

def cut_ratio(G,comm):
    return evaluation.cut_ratio(G,comm)

def expansion(G,comm):
    return evaluation.expansion(G,comm)

def modularity(G,comm):
    return evaluation.newman_girvan_modularity(G,comm)

def nmi(comm,ground_truth):
    return evaluation.normalized_mutual_information(comm,ground_truth)

def ari(comm,ground_truth):
    return evaluation.adjusted_rand_index(comm,ground_truth)

def ami(comm,ground_truth):
    return evaluation.adjusted_mutual_information(comm,ground_truth)

def test(G,predicted_communities,true_communities=None):
    results = {}
    results["Modularity"] = modularity(G, predicted_communities)[2]
    results["Conductance"] = conductance(G, predicted_communities)[2]
    results["Expansion"] = expansion(G, predicted_communities)[2]
    results["Cut-Ratio"] = cut_ratio(G, predicted_communities)[2]
    if true_communities:
        results["NMI"] = nmi(predicted_communities, true_communities)[0]
        results["ARI"] = ari(predicted_communities, true_communities)[0]
        results["AMI"] = ami(predicted_communities, true_communities)[0]
    return results


if __name__ == "__main__":
    G = nx.LFR_benchmark_graph(
        n=250, tau1=3, tau2=1.5, mu=0.1, average_degree=5, min_community=20, seed=10)
    communities = {frozenset(G.nodes[v]["community"]) for v in G}
    ground_truth = [list(c) for c in communities]
    communities = nx_comm.louvain_communities(G, seed=123)
    comm = [list(c) for c in communities]
    comm = NodeClustering(comm, graph=None)
    ground_truth = NodeClustering(ground_truth, graph=None)
    print(test(G,comm,ground_truth))
