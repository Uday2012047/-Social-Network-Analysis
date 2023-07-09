import networkx as nx
import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics as ep
import matplotlib.pyplot as plt
import numpy as np
from networkx.classes.function import common_neighbors
from collections import defaultdict
import random
import cdlib
from networkx.algorithms.components.connected import connected_components
import time
# from python_files import adjacency_list, graph_generator_function
import pandas as pd
import json

import gzip
import csv




my_filename ='./data/test1/email-Enron.txt.gz'

with gzip.open(my_filename, 'rt') as gz_file:
    data = gz_file.read() # read decompressed data
    with open(my_filename[:-3], 'wt') as out_file:
         out_file.write(data) # write decompressed data