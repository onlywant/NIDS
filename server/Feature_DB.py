# 导入:
from sqlalchemy import Column, String, Integer, create_engine, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from Raw_DB import Source_train, Source_test, Source_sniff

# 创建对象的基类:
Base = declarative_base()


# 定义Standard_train对象: nsl-kdd 训练集
class Fea_train(Base):
    # 表的名字:
    __tablename__ = 'Fea_train'

    # 表的结构:
    id = Column(Integer, primary_key=True, autoincrement=True)
    classification = Column(String(7))
    feature = Column(String)

    def __repr__(self):
        return "<Fea_train(id='%d', classification='%s', feature='%s')>" % (self.id, self.classification, self.feature)


# 定义Standard_test对象: nsl-kdd 测试集
class Fea_test(Base):
    # 表的名字:
    __tablename__ = 'Fea_test'

    # 表的结构:
    id = Column(Integer, primary_key=True, autoincrement=True)
    classification = Column(String)
    feature = Column(String)

    def __repr__(self):
        return "<Fea_test(id='%d', classification='%s', feature='%s')>" % (self.id, self.classification, self.feature)


# 定义Extra_train对象:  Sniff_data中确认正确的数据
class Extra_train(Base):
    # 表的名字:
    __tablename__ = 'extra_train'

    # 表的结构:
    id = Column(Integer, primary_key=True, autoincrement=True)
    classification = Column(String)
    feature = Column(String)

    def __repr__(self):
        return "<extra_train(id='%d', classification='%s', feature='%s')>" % (
        self.id, self.classification, self.feature)


# 创建表
def init_table(engine):
    Base.metadata.create_all(engine)


# 删除表
def drop_table(engine):
    Base.metadata.drop_all(engine)


# 设计一个函数，进行原始数据向单词数据转化的方法
def transform(row):
    res = []
    int_ = int(row[0])
    if int_ == 0:
        row[0] = 'W1_0'
    elif int_ < 100:
        row[0] = 'W1_1'
    else:
        row[0] = 'W1_2'
    int_ = int(row[4])
    if int_ == 0:
        row[4] = 'W5_0'
    elif int_ < 100:
        row[4] = 'W5_1'
    elif int_ < 1000:
        row[4] = 'W5_2'
    elif int_ < 10000:
        row[4] = 'W5_3'
    else:
        row[4] = 'W5_4'
    int_ = int(row[5])
    if int_ == 0:
        row[5] = 'W6_0'
    elif int_ < 100:
        row[5] = 'W6_1'
    elif int_ < 1000:
        row[5] = 'W6_2'
    elif int_ < 10000:
        row[5] = 'W6_3'
    else:
        row[5] = 'W6_4'

    if row[6] == 0:
        row[6] = 'W7_0'
    else:
        row[6] = 'W7_1'
    row[7] = 'W8_' + str(row[7])
    row[8] = 'W9_' + str(row[8])
    row[9] = 'W23_' + str(row[9])
    row[10] = 'W24_' + str(row[10])
    row[11] = 'W25_' + str(int(float(row[11]) * 100 // 10))
    row[12] = 'W26_' + str(int(float(row[12]) * 100 // 10))
    row[13] = 'W27_' + str(int(float(row[13]) * 100 // 10))
    row[14] = 'W28_' + str(int(float(row[14]) * 100 // 10))
    row[15] = 'W29_' + str(int(float(row[15]) * 100 // 10))
    row[16] = 'W30_' + str(int(float(row[16]) * 100 // 10))
    row[17] = 'W31_' + str(int(float(row[17]) * 100 // 10))
    row[18] = 'W32_' + str(row[18])
    row[19] = 'W33_' + str(row[19])
    row[20] = 'W34_' + str(int(float(row[20]) * 100 // 10))
    row[21] = 'W35_' + str(int(float(row[21]) * 100 // 10))
    row[22] = 'W36_' + str(int(float(row[22]) * 100 // 10))
    row[23] = 'W37_' + str(int(float(row[23]) * 100 // 10))
    row[24] = 'W38_' + str(int(float(row[24]) * 100 // 10))
    row[25] = 'W39_' + str(int(float(row[25]) * 100 // 10))
    row[26] = 'W40_' + str(int(float(row[26]) * 100 // 10))
    row[27] = 'W41_' + str(int(float(row[27]) * 100 // 10))


# 将数据添加至数据库中
def add_db(session):
    engine_raw = create_engine('sqlite:///./data/Raw.db')
    DBSession_raw = sessionmaker(bind=engine_raw)
    session_raw = DBSession_raw()
    # 添加Fea_test数据

    x = session_raw.query(Source_test).all()
    for i in range(len(x)):
        res = x[i].to_list()
        transform(res)
        fea_test = Fea_test(classification=x[i].classification, feature=' '.join(res))
        session.add(fea_test)
    session.commit()
    # 添加Fea_train数据
    x = session_raw.query(Source_train).all()
    for i in range(len(x)):
        res = x[i].to_list()
        transform(res)
        fea_train = Fea_train(classification=x[i].classification, feature=' '.join(res))
        session.add(fea_train)
    session.commit()
    # 添加Extra_train数据
    x = session_raw.query(Source_sniff).all()
    for i in range(len(x)):
        res = x[i].to_list()
        transform(res)
        extra_train = Extra_train(classification=x[i].classification, feature=' '.join(res))
        session.add(extra_train)
    session.commit()
    session.close()
    session_raw.close()


if __name__ == '__main__':
    # drop_db()
    # 初始化数据库连接:
    engine_fea = create_engine('sqlite:///./data/Fea.db')
    # 删除表
    drop_table(engine_fea)
    # 创建表
    init_table(engine_fea)
    # 创建DBSession类型:
    DBSession_fea = sessionmaker(bind=engine_fea)
    # 创建session对象:
    session_fea = DBSession_fea()

    add_db(session_fea)

    #   删除数据
    # session.query(Sniff_data).delete()
    # session.commit()

    # 创建Query查询，filter是where条件，最后调用one()返回唯一行，如果调用all()则返回所有行:
    # user = session_fea.query(Sniff_data).filter(Sniff_data.id == 1).first()

    session_fea.close()
