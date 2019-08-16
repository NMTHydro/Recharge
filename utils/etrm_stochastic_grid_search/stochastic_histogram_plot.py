# ===============================================================================
# Copyright 2019 Jan Hendrickx and Gabriel Parrish
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================
import yaml
import os
from matplotlib import pyplot as plt
import numpy as np
# ============= standard library imports ========================

cum_days = '1'
sitename = 'vcp'
sitecode = 'Vcp'

root = '/Users/dcadol/Desktop/academic_docs_II/calibration_approach/mini_model_outputs_II/{}/calibration_output'.format(sitename)

# # for eta
# cum_dir = '{}_cum_eta_{}day'.format(sitename, cum_days)
# for rzsm
# cum_dir = '{}_non_cum_rzsm'.format(sitename)
cum_dir = '{}_rzsm'.format(sitename)
cum_dir = '{}_{}day_eta'.format(sitename, cum_days)

chimin_path = os.path.join(root, cum_dir, 'US-{}_chimin_cum_eta_{}.yml'.format(sitecode, cum_days))
resid_path = os.path.join(root, cum_dir, 'US-{}_resid_cum_eta_{}.yml'.format(sitecode, cum_days))
# chimin_path = os.path.join(root, cum_dir, 'US-{}_chimin_non_cum_rzsm.yml'.format(sitecode))
# resid_path = os.path.join(root, cum_dir, 'US-{}_resid_non_cum_rzsm.yml'.format(sitecode, cum_days))

# name = 'US-{}_{}day'.format(sitecode, cum_days)
name = 'US-{}_rzsm'.format(sitecode)
taw = '250'

with open(resid_path, 'r') as rfile:
    resid_dict = yaml.load(rfile)
with open(chimin_path, 'r') as rfile:
    chimin_dict = yaml.load(rfile)

# ==== Chimin Dict Data ====
parameter_lst = chimin_dict['param_lst']
chi_list = chimin_dict['chi_lst']
delta_chi = chimin_dict['delta_chi']
num_obs = chimin_dict['number_of_observations']

# === Resid Dict Data ====
# retrieve the optimal TAW from the Chi_min plot
residuals = resid_dict[taw][1]
print residuals
print 'residuals'
residuals = np.asarray(residuals)
print residuals
# residuals = residuals[(residuals > -100) & (residuals < 100)]
#
# print 'plotting Histogram'
# fig1, ax1 = plt.subplots()
# ax1.hist(residuals, bins=50, color='{}'.format('blue'))
# ax1.set_title('Normalized Residuals for Site: {}'.format(name))
# # plt.xlim(-20, 5)
# plt.savefig('{}/{}/{}_hist_{}_cum.png'.format(root, cum_dir, name, taw))
# plt.show()
#
# print 'residuals \n', residuals
#
# zeroslst = [i for i in residuals if i == 0.0]
# print 'zeros lst \n', zeroslst
# print len(zeroslst)
#
# print 'plotting boxplot'
# fig2, ax2 = plt.subplots()
# ax2.boxplot(residuals, notch=True)
# ax2.set_title('Normalized Residuals for Site: {}'.format(name))
# plt.savefig('{}/{}/{}_box_{}_cum.png'.format(root, cum_dir, name, taw))
# plt.show()


# ax3 = plt.subplot(121)
# ax3.hist(residuals, bins=50, color='{}'.format('blue'))
# ax3.set_ylabel('Residual Count for {} Day Cumulative'.format(cum_days))
# ax3.set_xlabel('Normalized Residual')
#
# ax4 = plt.subplot(122)
# ax4.boxplot(residuals, notch=True, vert=False)
# ax4.set_yticklabels([])
# ax4.set_xlabel('Normalized Residual')
#
# plt.title('Normalized Residuals for Site: {}'.format(name))
# plt.show()

fig, (ax5, ax6) = plt.subplots(1, 2, figsize=(12, 6))

fig.suptitle('Normalized Residuals for Site: {}'.format(name))

ax5.hist(residuals, bins=50, color='{}'.format('blue'))
ax5.set_ylabel('Residual Count for {} Day Cumulative'.format(cum_days))
ax5.set_xlabel('Normalized Residual')

# # Not applicable for RZSM
# if cum_days == '1':
#     ax5.set_xlim(-25, 4)
# elif cum_days == '7':
#     ax5.set_xlim(-12, 3)
# elif cum_days == '14':
#     ax5.set_xlim(-7, 3)

ax6.boxplot(residuals, notch=True, vert=False)
ax6.set_yticklabels([])
ax6.set_xlabel('Normalized Residual')

# # Not applicable for RZSM
# if cum_days == '1':
#     ax6.set_xlim(-25, 4)
# elif cum_days == '7':
#     ax6.set_xlim(-12, 3)
# elif cum_days == '14':
#     ax6.set_xlim(-7, 3)

plt.savefig('{}/{}/{}_boxhist_{}_cum.png'.format(root, cum_dir, name, taw))
plt.show()