const path = require('path');
const grpc = require('grpc');
const protoLoader = require('@grpc/proto-loader');

const PROTO_PATH = path.resolve(__dirname, './../../protos/helloGRPC.proto');
const packageDefinition = protoLoader.loadSync(
    PROTO_PATH,
    {
        keepCase: true,
        longs: String,
        enums: String,
        defaults: true,
        oneofs: true
    }
);

const hello_proto = grpc.loadPackageDefinition(packageDefinition).helloGRPC;

// 调用 Greeter 的存根构造函数，指定服务器地址和端口。
const client = new hello_proto.Greeter( '127.0.0.1:50052',
            grpc.credentials.createInsecure());

// 构造调用服务的方法：使用事件或者回调函数去获得结果

function start(inter,filter) {
    function _(err, response) {
        if (err) {
            console.log(err);
        } else {
            
        }
    }
    return client.start({inter:inter,filter:filter},  _);
}

function stop(callback) {
    function _(err, response) {
        if (err) {
            console.log(err);
        } else {
            callback(response)   
        }
    }
    return client.stop("123",  _);
}

function getInterfaceList(callback){
    function _(err, interfaceList) {
        if (err) {
            console.log(err);
        } else {
            callback(interfaceList.interface)
            
        }
    }
    return client.getInterfaceList("123",  _);
}

function setInterface(inter,callback){
    function _(err, response) {
        if (err) {
            console.log(err);
        } else {
            callback(response)
            
        }
    }
    return client.setInterface({name:inter},  _);
}

function setFilter(filter,callback){
    function _(err, response) {
        if (err) {
            console.log(err);
        } else {
            callback(response)
            
        }
    }
    return client.setFilter({name:filter},  _);
}

function queryAllFromSniff(callback){
    function _(err, response) {
        if (err) {
            console.log(err);
        } else {
            callback(response);
        }
    }
    return client.queryAllFromSniff("123",  _);
}

function delFromSniff(id){
    function _(err, response) {
        if (err) {
            console.log(err);
        } else {
            console.log(response);
        }
    }
    console.log(id);
    console.log({"id":id});
    
    return client.delFromSniff({"id":id},  _);
}

function addToTrain(id){
    function _(err, response) {
        if (err) {
            console.log(err);
        } else {
            console.log(response);
        }
    }
    return client.addToTrain({"id":id},  _);
}

function trainAgain(train){
    function _(err, response) {
        if (err) {
            console.log(err);
        } else {
        }
    }
    return client.trainAgain(train,  _);
}
function coverModel(callback){
    function _(err, response) {
        if (err) {
            console.log(err);
        } else {
            callback(response);
        }
    }
    return client.coverModel("123",  _);
}

module.exports = {
    start,
    stop,
    getInterfaceList,
    setInterface,
    setFilter,
    queryAllFromSniff,
    delFromSniff,
    addToTrain,
    trainAgain,
    coverModel
}