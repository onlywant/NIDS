from sqlalchemy import Column, String, Integer, create_engine, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 创建对象的基类:
Base = declarative_base()

# 定义Sniff_data对象: 实时抓取的数据
class Sniff_data(Base):
    # 表的名字:
    __tablename__ = 'sniff_data'

    # 表的结构:
    id = Column(Integer, primary_key=True, autoincrement=True)
    src_ip = Column(String)
    dst_ip = Column(String)
    src_port = Column(String)
    dst_port = Column(String)
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

    feature = Column(String)
    classification = Column(String)
    def __repr__(self):
        return "<sniff_data(id='%d', classification='%s', feature='%s')>" % (self.id, self.classification, self.feature)

# 创建表
def init_table(engine):
    Base.metadata.create_all(engine)


# 删除表
def drop_table(engine):
    Base.metadata.drop_all(engine)


if __name__ == '__main__':

    # drop_db()
    # 初始化数据库连接:
    engine = create_engine('sqlite:///./data/Sniff.db')
    # 删除表
    drop_table(engine)
    # 创建表
    init_table(engine)
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    # 创建session对象:
    session = DBSession()

    session.close()
