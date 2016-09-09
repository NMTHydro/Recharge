import os
import unicodedata
folder = 'F:\ETRM_Inputs\NM_Geo_Shapes\State_Polygon'
os.chdir(folder)
files = os.listdir(folder)
for item in files:
    stripped, name = item.split('Buffer')
    name = 'NM_State{}'.format(name)
    # name = name.replace(' ', '_')
    print name
    os.rename(item, name)