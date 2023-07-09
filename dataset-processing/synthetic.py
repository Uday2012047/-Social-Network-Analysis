import networkx as nx
import random
import pandas as pd
import os
import shutil
import json

ground_truths = {}

def intial_graph(i,j):
    seed=random.randint(40,47)
    G = nx.LFR_benchmark_graph(250, tau1=3, tau2=1.5, mu=0.1, average_degree=5, min_community=30,seed=seed)
    G.remove_edges_from(nx.selfloop_edges(G))
    for (u, v) in G.edges():
        G.edges[u, v]['weight'] = random.randint(1, 7)
    df = pd.DataFrame([(u, v, d['weight']) for u, v, d in G.edges(data=True)], columns=['source', 'target', 'weight'])
    df.to_csv(f'syn-datasets{i}/graph{j}.csv', index=False)
    communities = {frozenset(G.nodes[v]["community"]) for v in G}
    ground_truth = [list(c) for c in communities]
    ground_truths[i][j] = ground_truth
    

for i in range(1,4):
    folder_name = "syn-datasets"+str(i)
    if os.path.exists(folder_name) and os.path.isdir(folder_name):
        shutil.rmtree(os.getcwd()+'\\'+folder_name)
    os.mkdir(folder_name)
    ground_truths[i]={}
    for j in range(6):
        intial_graph(i,j)

json_object = json.dumps(ground_truths)
with open("groundtruth.json", "w") as outfile:
    outfile.write(json_object)