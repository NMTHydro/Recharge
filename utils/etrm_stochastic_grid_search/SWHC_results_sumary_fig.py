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

for meth, d in zip(methods, method_dict_list):
    names = d.keys()
    values = d.values()
    print(names, values)
    axs.scatter(names, values, label=meth)
fig.suptitle('SWHC Results Summary')
plt.legend()
plt.grid()
plt.show()

#
# # for each method, make a dict = {'Ses': value, 'Seg': value...}
#
