import pandas as pd
import os
import numpy as np
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

root = '/media/gabriel/Seagate_Blue/jpl_research/jpl_WE_2012/SWHC_initial_condition'

sg_1k_1k = pd.read_csv(os.path.join(root,'we_depletions_sg_SWHC1000_INIDEP1000.csv'), parse_dates=True)
sg_600_600 = pd.read_csv(os.path.join(root, 'we_depletions_sg_SWHC600_INIDEP600.csv'), parse_dates=True)
sg_600_300 = pd.read_csv(os.path.join(root,'we_depletions_sg_SWHC600_INIDEP300.csv'), parse_dates=True)
sg_600_150 = pd.read_csv(os.path.join(root, 'we_depletions_sg_SWHC600_INIDEP150.csv'), parse_dates=True)

print sg_1k_1k.head()

plt.plot([1,2,3], [3, 5,7])
plt.show()

vcm_600_600 = 'we_depletions_vcm_SWHC600_INIDEP600.csv'
vcm_600_300 = 'we_depletions_vcm_SWHC600_INIDEP300.csv'
vcm_600_150 = 'we_depletions_vcm_SWHC600_INIDEP150.csv'

print(sg_600_600['date'])

plt.scatter(sg_600_150['date'].to_list(), sg_600_150['depletion'].to_list(), label='sg')
plt.grid()
plt.legend()
plt.show()
plt.savefig(os.path.join(root, 'testfig.png'))

# fig, (ax0, ax1, ax2, ax3) = plt.subplots(nrows=4)
#
# ax0.plot(sg_600_150['date'], sg_600_150['depletion'], label='Sg SWHC: 600, In. Dep: 150')
# ax1.plot(sg_600_300['date'], sg_600_300['depletion'], label='Sg SWHC: 600, In. Dep: 300')
# ax2.plot(sg_600_600['date'], sg_600_600['depletion'], label='Sg SWHC: 600, In. Dep: 600')
# ax3.plot(sg_1k_1k['date'], sg_1k_1k['depletion'], label='Sg SWHC: 1,000, In. Dep: 1,000')
#
# plt.grid()
# plt.legend()
# plt.show()