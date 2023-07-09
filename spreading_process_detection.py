import time
import networkx as nx
import networkx.algorithms.community as nx_comm
import matplotlib.pyplot as plt
import math
from sklearn.cluster import KMeans
# from metrics import test
import warnings
warnings.simplefilter('ignore')


def get_communities_spreading_process(G):
    Adj_matrix = nx.adjacency_matrix(G).todense().tolist()
    ntimes = 10
    lamda = 0.9
    mu = 0.8

    def run_simulation(G, times, Prob_R, Prob_S, Prob_I):
        temp_Prob_R, temp_Prob_S, temp_Prob_I = Prob_R, Prob_S, Prob_I
        for t in range(1, times+1):
            # calculate Prob_S for every node
            for node in nodes:
                Prob_S[node] = temp_Prob_S[node]
                mult = 1
                for n in nodes:
                    mult *= (1 - lamda * Adj_matrix[n][node] * temp_Prob_I[n])
                Prob_S[node] *= mult
            # calculate Prob_I for every node
            for node in nodes:
                Prob_I[node] = temp_Prob_S[node]
                mult = 1
                for n in nodes:
                    mult *= (lamda * Adj_matrix[n][node] * temp_Prob_I[n])
                Prob_I[node] *= (1 - mult)
                Prob_I[node] += (1 - mu) * temp_Prob_I[node]
            # calculate Prob_R for every node
            for node in nodes:
                Prob_R[node] = mu * temp_Prob_I[node] + temp_Prob_R[node]
            temp_Prob_S, temp_Prob_I, temp_Prob_R = Prob_S, Prob_I, Prob_R
        return temp_Prob_S, temp_Prob_I, temp_Prob_R

    nodes = list(G.nodes())

    Prob_matrix = [[0 for i in range(len(nodes))] for j in range(len(nodes))]

    for node in nodes:
        Prob_R = [0 for _ in range(len(nodes))]
        Prob_S = [mu for _ in range(len(nodes))]
        Prob_I = [0 for _ in range(len(nodes))]

        Prob_I[node] = 1

        Prob_S, Prob_I, Prob_R = run_simulation(
            G, ntimes, Prob_R, Prob_S, Prob_I)

        for n in nodes:
            Prob_matrix[n][node] = Prob_R[n]

    Part_matrix = [[0 for i in range(len(nodes))] for j in range(len(nodes))]
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            if i != j:
                Part_matrix[i][j] = Prob_matrix[i][j]
            else:
                x = 0
                for jj in range(len(nodes)):
                    if jj != i:
                        x += Prob_matrix[i][jj]
                Part_matrix[i][j] = x / (len(nodes)-1)

    means = [0 for _ in range(len(nodes))]
    sds = [0 for _ in range(len(nodes))]

    for i in range(len(nodes)):
        means[i] = sum(Part_matrix[i])/(len(nodes))

    for i in range(len(nodes)):
        x = 0
        for k in range(len(nodes)):
            x += (Part_matrix[i][k] - means[i])*(Part_matrix[i][k] - means[i])
        x /= len(nodes)
        sds[i] = math.sqrt(x)

    Pear_cor = [[0 for i in range(len(nodes))] for j in range(len(nodes))]
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            x = 0
            for k in range(len(nodes)):
                x += (Part_matrix[i][k]-means[i])*(Part_matrix[j][k]-means[j])
            x /= (len(nodes)*sds[i]*sds[j])
            Pear_cor[i][j] = x

    Distance_matrix = [[0 for i in range(len(nodes))]
                       for j in range(len(nodes))]
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            Distance_matrix[i][j] = 1 - Pear_cor[i][j]

    cluster = KMeans(2)
    cluster.fit(Distance_matrix)
    identified_clusters = cluster.fit_predict(Distance_matrix)

    def calcModularity(n):
        cluster = KMeans(n)
        cluster.fit(Distance_matrix)
        identified_clusters = cluster.fit_predict(Distance_matrix)
        # print(identified_clusters)
        clustMat = [[0 for i in range(0)] for j in range(n+1)]
        i = 0
        for id in identified_clusters:
            clustMat[id+1].append(i)
            i += 1

        # print(clustMat)
        mods = nx_comm.modularity(G, clustMat, weight='weight', resolution=1)
        # print(mods)
        return mods

    fv = 5
    for i in range(3, len(nodes)-1):
        prv_mod = calcModularity(i-1)
        cur_mod = calcModularity(i)
        nxt_mod = calcModularity(i+1)
        if (prv_mod <= cur_mod and cur_mod >= nxt_mod):
            fv = i
            break
    cluster = KMeans(fv)
    cluster.fit(Distance_matrix)
    identified_clusters = cluster.fit_predict(Distance_matrix)
    colors = cluster.labels_

    max_num_comm = max(colors)
    communities = [[]for _ in range(max_num_comm+1)]
    for i in range(len(colors)):
        communities[colors[i]].append(i)

    return communities


# for i in range(5):
#     G = nx.LFR_benchmark_graph(n=250, tau1=3, tau2=1.5,
#                                mu=0.1, average_degree=5, min_community=20, seed=10)
#     communities = {frozenset(G.nodes[v]["community"]) for v in G}
#     ground_truth = [list(c) for c in communities]
#     communities = get_communities_spreading_process(G)
