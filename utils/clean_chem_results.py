import pandas as pd
import os


def clean_up_chem_excel(folder):
    excels = os.listdir(folder)
    for excel in excels:
        print('excel: {}'.format(excel))
        if excel.endswith(".xlsx"):
            xls = pd.read_excel(os.path.join(folder, excel), header=4)
            xls = xls[xls.A.str.contains('Cycle') == False]
            write_name = excel.replace(' ', '_')
            xls.to_excel(os.path.join(folder, write_name))

if __name__ == '__main__':
    home = os.path.expanduser('~')
    print('home: {}'.format(home))
    root = os.path.join(home)
    input_path = os.path.join(root, 'Documents', 'Marie', 'chem_clean_3')
    clean_up_chem_excel(input_path)

# ============================EOF===================================================
