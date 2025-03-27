import pandas as pd
import numpy as np
import os
DIR = os.getcwd()
PROJECT = os.path.dirname(os.path.dirname(DIR))
DATA = os.path.join(PROJECT, "data")
OUTPUT = os.path.join(PROJECT, "output")

data = pd.read_csv(os.path.join(DATA, "2020_SML.csv"), index_col=0)
data = data.loc[~data.index.str.contains("OUT|TLS"), :]
data = data.loc[:, ~data.columns.str.contains("OUT|TLS")]

data.sum().sum()

dictionary = pd.read_excel(os.path.join(DATA, "dictionary.xlsx"))

country = dictionary['country'].dropna()
sector = dictionary['sector'].dropna()
fd = dictionary['fd'].dropna()


N = len(country)
J = len(sector)
F = len(fd)


country_id = list(country) * J
sector_id = np.repeat(sector, N)

IO_id = [f"{c}_{s}" for c, s in zip(country_id, sector_id)]
FD_id = [f"{c}_{f}" for c, f in zip(np.repeat(country, F), ["FD"]*F*N)]

IO = data.iloc[0:N*J, 0:N*J]
IO = IO.reindex(index=IO_id, columns=IO_id)
# Setting the diagonal to .01 in all zero expenditure rows
zero_sum_indices = IO.sum(axis=1)[IO.sum(axis=1) == 0].index
IO.loc[zero_sum_indices, zero_sum_indices] = .01

FD = data.iloc[0:N*J, N*J:]
FD.columns = FD_id
FD = FD.groupby(FD.columns, axis=1, sort=False).sum()
FD = FD.reindex(index=IO.index)

VA = pd.DataFrame(data.iloc[-1, :]).transpose()
VA = VA.reindex(columns=IO.columns)


MRIO = pd.concat([pd.concat([IO, VA], axis=0), FD], axis=1)
MRIO.fillna(0, inplace=True)

# MRIO.to_csv(os.path.join(OUTPUT, "data", "MRIO.csv"))
