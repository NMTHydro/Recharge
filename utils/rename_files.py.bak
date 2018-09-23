import os
import unicodedata
folder = 'F:\ETRM_Inputs\NM_Geo_Shapes\Selected_Basin_Polygons'
os.chdir(folder)
files = os.listdir(folder)
for item in files:
    stripped, name = item.split('Name__')
    name = '{}'.format(name)
    name = name.replace(' ', '_')
    name = name.lower()
    print name
    os.rename(item, name)