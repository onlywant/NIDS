# 实现了 server 端用于接收客户端发送的数据，并对数据后返回给客户端

from multiprocessing import Pipe,Queue,Process
from time import sleep
from concurrent import futures
import grpc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import protos.helloGRPC_pb2, protos.helloGRPC_pb2_grpc
import Catch_Net_Data as cnd
import Classification_Standard as cfs
from Feature_DB import Extra_train,transform
from Sniff_DB import Sniff_data
from Raw_DB import Source_sniff


_ONE_DAY_IN_SECONDS = 60 * 60 * 24
# 指定服务开放的地址及端口
_HOST = '127.0.0.1'
_PORT = '50052'


# 实现一个派生类,重写rpc中的接口函数.自动生成的grpc文件中比proto中的服务名称多了一个Servicer
class Function(protos.helloGRPC_pb2_grpc.GreeterServicer):
    # 重写接口函数.输入和输出都是proto中定义的Data类型
    def __init__(self):
        super(Function, self).__init__()
        self.father, self.son = Pipe()
        self.buffer_q = Queue()
        self.buffer_p = Queue()
        self.classification = cfs.Classification()
        self.process_sniff = None
        self.process_progress = None
        self.filter = 'ip and (tcp or udp or icmp)'
        self.iface = 'Realtek 8821CE Wireless LAN 802.11ac PCI-E NIC'
        self.engine_fea = create_engine('sqlite:///./data/Fea.db')
        self.engine_raw = create_engine('sqlite:///./data/Raw.db')
        self.engine_sniff = create_engine('sqlite:///./data/Sniff.db')
        print('rpc function init finished')

    def start(self, request, context):
        print('client use start button')
        self.iface = request.inter
        self.filter = request.filter
        print(self.iface,self.filter)
        sn = cnd.Sniffer()
        DBSession_sniff = sessionmaker(bind=self.engine_sniff)
        # 创建session对象:
        session_sniff = DBSession_sniff()
        self.process_sniff = Process(target=sn.start_cap, args=(self.buffer_q, self.son, self.filter, self.iface,))
        self.process_sniff.start()
        while True:
            # TODO 获取特征 重写
            conv = self.buffer_q.get()
            if conv is None:
                break
            fea = conv.get_all_features()
            trans_fea = fea.copy()
            transform(trans_fea)
            cate = self.classification.get_category_from_feature(trans_fea)

            str_fea = ' '.join(trans_fea)
            print(fea)
            new_s = Sniff_data( src_ip=conv.conv.five_tuple.src_ip, dst_ip=conv.conv.five_tuple.dst_ip,
                                src_port=conv.conv.five_tuple.src_port, dst_port=conv.conv.five_tuple.dst_port,
                                duration=fea[0], ip_proto=fea[1], service=fea[2], state=fea[3], src_bytes=fea[4],
                                dst_bytes=fea[5], land=fea[6], wrong_pac=fea[7], urgent_pac=fea[8],count=fea[9],
                                srv_count=fea[10],serror_rate=fea[11],srv_serror_rate=fea[12],rerror_rate=fea[13],
                                srv_rerror_rate=fea[14],same_srv_rate=fea[15],diff_srv_rate=fea[16],srv_diff_host_rate=fea[17],
                                dst_host_count=fea[18],dst_host_srv_count=fea[19],dst_host_same_srv_rate=fea[20],
                                dst_host_diff_srv_rate=fea[21], dst_host_same_src_port_rate=fea[22],
                                dst_host_srv_diff_host_rate=fea[23],
                                dst_host_serror_rate=fea[24], dst_host_srv_serror_rate=fea[25], dst_host_rerror_rate=fea[26],
                                dst_host_srv_rerror_rate=fea[27],feature=str_fea,
                                classification=cate)
            session_sniff.add(new_s)

            yield protos.helloGRPC_pb2.Datagram(duration=fea[0], ip_proto=fea[1], service=fea[2], state=fea[3], src_bytes=fea[4],
                                dst_bytes=fea[5], land=str(fea[6]), wrong_pac=fea[7], urgent_pac=fea[8],feature=str_fea,
                                classification=cate, src_ip=str(conv.conv.five_tuple.src_ip), dst_ip=str(conv.conv.five_tuple.dst_ip),
                                src_port=str(conv.conv.five_tuple.src_port), dst_port=str(conv.conv.five_tuple.dst_port))
        session_sniff.commit()
        session_sniff.close()
        print('producer over')
        # print(self.thread_with_server.is_alive())

    def stop(self, request, context):
        print('client use stop button')
        self.father.send('over!')
        return protos.helloGRPC_pb2.Message(mes="successfully stop")

    def getInterfaceList(self, request, context):
        print('get interface list')
        list = protos.helloGRPC_pb2.Interfaces()
        for i in cnd.IFACES.data:
            item = list.interface.add()
            item.name = cnd.IFACES.data[i].description
        return list

    def setInterface(self, request, context):
        print('set interface')
        self.iface = request.name
        return protos.helloGRPC_pb2.Message(mes="successfully set the interface")

    def setFilter(self, request, context):
        print('set filter')
        self.filter = request.name
        return protos.helloGRPC_pb2.Message(mes="successfully set the filter")

    def queryAllFromSniff(self, request, context):
        print('query all data')
        DBSession_sniff = sessionmaker(bind=self.engine_sniff)
        # 创建session对象:
        session_sniff = DBSession_sniff()
        data = session_sniff.query(Sniff_data).all()
        datas = protos.helloGRPC_pb2.Datagrams()
        for i in range(len(data)):
            datag = datas.datagram.add()
            datag.id = data[i].id
            datag.src_ip = data[i].src_ip
            datag.dst_ip = data[i].dst_ip
            datag.src_port = data[i].src_port
            datag.dst_port = data[i].dst_port
            datag.ip_proto = data[i].ip_proto
            datag.feature = data[i].feature
            datag.classification = data[i].classification
            datag.duration = data[i].duration
            datag.src_bytes = data[i].src_bytes
            datag.dst_bytes = data[i].dst_bytes
            datag.service = data[i].service
            datag.state = data[i].state
            datag.wrong_pac = data[i].wrong_pac
            datag.urgent_pac = data[i].urgent_pac
            # tra.feature =
            # tra.flag = data[i].classification
            # tra = datag.tra
        session_sniff.close()
        return datas

    def addToTrain(self, request, context):
        DBSession_fea = sessionmaker(bind=self.engine_fea)
        # 创建session对象:
        session_fea = DBSession_fea()
        DBSession_sniff = sessionmaker(bind=self.engine_sniff)
        # 创建session对象:
        session_sniff = DBSession_sniff()
        DBSession_raw = sessionmaker(bind=self.engine_raw)
        # 创建session对象:
        session_raw = DBSession_raw()

        user = session_sniff.query(Sniff_data).filter(Sniff_data.id == request.id).first()
        # print(user)
        session_fea.add(Extra_train(classification=user.classification, feature=user.feature))
        session_raw.add(Source_sniff(duration=user.duration, ip_proto=user.ip_proto, service=user.service,
                                     state=user.state, src_bytes=user.src_bytes, dst_bytes=user.dst_bytes,
                                     land=user.land, wrong_pac=user.wrong_pac, urgent_pac=user.urgent_pac,
                                     count=user.count ,
                                     srv_count=user.srv_count , serror_rate=user.serror_rate , srv_serror_rate=user.srv_serror_rate ,
                                     rerror_rate=user.rerror_rate ,
                                     srv_rerror_rate=user.srv_rerror_rate , same_srv_rate=user.same_srv_rate , diff_srv_rate=user.diff_srv_rate ,
                                     srv_diff_host_rate=user.srv_diff_host_rate ,
                                     dst_host_count=user.dst_host_count , dst_host_srv_count=user.dst_host_srv_count , dst_host_same_srv_rate=user.dst_host_same_srv_rate ,
                                     dst_host_diff_srv_rate=user.dst_host_diff_srv_rate , dst_host_same_src_port_rate=user.dst_host_same_src_port_rate ,
                                     dst_host_srv_diff_host_rate=user.dst_host_srv_diff_host_rate ,
                                     dst_host_serror_rate=user.dst_host_serror_rate , dst_host_srv_serror_rate=user.dst_host_srv_serror_rate,
                                     dst_host_rerror_rate=user.dst_host_rerror_rate ,
                                     dst_host_srv_rerror_rate=user.dst_host_srv_rerror_rate ,
                                     classification=user.classification))
        # session_sniff.query(Sniff_data).filter(Sniff_data.id == request.id).delete()
        # session_sniff.commit()
        session_fea.commit()
        session_raw.commit()
        session_raw.close()
        session_fea.close()
        session_sniff.close()
        return protos.helloGRPC_pb2.Message(mes='successfully add train')

    def delFromSniff(self, request, context):
        DBSession_sniff = sessionmaker(bind=self.engine_sniff)
        # 创建session对象:
        session_sniff = DBSession_sniff()
        session_sniff.query(Sniff_data).filter(Sniff_data.id == request.id).delete()
        session_sniff.commit()
        session_sniff.close()
        return protos.helloGRPC_pb2.Message(mes='successfully del sniffer')

    def trainAgain(self, request, context):
        self.classification.set_para(request.size, request.circle, request.epoch, request.Rate, request.deRate,
                                     request.addNew)
        self.process_progress = Process(target=self.classification.train_dbow,
                                                        args=(self.buffer_p,))
        self.process_progress.start()
        while True:
            percent = self.buffer_p.get()

            if percent is None:
                break
            yield protos.helloGRPC_pb2.Message(mes=str(percent))
        # self.process_progress.join()

        result = self.buffer_p.get()
        yield protos.helloGRPC_pb2.Message(mes=str(result))
        #
        # return protos.helloGRPC_pb2.Message(
        #     mes=self.classification.test_model(self.classification.modelDbow, self.classification.docTest_Tagged))

    def coverModel(self, request, context):
        self.classification.save_model_from_mid()
        return protos.helloGRPC_pb2.Message(mes='success!')


def serve():
    # 定义服务器并设置最大连接数,corcurrent.futures是一个并发库，类似于线程池的概念
    grpcServer = grpc.server(futures.ThreadPoolExecutor(max_workers=4))  # 创建一个服务器
    protos.helloGRPC_pb2_grpc.add_GreeterServicer_to_server(Function(), grpcServer)  # 在服务器中添加派生的接口服务（自己实现了处理函数）
    grpcServer.add_insecure_port(_HOST + ':' + _PORT)  # 添加监听端口
    grpcServer.start()  # 启动服务器
    try:
        while True:
            sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        grpcServer.stop(0)  # 关闭服务器


if __name__ == '__main__':
    print("server started")

    # p2.start()
    serve()
    #  python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. helloGRPC.proto
