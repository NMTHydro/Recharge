import os

path = 'C:\Users\David\Documents\Recharge\Snow\Data'
os.chdir(path)
srcDir = os.getcwd()

dirName = 'C:\Users\David\Documents\Recharge\Sensitivity analysis\SA_extracts'

dstDir = os.path.abspath(dirName)

for dirpath, dirnames, filenames in os.walk(srcDir):
    os.mkdir(os.path.join(dirName, dirpath[1+len(srcDir):]))

os.startfile(dirName)