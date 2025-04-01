import numpy as np


def EP(w_hat, P_hat, d, p):

    P_err = 1
    it = 1

    while P_err > p['tol'] and it < p['maxit']:
        # Log wage and prices
        lw_hat = np.log(w_hat)              # (N, 1)
        lP_hat = np.log(P_hat)              # (J, N)

        # Labor cost term
        lw_hat_term = lw_hat.T * p['B']     # (1, N) * (J, N) → (J, N)

        # Intermediate input term
        lP_hat_term = np.sum(p['G'] * lP_hat[:, :, None], axis=0).T  # (J, N)

        # Total cost change
        c_hat = np.exp(lw_hat_term + lP_hat_term)  # (J, N)

        # Trade costs adjusted by production costs
        pni_hat = np.empty((p['N'], p['N'], p['J']))
        for j in range(p['J']):
            c_j = c_hat[j, :]  # (N,)
            tau_j = d['tau_hat'][:, :, j]  # (N, N)
            pni_hat[:, :, j] = (c_j[None, :] * tau_j) ** (-p['theta'][j])

        # Price index
        log_sum = np.log(np.sum(d['pi'] * pni_hat, axis=1))  # (N, J)
        P_hat1 = np.exp(log_sum.T / (-p['theta'][:, None]))  # (J, N)

        P_err = np.max(np.abs(P_hat1 - P_hat))
        it += 1

        P_hat = P_hat1.copy()

    Pn_hat = np.prod(P_hat**p['alpha'], axis=0)

    return P_hat, c_hat, Pn_hat
