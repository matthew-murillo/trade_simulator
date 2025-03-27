import numpy as np


def LMC(w_hat, Expenditure, GO, p, d):

    VAnj = p['B'] * GO  # Element-wise multiply, broadcasting over rows

    # Lucas and Alvarez (2008)
    Z = -(np.sum(Expenditure, axis=0).T - np.sum(GO, axis=0).T -
          p['D']) / np.sum(d['VAnj'], axis=0).T

    w_hat = np.multiply(w_hat, (1 + p['v']*np.divide(Z, w_hat)))

    return w_hat, VAnj, Z
