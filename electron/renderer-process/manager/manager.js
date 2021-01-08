const { ipcRenderer} = require("electron");
var dt  = require( 'datatables.net' )( window, $ );
var t = null;
var data = null;

$(document).ready(function() {
  // 训练分类器
  $("#trainAgain").click(() => {
    ipcRenderer.send('create-window');
  });
  

  // 批量或单个删除
  $("#delItems").click(() => {
    $("#checkbox_id_all").prop("checked", false);
    var sel = t.rows(".selected");
    if (sel.eq(0).length == 0) {
      ipcRenderer.send("open-error-dialog");
      return;
    }
    sel.eq(0).each(function(index) {
      var dat = t.row(index).data();
      rpc.delFromSniff(dat["id"]);
    });
    sel.remove().draw();
  });

  // 批量或单个添加
  $("#addItems").click(() => {
    $("#checkbox_id_all").prop("checked", false);
    var sel = t.rows(".selected");
    if (sel.eq(0).length == 0) {
      ipcRenderer.send("open-error-dialog");
      return;
    }
    sel.eq(0).each(function(index) {
      var dat = t.row(index).data();
      rpc.addToTrain(dat["id"]);
    });
    sel.remove().draw();
  });

  // 查询显示全部数据
  $("#queryAllData").click(() => {
    if (t !== null) {
      t.clear();
    }
    rpc.queryAllFromSniff(datagrams => {
      data = datagrams.datagram;
      t.rows.add(data);
      t.draw();
    });
  });

  // 内表详细信息
  function format(d) {
    // `d` is the original data object for the row

    return (
      '<table cellpadding="1" cellspacing="0" border="0" style="padding-left:30px;">' +
      // "<tr>" +
      // '<td width="35%">id:</td>' +
      // "<td>" +
      // d.id +
      // "</td>" +
      // "</tr>" +
      "<tr>" +
      "<td >duration:</td>" +
      "<td>" +
      d.duration +
      "</td>" +
      "</tr>" +
      "<tr>" +
      "<td>src_port:</td>" +
      "<td>" +
      d.src_port +
      "</td>" +
      "</tr>" +
      "<tr>" +
      "<td>dst_port:</td>" +
      "<td>" +
      d.dst_port +
      "</td>" +
      "</tr>" +
      "<tr>" +
      "<td>src_bytes:</td>" +
      "<td>" +
      d.src_bytes +
      "</td>" +
      "</tr>" +
      "<tr>" +
      "<td>dst_bytes:</td>" +
      "<td>" +
      d.dst_bytes +
      "</td>" +
      "</tr>" +
      "<tr>" +
      "<td>wrong packets:</td>" +
      "<td>" +
      d.wrong_pac +
      "</td>" +
      "</tr>" +
      "<tr>" +
      "<td>urgent packets:</td>" +
      "<td>" +
      d.urgent_pac +
      "</td>" +
      "</tr>" +
      "</table>"
    );
  }

  t = $("#table_id").DataTable({
    paging: true,
    // scrollY : 400,
    data: data,
    columns: [
      {
        className: " details-control",
        orderable: false,
        data: null,
        defaultContent: ""
      },
      { data: "id"},
      { data: "src_ip" },
      { data: "dst_ip" },
      { data: "ip_proto" },
      { data: "state" },
      { data: "service" },
      { data: "classification" }
    ],

    oLanguage: {
      //插件的汉化
      sLengthMenu: "每页显示 _MENU_ 条记录",
      sZeroRecords: "抱歉， 没有找到",
      sInfo: "从 _START_ 到 _END_ /共 _TOTAL_ 条数据",
      sInfoEmpty: "没有数据",
      sInfoFiltered: "(从 _MAX_ 条数据中检索)",
      oPaginate: {
        sFirst: "首页",
        sPrevious: "前一页",
        sNext: "后一页",
        sLast: "尾页"
      },
      sZeroRecords: "没有检索到数据",
      sProcessing: "<img src='' />",
      sSearch: "搜索"
    },
    LengthChange: false,
    lengthMenu: [10, 50, 1000]
  });

  // 选中所有
  $("#checkbox_id_all").click(function() {
    $(":checkbox:not(#checkbox_id_all)").prop("checked", this.checked);
    var $tr = $("#table_id tr");
    if (this.checked) {
      $tr.addClass("selected");
    } else {
      $tr.removeClass("selected");
    }
  });

  // 扩展
  $("#table_id tbody").on("click", "td.details-control", function(event) {
    var tr = $(this).closest("tr");
    var row = t.row(tr);
    
    if (row.child.isShown()) {
      // This row is already open - close it
      row.child.hide();
      tr.removeClass("shown");
    } else {
      // Open this row
      row.child(format(row.data())).show();
      tr.addClass("shown");
    }
    event.stopPropagation();
  });

  //单击行，改变行的样式，并勾选
  $("#table_id tbody").on("click", "tr", function() {
    if ($(this).hasClass("selected")) {
      $(this).removeClass("selected");
    } else {
      $(this).addClass("selected");
    }
  });

  //表尾搜索框
  $("#table_id tfoot th").each(function(i) {
    var title = $(this).text();
    if (i != 0) {
      $(this).html('<input type="text" />');
    }
  });

  t.columns().every(function() {
    var that = this;
    $("input", this.footer()).on("keyup change clear", function() {
      if (that.search() !== this.value) {
        that.search(this.value).draw();
      }
    });
  });
});
