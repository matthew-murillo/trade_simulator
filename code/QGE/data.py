import pandas as pd
import numpy as np
from scipy.sparse import eye, kron
from scipy.linalg import null_space
import os


def data(DATA, OUTPUT):
    # Parameters
    p = {
        'N': 77,
        'J': 45,
        'VA': 1,
        'FD': 1,
        'MISC': 0,
        'tol': 1e-10,
        'v': 0.7,
        'maxit': 1e10,
    }
    p['NJ'] = p['N'] * p['J']
    EXPENDITURES = p['J'] + p['FD']

    # Loading country and sector names
    dictionary = pd.read_csv(os.path.join(DATA, 'dictionary.csv'))
    c = dictionary['country'].dropna()
    s = dictionary['sector'].dropna()

    # Load MRIO
    MRIO = np.genfromtxt(os.path.join(OUTPUT, 'data/MRIO.csv'),
                         delimiter=',', skip_header=1)[:, 1:]

    # Load theta
    theta = np.genfromtxt(os.path.join(
        DATA, 'elasticities.csv'), delimiter=',')  # will change
    theta = np.concatenate([theta, theta[-11:]])

    # Initialize tau
    tau = np.ones((p['N'], p['N'], p['J']))

    # X matrix: shape (NJ, EXPENDITURES * N)
    X = MRIO[:p['NJ'], :]

    # OPERATOR: kron(ones(EXPENDITURES, 1), eye(N))
    OPERATOR = kron(np.ones((EXPENDITURES, 1)), eye(p['N'], format='csr'))

    # Multiply X with OPERATOR (convert to dense for matmul)
    xbilat_g = X @ OPERATOR.toarray()  # Result: shape (NJ, N)

    # Transpose and reshape to (N, N, J)
    xbilat_g = np.reshape(xbilat_g.T, (p['N'], p['N'], p['J']), order='F')

    # Apply tariff adjustment
    xbilat = xbilat_g / tau  # shape: (N, N, J)

    # xbilat[n, i, j]: how much country n sends to country i in sector j

    # Gross Output
    GO = np.sum(MRIO[:, :p['NJ']], axis=0)
    GO = np.reshape(GO, (p['N'], p['J']), order='F').T  # shape: (J, N)
    pd.DataFrame(GO)
    # GO[j, n]: total value of gross output from country m in sector j

    # Factor payments (Value Added)
    VAnj = np.sum(MRIO[p['NJ']: p['NJ'] + p['VA'], :p['NJ']], axis=0)
    VAnj = np.reshape(VAnj, (p['N'], p['J']), order='F').T  # shape: (J, N)
    # VAnj[j, n]: labor compensation from country m in sector j

    # Labor shares
    B = VAnj / GO
    B[np.isnan(B)] = 0
    # B[j, n]: share of gross output allocated to labor

    # Input-output shares
    mbilat = MRIO[:p['NJ'], :p['NJ']]  # shape: (NJ, NJ)
    OPERATOR = kron(eye(p['J'], format='csr'), np.ones((p['N'], 1)))
    mbilat = mbilat.T @ OPERATOR.toarray()  # shape: (NJ, J)

    # Normalize to get IO shares
    M = np.sum(mbilat, axis=1, keepdims=True)  # shape: (NJ, 1)
    gamma_raw = mbilat / M  # shape: (NJ, J)

    # Reshape to (J, N, J) using Fortran order to match MATLAB
    gamma = np.reshape(gamma_raw.T, (p['J'], p['N'], p['J']), order='F')
    # gamma[j, n, i]: share of sector i inputs from country n used in sector j

    # G matrix: input-output coefficients adjusted by labor share
    G = np.zeros((p['J'], p['N'], p['J']))  # shape: (j2, n, j1)

    for j1 in range(p['J']):
        G[:, :, j1] = (1 - B[j1, :]) * gamma[:, :, j1]  # shape: (J, N)

    # Domestic exports (sum over exporters)
    xbilat_d = np.sum(xbilat, axis=0).reshape(
        (p['N'], p['J']), order='F').T  # shape: (J, N)

    # Ensure GO reflects actual sales
    GO = np.maximum(GO, xbilat_d)  # (J, N)
    domsales = GO - xbilat_d      # (J, N)

    # Add domestic sales to diagonals
    for j in range(p['J']):
        xbilat_g[:, :, j] += np.diag(domsales[j, :])

    # Recompute tariff-adjusted bilateral flows
    xbilat = xbilat_g / tau  # (N, N, J)

    # Production by country: sum over importers (axis 0)
    GO = np.sum(xbilat, axis=0).reshape(
        (p['N'], p['J']), order='F').T  # (J, N)

    # Expenditure by country: sum over exporters (axis 1)
    Expenditure = np.sum(xbilat, axis=1).reshape(
        (p['N'], p['J']), order='F').T  # (J, N)

    # Trade deficits
    D = np.sum(Expenditure - GO, axis=0)  # (N,)

    # Trade flows
    xbilat_foreign = xbilat.copy()
    for j in range(p['J']):
        np.fill_diagonal(xbilat_foreign[:, :, j], 0)
    # Exports by country: sum over importers (axis 0)
    Ex = np.sum(xbilat_foreign, axis=0).reshape(
        (p['N'], p['J']), order='F').T  # (J, N)

    # Imports by country: sum over exporters (axis 1)
    Im = np.sum(xbilat_foreign, axis=1).reshape(
        (p['N'], p['J']), order='F').T  # (J, N)

    # Expenditure shares
    X = np.sum(xbilat_g, axis=1, keepdims=True)  # (N, 1, J)
    pi = xbilat_g / X  # (N, N, J)

    # Sectoral expenditures
    X = np.reshape(X, (p['N'], p['J']), order='F').T  # (J, N)

    # Aggregate factor payments
    VAn = np.sum(GO * B, axis=0)  # (N,)

    # Tariff revenues
    Rt = xbilat_g * (tau - 1) / tau  # (N, N, J)

    # Intermediate demand
    xsum = np.sum(xbilat, axis=0)        # (N, J)
    X_m = np.sum(G * xsum[None, :, :], axis=2)  # (J, N)

    # Final consumption shares
    In_pre = VAn + D  # shape: (N,)
    A_pre = (X - X_m) / In_pre[np.newaxis, :]  # shape: (J, N)

    alpha = np.zeros((p['J'], p['N']))

    for n in range(p['N']):
        # Replicate column to match MATLAB's kron(1, ones(1, J))
        A = np.tile(A_pre[:, n][:, np.newaxis], (1, p['J']))  # shape: (J, J)

        null_vec = null_space(A - np.eye(p['J']), rcond=1e-10)

        if null_vec.shape[1] == 0:
            raise ValueError(f"No null space found for country {n}")

        alpha_n = null_vec[:, 0]
        alpha_n = alpha_n / np.sum(alpha_n)
        alpha[:, n] = alpha_n

    # Post-cleaning: clip negative noise and normalize
    alpha[alpha < 0] = 0
    alpha = alpha / np.sum(alpha, axis=0, keepdims=True)

    # Final income
    In = In_pre / np.sum(alpha, axis=0)

    # Store results in d
    d = {
        'X': X,
        'pi': pi,
        'VAnj': VAnj,
        'In': In,
        'xbilat': xbilat,
        'GO': GO,
        'Expenditure': Expenditure,
        'Im': Im,
        'Ex': Ex,
        'w_hat0': np.ones(p['N']),
        'P_hat0': np.ones((p['J'], p['N'])),
        'tau_hat': np.ones((p['N'], p['N'], p['J'])),
        'tau': np.ones((p['N'], p['N'], p['J'])),
        'taup': np.ones((p['N'], p['N'], p['J']))
    }

    # Update p with final calibrated objects
    p.update({
        'B': B,
        'G': G,
        'D': D,
        'alpha': alpha,
        'theta': theta,
        'c': c,
        's': s,
    })

    return p, d
