import csv

from sqlalchemy import Column, String, Integer, create_engine, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 创建对象的基类:
Base = declarative_base()


# 定义Source_train对象: nsl-kdd 训练集
class Source_train(Base):
    # 表的名字:
    __tablename__ = 'Source_train'

    # 表的结构
    id = Column(Integer, primary_key=True, autoincrement=True)

    duration = Column(Float)  # 1
    ip_proto = Column(String)  # 2
    service = Column(String)  # 3
    state = Column(String)  # 4
    src_bytes = Column(Integer)  # 5
    dst_bytes = Column(Integer)  # 6
    land = Column(String)  # 7
    wrong_pac = Column(Integer)  # 8
    urgent_pac = Column(Integer)  # 9
    # 统计当前连接记录与之前2s时间内的连接的关联信息，包含相同目标主机和相同服务两种连接
    count = Column(Integer)  # feature 23
    srv_count = Column(Integer)  # feature 24
    serror_rate = Column(Float)   # feature 25
    srv_serror_rate = Column(Float)   # feature 26
    rerror_rate = Column(Float)   # feature 27
    srv_rerror_rate = Column(Float)   # feature 28
    same_srv_rate = Column(Float)   # feature 29
    diff_srv_rate = Column(Float)   # feature 30
    srv_diff_host_rate = Column(Float) # feature 31
    # 统计当前连接之前100个连接记录中与当前连接具有相同目标主机的统计信息
    dst_host_count = Column(Integer)  # feature 32
    dst_host_srv_count = Column(Integer)  # feature 33
    dst_host_same_srv_rate = Column(Float)   # feature 34
    dst_host_diff_srv_rate = Column(Float)   # feature 35
    dst_host_same_src_port_rate = Column(Float)   # feature 36
    dst_host_srv_diff_host_rate = Column(Float) # feature 37
    dst_host_serror_rate = Column(Float)   # feature 38
    dst_host_srv_serror_rate = Column(Float)   # feature 39
    dst_host_rerror_rate = Column(Float)   # feature 40
    dst_host_srv_rerror_rate = Column(Float)   # feature 41
    classification = Column(String)

    def __repr__(self):
        return "<Source_train(id='%d', duration='%s', ip_proto='%s', service='%s', state='%s')>" % (
            self.id, self.duration, self.ip_proto, self.service, self.state)
    def to_list(self):
        return [self.duration, self.ip_proto, self.service, self.state, self.src_bytes, self.dst_bytes
            , self.land, self.wrong_pac, self.urgent_pac,
                self.count, self.srv_count, self.serror_rate,
                self.srv_serror_rate, self.rerror_rate, self.srv_rerror_rate, self.same_srv_rate, self.diff_srv_rate
            , self.srv_diff_host_rate,
                self.dst_host_count, self.dst_host_srv_count, self.dst_host_same_srv_rate,
                self.dst_host_diff_srv_rate, self.dst_host_same_src_port_rate, self.dst_host_srv_diff_host_rate,
                self.dst_host_serror_rate, self.dst_host_srv_serror_rate,
                self.dst_host_rerror_rate, self.dst_host_srv_rerror_rate]


# 定义Standard_test对象: nsl-kdd 测试集
class Source_test(Base):
    # 表的名字:
    __tablename__ = 'Source_test'

    # 表的结构
    id = Column(Integer, primary_key=True, autoincrement=True)

    duration = Column(Float)  # 1
    ip_proto = Column(String)  # 2
    service = Column(String)  # 3
    state = Column(String)  # 4
    src_bytes = Column(Integer)  # 5
    dst_bytes = Column(Integer)  # 6
    land = Column(String)  # 7
    wrong_pac = Column(Integer)  # 8
    urgent_pac = Column(Integer)  # 9
    # 统计当前连接记录与之前2s时间内的连接的关联信息，包含相同目标主机和相同服务两种连接
    count = Column(Integer)  # feature 23
    srv_count = Column(Integer)  # feature 24
    serror_rate = Column(Float)  # feature 25
    srv_serror_rate = Column(Float)  # feature 26
    rerror_rate = Column(Float)  # feature 27
    srv_rerror_rate = Column(Float)  # feature 28
    same_srv_rate = Column(Float)  # feature 29
    diff_srv_rate = Column(Float)  # feature 30
    srv_diff_host_rate = Column(Float)  # feature 31
    # 统计当前连接之前100个连接记录中与当前连接具有相同目标主机的统计信息
    dst_host_count = Column(Integer)  # feature 32
    dst_host_srv_count = Column(Integer)  # feature 33
    dst_host_same_srv_rate = Column(Float)  # feature 34
    dst_host_diff_srv_rate = Column(Float)  # feature 35
    dst_host_same_src_port_rate = Column(Float)  # feature 36
    dst_host_srv_diff_host_rate = Column(Float)  # feature 37
    dst_host_serror_rate = Column(Float)  # feature 38
    dst_host_srv_serror_rate = Column(Float)  # feature 39
    dst_host_rerror_rate = Column(Float)  # feature 40
    dst_host_srv_rerror_rate = Column(Float)  # feature 41
    classification = Column(String)


    def __repr__(self):
        return "<Source_test(id='%d', duration='%s', ip_proto='%s', service='%s', state='%s')>" % (
            self.id, self.duration, self.ip_proto, self.service, self.state)
    def to_list(self):
        return [self.duration, self.ip_proto, self.service, self.state, self.src_bytes, self.dst_bytes
            , self.land, self.wrong_pac, self.urgent_pac,
                self.count, self.srv_count, self.serror_rate,
                self.srv_serror_rate, self.rerror_rate, self.srv_rerror_rate, self.same_srv_rate, self.diff_srv_rate
            , self.srv_diff_host_rate,
                self.dst_host_count, self.dst_host_srv_count, self.dst_host_same_srv_rate,
                self.dst_host_diff_srv_rate, self.dst_host_same_src_port_rate, self.dst_host_srv_diff_host_rate,
                self.dst_host_serror_rate, self.dst_host_srv_serror_rate,
                self.dst_host_rerror_rate, self.dst_host_srv_rerror_rate]

# 定义Source_sniff对象: 实时抓取的
class Source_sniff(Base):
    # 表的名字:
    __tablename__ = 'Source_sniff'

    # 表的结构
    id = Column(Integer, primary_key=True, autoincrement=True)

    duration = Column(Float)  # 1
    ip_proto = Column(String)  # 2
    service = Column(String)  # 3
    state = Column(String)  # 4
    src_bytes = Column(Integer)  # 5
    dst_bytes = Column(Integer)  # 6
    land = Column(Integer)  # 7
    wrong_pac = Column(Integer)  # 8
    urgent_pac = Column(Integer)  # 9
    # 统计当前连接记录与之前2s时间内的连接的关联信息，包含相同目标主机和相同服务两种连接
    count = Column(Integer)  # feature 23
    srv_count = Column(Integer)  # feature 24
    serror_rate = Column(Float)  # feature 25
    srv_serror_rate = Column(Float)  # feature 26
    rerror_rate = Column(Float)  # feature 27
    srv_rerror_rate = Column(Float)  # feature 28
    same_srv_rate = Column(Float)  # feature 29
    diff_srv_rate = Column(Float)  # feature 30
    srv_diff_host_rate = Column(Float)  # feature 31
    # 统计当前连接之前100个连接记录中与当前连接具有相同目标主机的统计信息
    dst_host_count = Column(Integer)  # feature 32
    dst_host_srv_count = Column(Integer)  # feature 33
    dst_host_same_srv_rate = Column(Float)  # feature 34
    dst_host_diff_srv_rate = Column(Float)  # feature 35
    dst_host_same_src_port_rate = Column(Float)  # feature 36
    dst_host_srv_diff_host_rate = Column(Float)  # feature 37
    dst_host_serror_rate = Column(Float)  # feature 38
    dst_host_srv_serror_rate = Column(Float)  # feature 39
    dst_host_rerror_rate = Column(Float)  # feature 40
    dst_host_srv_rerror_rate = Column(Float)  # feature 41
    classification = Column(String)


    def __repr__(self):
        return "<Source_sniff(id='%d', duration='%s', ip_proto='%s', service='%s', state='%s')>" % (
            self.id, self.duration, self.ip_proto, self.service, self.state)

    def to_list(self):
        return [self.duration,self.ip_proto,self.service,self.state,self.src_bytes,self.dst_bytes
                ,self.land,self.wrong_pac,self.urgent_pac,
                self.count,self.srv_count,self.serror_rate,
                self.srv_serror_rate,self.rerror_rate,self.srv_rerror_rate,self.same_srv_rate,self.diff_srv_rate
                ,self.srv_diff_host_rate,
                self.dst_host_count,self.dst_host_srv_count,self.dst_host_same_srv_rate,
                self.dst_host_diff_srv_rate,self.dst_host_same_src_port_rate,self.dst_host_srv_diff_host_rate,
                self.dst_host_serror_rate,self.dst_host_srv_serror_rate,
                self.dst_host_rerror_rate,self.dst_host_srv_rerror_rate]

# 创建表
def init_table(engine):
    Base.metadata.create_all(engine)


# 删除表
def drop_table(engine):
    Base.metadata.drop_all(engine)


if __name__ == '__main__':

    # drop_db()
    # 初始化数据库连接:
    engine = create_engine('sqlite:///./data/Raw.db')
    # 删除表
    drop_table(engine)
    # 创建表
    init_table(engine)
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    # 创建session对象:
    session = DBSession()

    source_file1 = './data/NSL-KDD/KDDTest+.txt'  # 'source_file/kddcup.data_10_percent_corrected'
    source_file2 = './data/NSL-KDD/KDDTrain+.txt'  # 'source_file/kddcup.data_10_percent_corrected'
    print('start')

    list_flag = [['normal', 'normal'],
                 ['dos', 'back', 'land', 'neptune', 'pod', 'smurf', 'teardrop', 'apache2', 'mailbomb', 'processtable'],
                 ['probe', 'ipsweep', 'nmap', 'portsweep', 'satan', 'mscan', 'saint'],
                 ['r2l', 'ftp_write', 'guess_passwd', 'imap', 'multihop', 'phf', 'spy', 'warezclient', 'warezmaster',
                  'sendmail', 'named', 'snmpgetattack', 'snmpguess', 'xlock', 'xsnoop', 'worm'],
                 ['u2r', 'buffer_overflow', 'loadmodule', 'perl', 'rootkit', 'httptunnel', 'ps', 'sqlattack', 'xterm']]

    # Source_test添加数据
    with open(source_file1, 'r') as data_source:
        csv_reader = csv.reader(data_source)
        for row in csv_reader:
            for i in range(len(list_flag)):
                if row[-2] in list_flag[i]:
                    row[-2] = list_flag[i][0]
            if row[-2] == 'r2l' or row[-2] == 'u2r':
                continue
            new_d = Source_test(duration=row[0], ip_proto=row[1], service=row[2], state=row[3], src_bytes=row[4],
                                dst_bytes=row[5], land=row[6], wrong_pac=row[7], urgent_pac=row[8],count=row[22],
                                srv_count=row[23],serror_rate=row[24],srv_serror_rate=row[25],rerror_rate=row[26],
                                srv_rerror_rate=row[27],same_srv_rate=row[28],diff_srv_rate=row[29],srv_diff_host_rate=row[30],
                                dst_host_count=row[31],dst_host_srv_count=row[32],dst_host_same_srv_rate=row[33],
                                dst_host_diff_srv_rate=row[34], dst_host_same_src_port_rate=row[35],
                                dst_host_srv_diff_host_rate=row[36],
                                dst_host_serror_rate=row[37], dst_host_srv_serror_rate=row[38], dst_host_rerror_rate=row[39],
                                dst_host_srv_rerror_rate=row[40],
                                classification=row[-2])
            session.add(new_d)
        session.commit()
    user = session.query(Source_test).filter(Source_test.id == 1).first()
    print(user)

    # Source_test添加数据
    with open(source_file2, 'r') as data_source:
        csv_reader = csv.reader(data_source)
        for row in csv_reader:
            for i in range(len(list_flag)):
                if row[-2] in list_flag[i]:
                    row[-2] = list_flag[i][0]
            if row[-2] == 'r2l' or row[-2] == 'u2r':
                continue
            new_d = Source_train(duration=row[0], ip_proto=row[1], service=row[2], state=row[3], src_bytes=row[4],
                                dst_bytes=row[5], land=row[6], wrong_pac=row[7], urgent_pac=row[8], count=row[22],
                                srv_count=row[23], serror_rate=row[24], srv_serror_rate=row[25], rerror_rate=row[26],
                                srv_rerror_rate=row[27], same_srv_rate=row[28], diff_srv_rate=row[29],
                                srv_diff_host_rate=row[30],
                                dst_host_count=row[31], dst_host_srv_count=row[32], dst_host_same_srv_rate=row[33],
                                dst_host_diff_srv_rate=row[34], dst_host_same_src_port_rate=row[35],
                                dst_host_srv_diff_host_rate=row[36],
                                dst_host_serror_rate=row[37], dst_host_srv_serror_rate=row[38],
                                dst_host_rerror_rate=row[39],
                                dst_host_srv_rerror_rate=row[40],
                                classification=row[-2])
            session.add(new_d)
        session.commit()
    user = session.query(Source_train).filter(Source_train.id == 1).first()
    print(user)

    session.close()
