from datetime import datetime
import numpy as np


def read_std_extract_csv(file_name):
    recs = []
    # try:
    fid = open(file_name)
    lines = fid.readlines()[:]
    fid.close()
    # except IOError:
    #     print "couldn't find " + '{a}'.format(a=fid)
    rows = [line.split(',') for line in lines]

    for line in rows:
        try:
            recs.append([datetime.strptime(line[0], '%m/%d/%Y'),  # date
                         float(line[1]), float(line[2]), float(line[3]), float(line[4]),
                         float(line[5]), float(line[6]), float(line[7]), float(line[8]),
                         float(line[9]), float(line[10]), float(line[11]), float(line[12]), float(line[13]),
                         float(line[14]), float(line[15]), float(line[16])])

        except ValueError:
            try:
                recs.append([datetime.strptime(line[0], '%Y-%m-%d %H:%M:%S'),  # date
                             float(line[1]), float(line[2]), float(line[3]), float(line[4]),
                             float(line[5]), float(line[6]), float(line[7]), float(line[8]),
                             float(line[9]), float(line[10]), float(line[11]), float(line[12]), float(line[13]),
                             float(line[14]), float(line[15]), float(line[16])])
            except ValueError:
                recs.append([datetime.strptime(line[0], '%Y/%m/%d'),  # date
                             float(line[1]), float(line[2]), float(line[3]), float(line[4]),
                             float(line[5]), float(line[6]), float(line[7]), float(line[8]),
                             float(line[9]), float(line[10]), float(line[11]), float(line[12]), float(line[13]),
                             float(line[14]), float(line[15]), float(line[16])])

                # ['date', 'ksat', 'soil_ksat', 'kcb', 'rlin', 'rg', 'etrs_Pm', 'plant height', 'min temp',
                # 'max temp', 'temp', 'precip', 'fc', 'wp', 'taw', 'aws', 'root_z'

    data = np.array(recs)
    return data
