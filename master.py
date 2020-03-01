# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import yaml as yaml

from src.customer_rfm import customer_rfm

print("Processing : Loading configuration file")
config = yaml.safe_load(open(
    r"C:\Users\adepup\Documents\Prav-Development\Research\github\customer_loyalty\config\config.yaml"))
n_clusters = config['parameters']['n_clusters']

rfm = customer_rfm()     
products = rfm.read_source_products_file(config)   

transactions_holdout = rfm.transactions_rfm(config, products)
transactions_holdout = rfm.frequency_clusters(transactions_holdout, n_clusters)

confusion_matrix = pd.crosstab(transactions_holdout['frequency_cluster'], transactions_holdout['frequency_holdout_cluster'], rownames=['Actual'], colnames=['Predicted'])
print(confusion_matrix)


"""
Clusters Interpretation

Clusters are calibrated in ascending order i.e. higher the cluster number, more frequencies
Actual vs Predicted Clusters
Cross tab gives number of customers moving among clusters

Good : Customer moving from lower cluster to higher cluster, eg: 1,143 customers moving from cluster 0 to cluster 1
Bad : Customer moving from higher cluster to lower cluster, eg: 2,062 clustomers moving from cluster 1 to cluster 0
"""


"""
Productionisation
    1. Implement logic on how to change parameters from config file
        It can be within data pipeline workflow
        Create a web app for config yaml file updates
    2. Write final outputs into database
        Maintain audit log datetime in database for each model run
        create visualisations to compare different model runs
"""