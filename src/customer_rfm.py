# -*- coding: utf-8 -*-
import pandas as pd
from lifetimes.utils import calibration_and_holdout_data
from lifetimes import GammaGammaFitter
from lifetimes import BetaGeoFitter
from sklearn.cluster import KMeans

class customer_rfm():
    '''Customer loyalty RFM implementation using lifetimes package

        Parameters
        ----------
        None
        

        Raises
        ------
        RuntimeError
            None

        Returns
        -------
        source dataframe
            reading source datafile using config parameters
        RFM dataframe
            Calculate RFTM from transactions
        Clusters
            Calculate Frequency clusters
            
        '''
    def __init__(self):
        """
        docstring
        """  
   
    def read_source_products_file(self, config):
        """
        docstring
        """
        self.config = config
        self.products_file = self.config['parameters']['source_file_path']
        self.products = pd.read_csv(self.products_file)
        return self.products
    
    
    def customer_cluster(self, cluster, group, df, ascending=True):
        self.cluster = cluster
        self.group = group 
        self.df = df
        # This step is to generate a sorted index based on the 'group' mean
        self.initial = (self.df.groupby(self.cluster)[self.group] 
                .mean()
                .reset_index()
                .sort_values(by=group, ascending=True)
                .reset_index(drop=True)) 
        # Throwing out the old index as a scoring variable
        self.initial['index'] = self.initial.index 
        del self.initial[self.group]
        #.set_index('index') # Merging with the original DF
        self.final = self.df.merge(self.initial, on=self.cluster)
        # Dropping the cluster scores, and renaming the old index as the cluster
        self.final = (self.final.drop([self.cluster], axis=1)
                .rename(columns={"index":self.cluster})) 
    
        return self.final
    
    def transactions_rfm(self, config, transactions):      
        """
        docstring
        """
        self.calibration_period_end = config['parameters']['calibration_period_end']
        self.observation_period_end = config['parameters']['observation_period_end']

        transactions['trans_date'] = pd.to_datetime(transactions['trans_date'])

        self.transactions_holdout = calibration_and_holdout_data(transactions, 
                                                            'customer_id', 
                                                            'trans_date',
                                                            calibration_period_end = self.calibration_period_end,
                                                            observation_period_end = self.observation_period_end
                                                           )

        self.tr_subset = transactions.loc[(transactions['trans_date'] <= self.calibration_period_end)].groupby('customer_id')['tran_amount'].mean().reset_index()
        self.tr_holdout = transactions.loc[(transactions['trans_date'] > self.calibration_period_end) & (transactions['trans_date'] <= self.observation_period_end)].groupby('customer_id')['tran_amount'].mean().reset_index()

        self.tr_subset.rename(columns={'tran_amount': 'monetary_cal'}, inplace=True)
        self.tr_holdout.rename(columns={'tran_amount': 'monetary_holdout'}, inplace=True)

        self.transactions_holdout = pd.merge(self.transactions_holdout,self.tr_subset, on='customer_id', how='left')
        self.transactions_holdout = pd.merge(self.transactions_holdout,self.tr_holdout, on='customer_id', how='left')

        self.transactions_holdout.fillna(0, inplace=True)
        return self.transactions_holdout

    def frequency_clusters(self, transactions_holdout, n_clusters):
        """
        docstring
        """
        kmeans = KMeans(n_clusters=n_clusters)

        kmeans.fit(transactions_holdout[['frequency_cal']])
        transactions_holdout['frequency_cluster'] = kmeans.predict(transactions_holdout[['frequency_cal']])
        
        transactions_holdout = self.customer_cluster('frequency_cluster', 'frequency_cal', transactions_holdout, True)
  
        kmeans = KMeans(n_clusters=n_clusters)
        
        kmeans.fit(transactions_holdout[['frequency_holdout']])
        transactions_holdout['frequency_holdout_cluster'] = kmeans.predict(transactions_holdout[['frequency_holdout']])        

        transactions_holdout=self.customer_cluster('frequency_holdout_cluster', 'frequency_holdout', transactions_holdout, True)                
        
        return transactions_holdout

