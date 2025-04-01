import numpy as np


def TS(c_hat, P_hat, d, p):
    pi_hat = np.empty((p['N'], p['N'], p['J']))

    for j in range(p['J']):
        c_j = c_hat[j, :]                   # shape: (N,)
        tau_j = d['tau_hat'][:, :, j]       # shape: (N, N)
        P_j = P_hat[j, :]                   # shape: (N,)

        pi_hat[:, :, j] = ((c_j[None, :] * tau_j) /
                           P_j[:, None]) ** (-p['theta'][j])

    # Update trade shares
    pi = d['pi'] * pi_hat  # elementwise multiply

    return pi, pi_hat
