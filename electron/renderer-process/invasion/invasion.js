const { BrowserWindow } = require("electron").remote;
const path = require("path");
const rpc = require("./assets/js/rpc.js");

rpc.getInterfaceList(function(interfacelist) {
  const select = document.getElementById("interface");
  interfacelist.forEach(element => {
    var name = document.createElement("option");
    name.innerHTML = element.name;
    select.appendChild(name);
  });
});


var app = new Vue({
  el: "#invasion-section",
  data: {
    num: { normal: 0, dos: 0, probe: 0, r2l: 0, u2r: 0 },
    arr_data: [],
    arr_interface: []
  },
  methods: {
    start: function() {
      // 设置过滤器
      var sel = document.getElementById("interface");
      var index = sel.selectedIndex;
      var inter = sel.options[index].value;
      sel = document.getElementById("filter");
      index = sel.selectedIndex;
      var filter = sel.options[index].value;
      // 设置按钮
      $("#start_sys").toggle();
      $("#stop_sys").toggle();
      var t = document.getElementById("checking");
      // 接受数据
      const stream = rpc.start(inter,filter);
      that = this;
      stream.on("data", function(info) {
        that.arr_data.push(info);
        that.num[info.classification]++;
      });
    },
    stop: function() {
      // 发送结束信号
      var x = rpc.stop(console.log);
      // 设置按钮
      $("#start_sys").toggle();
      $("#stop_sys").toggle();
    }
  }
});
