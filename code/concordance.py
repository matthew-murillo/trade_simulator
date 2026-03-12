import pandas as pd
import numpy as np
import os
DIR = os.getcwd()
PROJECT = os.path.dirname(DIR)
DATA = os.path.join(PROJECT, "data")
OUTPUT = os.path.join(PROJECT, "output")

# Loading the data

isic3_isic31 = pd.read_csv(os.path.join(
    DATA, "ISIC_Rev_3-ISIC_Rev_3_1_correspondence.txt"), dtype=str)[['Rev3', 'Rev31']]
isic31_isic4 = pd.read_csv(os.path.join(DATA, "ISIC31_ISIC4.txt"), dtype=str)[
    ['ISIC31code', 'ISIC4code']]
isic4_isic4agg = pd.read_csv(os.path.join(
    DATA, "isic4_isic4agg.csv"), dtype=str)
sector = pd.read_csv(os.path.join(DATA, "dictionary.csv"),
                     dtype=str)[['sector']].dropna()
data = pd.read_csv(os.path.join(
    DATA, "2840275_B3D44792-0/DataJobID-2840275_2840275_tradesim04022025.csv"), index_col=0).fillna(0)

isic3_isic31['Rev3'] = isic3_isic31['Rev3'].str[:2]
isic3_isic31['Rev31'] = isic3_isic31['Rev31'].str[:2]
isic31_isic4['ISIC31code'] = isic31_isic4['ISIC31code'].str[:2]
isic31_isic4['ISIC4code'] = isic31_isic4['ISIC4code'].str[:2]

isic3_isic31 = isic3_isic31.drop_duplicates()
isic31_isic4 = isic31_isic4.drop_duplicates()

isic3_isic31.rename(columns={'Rev3': 'ISIC3code',
                    'Rev31': 'ISIC31code'}, inplace=True)

isic3_isic4 = pd.merge(isic3_isic31, isic31_isic4)[['ISIC3code', 'ISIC4code']]
isic3_isic4 = isic3_isic4.drop_duplicates()

isic4_isic4agg.rename(columns={'isic4': 'ISIC4code',
                               'isic4_agg': 'ISIC4aggcode'}, inplace=True)
isic3_isic4agg = pd.merge(isic3_isic4, isic4_isic4agg)[
    ['ISIC3code', 'ISIC4aggcode']]
isic3_isic4agg = isic3_isic4agg.drop_duplicates()
isic3_isic4agg.loc[isic3_isic4agg['ISIC3code'] == '02']

# Pivot table

data = data.reset_index().melt(id_vars='V1', var_name='importer',
                               value_name='trade_value').rename(columns={'V1': 'exporter'})
data['exporter_c'] = data['exporter'].str[0:3]
data['exporter_s'] = data['exporter'].str[4:]
data['importer_c'] = data['importer'].str[0:3]
data['importer_s'] = data['importer'].str[4:]

data = data[['exporter_c', 'importer_c', 'importer_s', 'trade_value']]
data = data.groupby(['importer_c', 'exporter_c',
                    'importer_s']).sum().reset_index()
data.loc[data['importer_c'] == data['exporter_c'],
         'trade_value'] = 0  # Dropping self-trade

data = pd.merge(data, isic3_isic4agg, left_on=[
                'importer_s'], right_on=['ISIC4aggcode'], how='left')

data['agg_trade_value'] = data.groupby(['ISIC4aggcode', 'exporter_c', 'importer_c'])[
    'trade_value'].transform('sum')

data['trade_weight'] = data['trade_value'] / data['agg_trade_value']
x = data.loc[(data['ISIC3code'] == '01') & (
    data['exporter_c'] == 'ARG') & (data['importer_c'] == 'USA')]
y = data.loc[(data['ISIC4aggcode'] == 'C10T12') & (
    data['exporter_c'] == 'DEU') & (data['importer_c'] == 'USA')]

x[['importer_c', 'exporter_c', 'ISIC3code', 'ISIC4aggcode', 'trade_weight']]
y[['importer_c', 'exporter_c', 'ISIC3code', 'ISIC4aggcode', 'trade_weight']]
