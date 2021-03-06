# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import protos.helloGRPC_pb2 as helloGRPC__pb2


class GreeterStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.start = channel.unary_stream(
        '/helloGRPC.Greeter/start',
        request_serializer=helloGRPC__pb2.StartMes.SerializeToString,
        response_deserializer=helloGRPC__pb2.Datagram.FromString,
        )
    self.stop = channel.unary_unary(
        '/helloGRPC.Greeter/stop',
        request_serializer=helloGRPC__pb2.Message.SerializeToString,
        response_deserializer=helloGRPC__pb2.Message.FromString,
        )
    self.getInterfaceList = channel.unary_unary(
        '/helloGRPC.Greeter/getInterfaceList',
        request_serializer=helloGRPC__pb2.Message.SerializeToString,
        response_deserializer=helloGRPC__pb2.Interfaces.FromString,
        )
    self.setInterface = channel.unary_unary(
        '/helloGRPC.Greeter/setInterface',
        request_serializer=helloGRPC__pb2.Interface.SerializeToString,
        response_deserializer=helloGRPC__pb2.Message.FromString,
        )
    self.setFilter = channel.unary_unary(
        '/helloGRPC.Greeter/setFilter',
        request_serializer=helloGRPC__pb2.Filter.SerializeToString,
        response_deserializer=helloGRPC__pb2.Message.FromString,
        )
    self.addToTrain = channel.unary_unary(
        '/helloGRPC.Greeter/addToTrain',
        request_serializer=helloGRPC__pb2.Id.SerializeToString,
        response_deserializer=helloGRPC__pb2.Message.FromString,
        )
    self.delFromSniff = channel.unary_unary(
        '/helloGRPC.Greeter/delFromSniff',
        request_serializer=helloGRPC__pb2.Id.SerializeToString,
        response_deserializer=helloGRPC__pb2.Message.FromString,
        )
    self.queryAllFromSniff = channel.unary_unary(
        '/helloGRPC.Greeter/queryAllFromSniff',
        request_serializer=helloGRPC__pb2.Message.SerializeToString,
        response_deserializer=helloGRPC__pb2.Datagrams.FromString,
        )
    self.trainAgain = channel.unary_stream(
        '/helloGRPC.Greeter/trainAgain',
        request_serializer=helloGRPC__pb2.Train.SerializeToString,
        response_deserializer=helloGRPC__pb2.Message.FromString,
        )
    self.coverModel = channel.unary_unary(
        '/helloGRPC.Greeter/coverModel',
        request_serializer=helloGRPC__pb2.Message.SerializeToString,
        response_deserializer=helloGRPC__pb2.Message.FromString,
        )


class GreeterServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def start(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def stop(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def getInterfaceList(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def setInterface(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def setFilter(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def addToTrain(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def delFromSniff(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def queryAllFromSniff(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def trainAgain(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def coverModel(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_GreeterServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'start': grpc.unary_stream_rpc_method_handler(
          servicer.start,
          request_deserializer=helloGRPC__pb2.StartMes.FromString,
          response_serializer=helloGRPC__pb2.Datagram.SerializeToString,
      ),
      'stop': grpc.unary_unary_rpc_method_handler(
          servicer.stop,
          request_deserializer=helloGRPC__pb2.Message.FromString,
          response_serializer=helloGRPC__pb2.Message.SerializeToString,
      ),
      'getInterfaceList': grpc.unary_unary_rpc_method_handler(
          servicer.getInterfaceList,
          request_deserializer=helloGRPC__pb2.Message.FromString,
          response_serializer=helloGRPC__pb2.Interfaces.SerializeToString,
      ),
      'setInterface': grpc.unary_unary_rpc_method_handler(
          servicer.setInterface,
          request_deserializer=helloGRPC__pb2.Interface.FromString,
          response_serializer=helloGRPC__pb2.Message.SerializeToString,
      ),
      'setFilter': grpc.unary_unary_rpc_method_handler(
          servicer.setFilter,
          request_deserializer=helloGRPC__pb2.Filter.FromString,
          response_serializer=helloGRPC__pb2.Message.SerializeToString,
      ),
      'addToTrain': grpc.unary_unary_rpc_method_handler(
          servicer.addToTrain,
          request_deserializer=helloGRPC__pb2.Id.FromString,
          response_serializer=helloGRPC__pb2.Message.SerializeToString,
      ),
      'delFromSniff': grpc.unary_unary_rpc_method_handler(
          servicer.delFromSniff,
          request_deserializer=helloGRPC__pb2.Id.FromString,
          response_serializer=helloGRPC__pb2.Message.SerializeToString,
      ),
      'queryAllFromSniff': grpc.unary_unary_rpc_method_handler(
          servicer.queryAllFromSniff,
          request_deserializer=helloGRPC__pb2.Message.FromString,
          response_serializer=helloGRPC__pb2.Datagrams.SerializeToString,
      ),
      'trainAgain': grpc.unary_stream_rpc_method_handler(
          servicer.trainAgain,
          request_deserializer=helloGRPC__pb2.Train.FromString,
          response_serializer=helloGRPC__pb2.Message.SerializeToString,
      ),
      'coverModel': grpc.unary_unary_rpc_method_handler(
          servicer.coverModel,
          request_deserializer=helloGRPC__pb2.Message.FromString,
          response_serializer=helloGRPC__pb2.Message.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'helloGRPC.Greeter', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
