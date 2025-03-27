import numpy as np


def EX(w_hat, pi, p, d):

    Pi_mat = np.transpose(pi, (0, 2, 1))        # (N, J, N)
    Tau_mat = np.transpose(d['taup'], (0, 2, 1))  # (N, J, N)
    G_mat = np.transpose(p['G'], (0, 2, 1))     # (J, J, N)

    M_mat = np.zeros((p['N'], p['J'], p['N'], p['J']))

    for j in range(p['J']):
        # Get G_mat[j, :, :] → shape (p['J'], p['N']) in NumPy
        # MATLAB reshapes this in column-major order to (1, p.J, p.N)
        G_slice = G_mat[j, :, :]               # shape (p['J'], p['N'])
        # matches MATLAB reshape
        G_reshaped = np.reshape(G_slice, (1, p['J'], p['N']), order='F')

        # Now broadcast multiply (p['N'], p['J'], p['N']) * (1, p['J'], p['N'])
        M_mat[:, :, :, j] = Pi_mat * G_reshaped / Tau_mat

    # Now reshape to match MATLAB's linearization (column-major)
    M_mat = M_mat = np.reshape(
        M_mat, (p['N'] * p['J'], p['N'] * p['J']), order='F').T

    # Rt_mat_pre: shape (p.N, p.N, p.J)
    Rt_mat_pre = np.sum(pi * (d['taup'] - 1) / d['taup'], axis=1)[:,
                                                                  np.newaxis, :] * np.eye(p['N'])[:, :, np.newaxis]

    # Concatenate Rt_mat across J horizontally
    Rt_mat = np.hstack([Rt_mat_pre[:, :, j]
                       for j in range(p['J'])])  # shape: (p.N, p.N * p.J)

    # Repeat vertically J times and multiply by alpha reshaped to (J, 1)
    # shape: (p.N * p.J, p.N * p.J)
    Rt_mat = np.tile(Rt_mat, (p['J'], 1)) * p['alpha'].reshape(-1, 1)

    # Leontief matrix
    Leonteiff = np.eye(p['N'] * p['J']) - M_mat - Rt_mat

    # Pre-tax Income vector
    VAn = np.sum(d['VAnj'] * w_hat.T, axis=0)  # (N,)
    In_pre = VAn + p['D']                          # (N,)
    In_vec = np.tile(In_pre, (p['J'], 1)).flatten() * \
        p['alpha'].T.flatten(order='F')  # (J*N,)

    # Solve for output
    X = np.linalg.solve(Leonteiff, In_vec)  # (J*N,)
    X = X.reshape((p['N'], p['J']), order='F').T  # (J, N)

    # Bilateral expenditure matrix
    xbilat_g = np.empty((p['N'], p['N'], p['J']))
    for j in range(p['J']):
        xbilat_g[:, :, j] = X[j, :, np.newaxis] * pi[:, :, j]  # (N, N)

    xbilat = xbilat_g / d['taup']

    # Production by country: sum over importers (axis 0)
    GO = np.sum(xbilat, axis=0).reshape(
        (p['N'], p['J']), order='F').T  # (J, N)

    # Expenditure by country: sum over exporters (axis 1)
    Expenditure = np.sum(xbilat, axis=1).reshape(
        (p['N'], p['J']), order='F').T  # (J, N)

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

    # Post-tax income vector
    R_t = np.sum(np.sum(xbilat * (d['taup'] - 1) / d['taup'], axis=1), axis=1)
    In = In_pre + R_t

    return X, xbilat, In, GO, Expenditure, Im, Ex
