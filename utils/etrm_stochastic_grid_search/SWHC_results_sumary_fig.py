from matplotlib import pyplot as plt
import pandas as pd
import numpy as np


# summary path to csv
csvpath = '/home/gabriel/Documents/summary_table_SWHC.csv'

methods = []
method_dict_list = []
with open(csvpath, 'r') as rfile:

    for i, line in enumerate(rfile):
        line = line.strip('\n')
        ln = line.split(',')
        if i == 0:
            columns = ln
        else:
            dict = {}
            methods.append(ln[0])
            print(ln[1:], columns[1:])
            for i, c in zip(ln[1:], columns[1:]):
                print(i)
                print(c)
                if i != '':
                    dict[c] = float(i)
                else:
                    dict[c] = np.nan
            method_dict_list.append(dict)


print(methods)
print(method_dict_list)

fig, axs = plt.subplots(1, 1, figsize=(9, 3), sharey=True, sharex=True)
markers = ['d', 'o',  '8', 's', 'P', 'X', 'D', '>', '<', '^','*']
for meth, d, m in zip(methods, method_dict_list, markers):
    names = d.keys()
    values = d.values()
    print(names, values)
    axs.scatter(names, values, label=meth, marker=m, s=100, edgecolor='black')
box = axs.get_position()
axs.set_position([box.x0, box.y0, box.width*0.65, box.height])
axs.set_xlabel('Eddy Covariance Tower Site', size=12)
axs.set_ylabel('SWHC (mm)', size=12)
fig.suptitle('SWHC Results Summary', size=15)
plt.legend(loc='center left', bbox_to_anchor= (1, 0.5), borderaxespad=0, frameon=False)
plt.grid()
plt.show()

#
# # for each method, make a dict = {'Ses': value, 'Seg': value...}
#
