import os
import sys

import numpy as np


PROJECT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CODE_DIR = os.path.join(PROJECT, 'code')

if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

from QGE.main import run


def test_run_handles_free_trade_with_null_tariff_change():
    ctf = {
        'rule1': [{
            'importer_indices': [0],
            'exporter_indices': [1],
            'sector_indices': [0],
            'free_trade': True,
            'tariff_change': None,
        }]
    }

    output, d, _ = run(ctf)

    assert output['it'] >= 1
    assert d['tau_hat'][0, 1, 0] == 1.0
    assert d['tau_hat'][0, 0, 0] == 1.0


def test_empty_rule_dimensions_expand_to_all_indices():
    ctf = {
        'rule1': [{
            'importer_indices': [],
            'exporter_indices': [1],
            'sector_indices': [0],
            'free_trade': False,
            'tariff_change': 10.0,
        }]
    }

    _, d, _ = run(ctf)

    changed = np.abs(d['tau_hat'][:, 1, 0] - 1.0) > 1e-12
    assert changed.sum() == d['tau_hat'].shape[0] - 1
    assert d['tau_hat'][1, 1, 0] == 1.0


def test_all_rule_entries_are_applied():
    ctf = {
        'rule1': [
            {
                'importer_indices': [0],
                'exporter_indices': [1],
                'sector_indices': [0],
                'free_trade': False,
                'tariff_change': 10.0,
            },
            {
                'importer_indices': [2],
                'exporter_indices': [3],
                'sector_indices': [4],
                'free_trade': False,
                'tariff_change': 20.0,
            },
        ]
    }

    _, d, _ = run(ctf)

    assert d['tau_hat'][0, 1, 0] == 1.1
    assert d['tau_hat'][2, 3, 4] == 1.2
