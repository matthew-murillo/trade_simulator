import pycountry
import sys
import numpy as np
import pandas as pd
import os
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from QGE.equilibrium import equilibrium
    from QGE.data import data
else:
    from QGE.equilibrium import equilibrium
    from QGE.data import data


def run(ctf):
    DIR = os.getcwd()
    if __name__ == "__main__":
        PROJECT = os.path.dirname(os.path.dirname(DIR))
    else:
        PROJECT = os.path.dirname(DIR)
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

            # Removing all own-country tariffs
            d['tau_hat'][np.ix_(importers, importers, sectors)] = 1

        d['taup'] = d['tau_hat']*d['tau']
        counterfactual = equilibrium(d, p)

        return counterfactual, d, p


# d['taup'] = d['tau']
# d['tau_hat'][0, 7, 19] = 1.11

# results = counterfactual
# baseline = d

# VA_hat = np.sum(results['VAnj'], axis=0)/np.sum(baseline['VAnj'], axis=0)
# L_hat = VA_hat/results['w_hat']
# L_pct_change = np.round(((L_hat)-1)*100, 4)

# w_pct_change = np.round(((results['w_hat'])-1)*100, 4)

# results['In']


# ((np.sum(counterfactual['Expenditure'],axis=0)/np.sum(d['Expenditure'],axis=0))-1)*100
# ((np.sum(counterfactual['Im'],axis=0)/np.sum(d['Im'],axis=0))-1)*100


# ctf_xbilat = counterfactual['xbilat'].copy()
# baseline_xbilat = d['xbilat'].copy()
# # Aggregate trade flows
# xbilat_agg_hat = np.sum(ctf_xbilat_foreign, axis=2) / \
#     np.sum(baseline_xbilat_foreign, axis=2)
# xbilat_agg_pct_change = np.round(((xbilat_agg_hat)-1)*100, 4)
# np.fill_diagonal(xbilat_agg_pct_change, 0)
# # Country specific
# df = pd.DataFrame()
# df['country'] = p['c']
# df['sector'] = "selection"
# df['trade_flow'] = xbilat_agg_pct_change[p['c'] == 'ARG', :].flatten()


# sector_filter = selected_sector
# # Aggregate trade flows
# xbilat_hat = ctf_xbilat / baseline_xbilat
# xbilat_pct_change = np.round(((xbilat_hat)-1)*100, 4)
# for j in range(p['J']):
#     np.fill_diagonal(xbilat_pct_change[:, :, j], 0)
# # replace nan with 0
# xbilat_pct_change = np.nan_to_num(xbilat_pct_change)
# np.max(xbilat_pct_change)
# np.min(xbilat_pct_change)

# # Country specific
# df = pd.DataFrame()
# df['country'] = p['c']
# df['sector'] = selected_sector
# df['trade_flow'] = xbilat_pct_change[p['c'] == selected_option,
#                                      :, p['s'] == selected_sector].flatten()

# fig = plot_trade_map(
#     df, selected_option, sector=sector_filter)
# st.plotly_chart(fig, use_container_width=True)
# plot_trade_map(df, sector=None, flow_label="Trade Flow",
#                title="Trade Flows by Country")


# """
#     Plots a choropleth world map of trade flows by country (and optionally by sector).

#     Parameters:
#     - df: DataFrame with columns ['country' (ISO alpha-3), 'sector', 'trade_flow']
#     - sector: If provided, filters the map to a specific sector
#     - flow_label: Label for the colorbar and hover info
#     - title: Plot title

#     Returns:
#     - A Plotly Figure object
#     """


# # pd.DataFrame(counterfactual['Expenditure'])
# # pd.DataFrame(counterfactual['Im'])
# # pd.DataFrame(d['Expenditure'])
# # pd.DataFrame(d['Im'])
# # go_hat = x['GO']/d['GO']
# # q_hat = go_hat / x['P_hat']
# # go_pct_change = np.round(((go_hat)-1)*100, 4)
# # pn_pct_change = np.round(((x['P_hat'])-1)*100, 4)
# # q_pct_change = np.round(((q_hat)-1)*100, 4)

# # # Country specific
# # go_pct_change = go_pct_change[:, p['c'] == 'ARG']
# # pn_pct_change = pn_pct_change[:, p['c'] == 0]
# # q_pct_change = q_pct_change[:, p['c'] == 0]

# # x.keys()
