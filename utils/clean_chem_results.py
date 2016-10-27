import pandas as pd
import os


def clean_up_chem_excel(folder):
    excels = os.listdir(folder)
    for excel in excels:
        print 'excel: {}'.format(excel)
        if excel.endswith(".xlsx"):
            xls = pd.read_excel(os.path.join(folder, excel))
            heading = xls.iloc[:5, :]
            df = xls.iloc[6:, :]
            to_drop = 'Cycle'
            df = xls[~xls['title'].isin(to_drop)]

            data = xls.iloc[6:, :]
            ind = xls.index[6:]
            print 'data: {}'.format(data)
            print 'index: {}'.format(ind)
            # xls.index = xls[]

            print xls


if __name__ == '__main__':
    home = os.path.expanduser('~')
    print 'home: {}'.format(home)
    root = os.path.join(home)
    input_path = os.path.join(root, 'Documents', 'Marie', 'chem_clean')
    clean_up_chem_excel(input_path)

# ============================EOF===================================================
