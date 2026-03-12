import sys
import numpy as np
import pandas as pd
import os
from QGE.equilibrium import equilibrium
from QGE.data import data


def _expand_indices(indices, size):
    if indices:
        return indices
    return list(range(size))


def _iter_counterfactual_rules(ctf, p):
    for rule_entries in ctf.values():
        entries = rule_entries if isinstance(rule_entries, list) else [rule_entries]
        for entry in entries:
            yield {
                'importers': _expand_indices(entry.get('importer_indices', []), p['N']),
                'exporters': _expand_indices(entry.get('exporter_indices', []), p['N']),
                'sectors': _expand_indices(entry.get('sector_indices', []), p['J']),
                'free_trade': entry.get('free_trade', False),
                'tariff_change': entry.get('tariff_change', 0.0),
            }


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
        for rule in _iter_counterfactual_rules(ctf, p):
            importers = rule['importers']
            exporters = rule['exporters']
            sectors = rule['sectors']

            if rule['free_trade']:
                d['tau_hat'][np.ix_(importers, exporters, sectors)] = 1 / \
                    d['tau'][np.ix_(importers, exporters, sectors)]
            else:
                tariff_change = rule['tariff_change']
                if tariff_change is None:
                    tariff_change = 0.0
                d['tau_hat'][np.ix_(importers, exporters, sectors)] = 1 + \
                    tariff_change / 100

            for importer in importers:
                for sector in sectors:
                    d['tau_hat'][importer, importer, sector] = 1

        d['taup'] = d['tau_hat']*d['tau']
        counterfactual = equilibrium(d, p)

        return counterfactual, d, p
