import pandas as pd
import numpy as np
from scipy.sparse import eye, kron
from scipy.linalg import null_space
import os
import sys
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from QGE.EP import EP
    from QGE.TS import TS
    from QGE.EX import EX
    from QGE.LMC import LMC
else:
    from QGE.EP import EP
    from QGE.TS import TS
    from QGE.EX import EX
    from QGE.LMC import LMC


def equilibrium(d, p):
    it = 0
    # Initialize model variables
    w_hat = d['w_hat0'].copy()     # (N, 1)
    P_hat = d['P_hat0'].copy()     # (J, N)
    X = d['X']                     # (J, N)
    pi = d['pi']                   # (N, N, J)
    D = p['D']                     # (N,)
    Z_err = 1
    while Z_err > p['tol']:

        # Prices
        [P_hat, c_hat, Pn_hat] = EP(w_hat, P_hat, d, p)

        # Trade shares
        [pi, pi_hat] = TS(c_hat, P_hat, d, p)

        # Expenditures
        [X, xbilat, In, GO, Expenditure, Im, Ex] = EX(w_hat, pi, p, d)

        # LMC
        [w_hat, VAnj, Z] = LMC(w_hat, Expenditure, GO, p, d)

        Z_err = sum(abs(Z))
        print('Tolerance = ', Z_err)

        it += 1

    print('Equilibrium converged')

    output = {
        'X': X,
        'pi': pi,
        'VAnj': VAnj,
        'In': In,
        'xbilat': xbilat,
        'w_hat': w_hat,
        'P_hat': P_hat,
        'Pn_hat': Pn_hat,
        'GO': GO,
        'Expenditure': Expenditure,
        'Im': Im,
        'Ex': Ex,
        'D': D,
        'it': it
    }

    # Reorder to 'baseline' keys to match 'd' do it manually

    return output
