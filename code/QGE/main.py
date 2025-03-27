import sys
import numpy as np
import pandas as pd
import os
from QGE.equilibrium import equilibrium
from QGE.data import data


def run(ctf):
    CURRENT = os.path.dirname(os.path.abspath(__file__))
    PROJECT = os.path.dirname(os.path.dirname(CURRENT))
    DATA = os.path.join(PROJECT, 'data')
    OUTPUT = os.path.join(PROJECT, 'output')

    BASELINE = 0

    if BASELINE:
        # Calibrate baseline data
        [p, d] = data(DATA, OUTPUT)
        np.save(os.path.join(OUTPUT, 'p.npy'), p)
        np.save(os.path.join(OUTPUT, 'baseline', 'd.npy'), d)

        baseline = equilibrium(d, p)

        np.save(os.path.join(OUTPUT, 'baseline', 'baseline.npy'), baseline)

    else:
        # Load baseline data
        p = np.load(os.path.join(OUTPUT, 'p.npy'), allow_pickle=True).item()
        d = np.load(os.path.join(OUTPUT, 'baseline', 'd.npy'),
                    allow_pickle=True).item()
        baseline = np.load(os.path.join(OUTPUT, 'baseline',
                                        'baseline.npy'),    allow_pickle=True).item()
        d.update({
            'X': baseline['X'],
            'GO': baseline['GO'],
            'Expenditure': baseline['Expenditure'],
            'pi': baseline['pi'],
            'VAnj': baseline['VAnj'],
            'In': baseline['In'],
            'xbilat': baseline['xbilat'],
            'Im': baseline['Im'],
            'Ex': baseline['Ex'],
        })
        p.update({'tol': 1e-6})

        # Check that equilibrium converges in one iteration
        # output = equilibrium(d, p)
        # if output['it'] > 1:
        #     raise ValueError(
        #         f"Equilibrium did not converge in one iteration: {output['it']}")
        # else:
        #     print('Passed')

        # Counterfactual
        for rule in ctf:
            # Counterfactual tariffs
            importers = ctf[rule][0]['importer_indices']
            exporters = ctf[rule][0]['exporter_indices']
            sectors = ctf[rule][0]['sector_indices']
            free_trade = ctf[rule][0]['free_trade']
            tau_hat = ctf[rule][0]['tariff_change']
            tau_hat = 1 + tau_hat/100

            d['tau_hat'][np.ix_(importers, exporters, sectors)] = tau_hat

            # If free trade, set tau_hat to 1/tau
            if free_trade:
                d['tau_hat'][np.ix_(importers, exporters, sectors)] = 1 / \
                    d['tau'][np.ix(importers, exporters, sectors)]

            for i in importers:
                for s in sectors:
                    d['tau_hat'][i, i, s] = 1

        d['taup'] = d['tau_hat']*d['tau']
        counterfactual = equilibrium(d, p)

        return counterfactual, d, p
