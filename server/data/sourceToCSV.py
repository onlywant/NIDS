import csv
import tqdm
import pandas as pd
import numpy as np

''' 
maxtime = 58329s  分成 0 [1-1000] [1001-2000] ……
maxbytesend = 1379963888      三位数 100 一段 四位数 1000 一段 五位数 10000一段 ……
maxbyterec = 1309937401       三位数 100 一段 四位数 1000 一段 五位数 10000一段 ……
'''
def to_csv():
    source_file = '../data/NSL-KDD/KDDTest+.txt'#'source_file/kddcup.data_10_percent_corrected'
    handled_file = '../data/nsl-test.csv'  # write to csv file
    # source_file = '../data/NSL-KDD/KDDTrain+.txt'  # 'source_file/kddcup.data_10_percent_corrected'
    # handled_file = '../data/nsl-train.csv'  # write to csv file
    # source_file = 'source_file/kddcup.data.corrected'  # 'source_file/kddcup.data_10_percent_corrected'
    # handled_file = 'all_data.csv'  # write to csv file
    data_file = open(handled_file, 'w', newline='')
    print('start')
    maxtime = 0
    maxbytesend = 0
    maxbyterec = 0
    list_flag = [['normal','normal'],
                 ['dos','back', 'land', 'neptune', 'pod', 'smurf', 'teardrop','apache2','mailbomb','processtable'],
                 ['probe','ipsweep', 'nmap', 'portsweep','satan','mscan','saint'],
                 ['r2l','ftp_write', 'guess_passwd', 'imap', 'multihop', 'phf', 'spy', 'warezclient', 'warezmaster',
                  'sendmail','named','snmpgetattack','snmpguess','xlock','xsnoop','worm'],
                 ['u2r','buffer_overflow', 'loadmodule', 'perl', 'rootkit','httptunnel','ps','sqlattack','xterm']]

    csv_writer = csv.writer(data_file)
    with open(source_file, 'r') as data_source:
        csv_reader = csv.reader(data_source)
        for row in tqdm.tqdm(csv_reader):
            for i in range(len(list_flag)):
                if row[-2] in list_flag[i]:
                    row[-2] = list_flag[i][0]
            if row[-2]=='r2l' or row[-2]=='u2r':
                continue
            int_ = int(row[0])
            if int_ == 0:
                row[0] = 'time_0'
            elif int_ < 100:
                row[0] = 'time_1'
            else:
                row[0] = 'time_2'
            int_ = int(row[4])
            if int_ == 0:
                row[4] = 'byte_src_0'
            elif int_ < 100:
                row[4] = 'byte_src_1'
            elif int_ < 1000:
                row[4] = 'byte_src_2'
            elif int_ < 10000:
                row[4] = 'byte_src_3'
            else:
                row[4] = 'byte_src_4'
            int_ = int(row[5])
            if int_ == 0:
                row[5] = 'byte_dst_0'
            elif int_ < 100:
                row[5] = 'byte_dst_1'
            elif int_ < 1000:
                row[5] = 'byte_dst_2'
            elif int_ < 10000:
                row[5] = 'byte_dst_3'
            else:
                row[5] = 'byte_dst_4'

            if row[6] == '0':
                row[6] = 'zero'
            else:
                row[6] = 'one'
            row[7] = 'wf'+row[7]
            row[8] = 'ug'+row[8]
            x = row[0:9]
            row[22] = 'count'+row[22]
            row[23] = 'srv_count' + row[23]
            row[24] = 'serror_rate' + str(int(float(row[24]) * 100 // 10))
            row[25] = 'srv_serror_rate' + str(int(float(row[25]) * 100 // 10))
            row[26] = 'rerror_rate' + str(int(float(row[26]) * 100 // 10))
            row[27] = 'srv_rerror_rate' + str(int(float(row[27]) * 100 // 10))
            row[28] = 'same_srv_rate' + str(int(float(row[28]) * 100 // 10))
            row[29] = 'diff_srv_rate' + str(int(float(row[29]) * 100 // 10))
            row[30] = 'srv_diff_host_rate' + str(int(float(row[30]) * 100 // 10))

            row[31] = 'dst_host_count' + row[31]
            row[32] = 'dst_host_srv_count' + row[32]
            row[33] = 'dst_host_same_srv_rate' + str(int(float(row[33]) * 100 // 10))
            row[34] = 'dst_host_diff_srv_rate' + str(int(float(row[34]) * 100 // 10))
            row[35] = 'dst_host_same_src_port_rate' + str(int(float(row[35]) * 100 // 10))
            row[36] = 'dst_host_srv_diff_host_rate' + str(int(float(row[36]) * 100 // 10))
            row[37] = 'dst_host_serror_rate' + str(int(float(row[37]) * 100 // 10))
            row[38] = 'dst_host_srv_serror_rate' + str(int(float(row[38]) * 100 // 10))
            row[39] = 'dst_host_rerror_rate' +str(int(float(row[39]) * 100 // 10))
            row[40] = 'dst_host_srv_rerror_rate' + str(int(float(row[40]) * 100 // 10))
            x.extend(row[22:41])

            x.append(row[-2])
            csv_writer.writerow(x)
        data_file.close()

    print(maxbytesend,maxbyterec)
    print('pre process completed!')




if __name__ == '__main__':
    to_csv()
    # reader = pd.read_csv('nsl-train.csv')
    # arr = np.array(reader)
    # col1 = arr[:,-1]
    # dict = {}
    # for i in range(len(col1)):
    #     if dict.get(col1[i],None) == None:
    #         dict[col1[i]] = 0
    #     else:
    #         dict[col1[i]]+=1
    # for i in sorted(dict.keys()):
    #     print((i,dict[i]),end=' ')
