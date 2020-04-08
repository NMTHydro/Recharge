import os
import numpy as np
import pandas as pd

def depletion_calc(inidep, swhc, df):
    """Does a Wang-Erlandsson deplietion but takes into account the SWHC and the initial depletion condition."""

    # dates = df.index.to_list()
    # deficit = df['deficit'].to_list()
    et = df['eta']
    precip = df['precip']

    depletion = []
    # recharge/runoff i.e. depletion greater than zero
    rr = []
    depletion_condition = None
    for i, e, p in zip(range(len(et)), et, precip):

        # todays depletion
        d = e - p

        if i == 0:
            # the initial depletion
            day_one_depletion = inidep + d
            depletion.append(day_one_depletion)
            depletion_condition = day_one_depletion
            rr.append(0)
        else:
            depletion_condition += d
            if depletion_condition <= 0:
                # recharge is any negative depletion
                rr.append(abs(depletion_condition))
                # the depletion is capped at zero since the positive depletion goes to rr
                depletion_condition = 0
            else:
                rr.append(0)
            # the depletion cannot get smaller than the theoretical SWHC
            if depletion_condition >= swhc:
                depletion_condition = swhc
            depletion.append(depletion_condition)

    return depletion, rr

    # === old mistaken version ===
    # dep_list = []
    # temp = None
    # for i, d in enumerate(deficit):
    #     if i == 0:
    #         # the initial depletion
    #         day_one_depletion = inidep + d
    #         temp = day_one_depletion
    #         dep_list.append(temp)
    #     else:
    #         running_dep = temp + d
    #         # a negative depletion is runoff or recharge
    #         if running_dep <= 0:
    #             running_dep = 0.0
    #         # if greater than swhc, we'll just assume the forest died?
    #         if running_dep >= swhc:
    #             running_dep = swhc
    #         dep_list.append(running_dep)
    #         temp = running_dep
    #
    # return dep_list


# Large initial depletion
SWHC = 50

#Initial depletion
inidep = 0

site = 'sg'

root = '/Users/Gabe/Downloads/thesis spreadies'

eta_path = '/Users/Gabe/Downloads/thesis spreadies/{}_eta_interp.csv'.format(site)
precip_path = '/Users/Gabe/Downloads/thesis spreadies/{}_precip_interp.csv'.format(site)

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

# # === output interpolated dfs ===
# eta_df.to_csv('/Users/Gabe/Downloads/thesis spreadies/{}_eta_interp.csv'.format(site))
# precip_df.to_csv('/Users/Gabe/Downloads/thesis spreadies/{}_precip_interp.csv'.format(site))

# join the dataframes
ddf = pd.concat([eta_df, precip_df], axis=1, sort=True)

ddf['cum_eta'] = ddf['eta'].cumsum(skipna=True)
ddf['cum_precip'] = ddf['precip'].cumsum(skipna=True)
ddf['deficit'] = ddf.cum_eta - ddf.cum_precip

# print ddf.head()

ddf['depletion'], ddf['recharge_ro'] = depletion_calc(inidep, swhc=SWHC, df=ddf)

print ddf.head()

ddf.to_csv(os.path.join(root, 'ext_we_depletions_{}_SWHC{}_INIDEP{}.csv'.format(site, SWHC, inidep)))



