import os
import numpy as np
import pandas as pd

def depletion_calc(inidep, swhc, df):
    """Does a Wang-Erlandsson deplietion but takes into account the SWHC and the initial depletion condition."""

    dates = df.index.to_list()
    deficit = df['deficit'].to_list()

    dep_list = []
    temp = None
    for i, d in enumerate(deficit):
        if i == 0:
            # the initial depletion
            day_one_depletion = inidep + d
            temp = day_one_depletion
            dep_list.append(temp)
        else:
            running_dep = temp + d
            # a negative depletion is runoff or recharge
            if running_dep <= 0:
                running_dep = 0.0
            # if greater than swhc, we'll just assume the forest died?
            if running_dep >= swhc:
                running_dep = swhc
            dep_list.append(running_dep)
            temp = running_dep

    return dep_list



# Large initial depletion
SWHC = 1000

#Initial depletion
inidep = 1000

site = 'sg'

root = '/media/gabriel/Seagate_Blue/jpl_research/jpl_WE_2012/SWHC_initial_condition'

eta_path = '/media/gabriel/Seagate_Blue/jpl_research/jpl_WE_2012/SWHC_initial_condition/{}_eta.csv'.format(site)
precip_path = '/media/gabriel/Seagate_Blue/jpl_research/jpl_WE_2012/SWHC_initial_condition/{}_precip.csv'.format(site)

# === Precip ====
precip_df = pd.read_csv(precip_path, header=0, parse_dates=['date'])
precip_df = precip_df.set_index('date')
precip_df['precip'] = precip_df['value']
precip_df.to_csv(os.path.join(root, 'test.csv'))
# linearly interpolate through N/A
precip_df.interpolate(axis=1, method='linear', inplace=True)

# === ETa ====
eta_df = pd.read_csv(eta_path, header=0, parse_dates=['date'])
eta_df = eta_df.set_index('date')
# Need to reindex for missing ETa values
eta_df = eta_df.asfreq('1D', fill_value=np.nan)
eta_df['eta'] = eta_df['value']
# linearly interpolate through N/A
eta_df = eta_df.interpolate(method='linear')

# join the dataframes
ddf = pd.concat([eta_df, precip_df], axis=1, sort=True)

ddf['cum_eta'] = ddf['eta'].cumsum(skipna=True)
ddf['cum_precip'] = ddf['precip'].cumsum(skipna=True)
ddf['deficit'] = ddf.cum_eta - ddf.cum_precip

# print ddf.head()

ddf['depletion'] = depletion_calc(inidep, swhc=SWHC, df=ddf)

print ddf.head()

ddf.to_csv(os.path.join(root, 'we_depletions_{}_SWHC{}_INIDEP{}.csv'.format(site, SWHC, inidep)))



