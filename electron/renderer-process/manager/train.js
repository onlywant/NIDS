const { ipcRenderer } = require("electron");
const rpc = require("./../../assets/js/rpc.js");

$(function() {
  $(".input input").on("focus", function() {
    $(this)
      .parent()
      .addClass("focus");
  });

  $(".input input").on("blur", function() {
    if ($(this).val() === "")
      $(this)
        .parent()
        .removeClass("focus");
  });

  $(".submit").on("click", function() {
    $(this).toggleClass("active");
    setTimeout(() => {
      $(this).toggleClass("verity");
    }, 1000);
    $(this).attr("disabled", "disabled");
    $("#close").css({ display: "none" });

    $(".feedback").fadeIn(1500);
    $(".feedback").css({ display: "flex" });
    $(".training").fadeIn(1000);

    size = $("#size").val();
    circle = $("#circle").val();
    epoch = $("#epoch").val();
    rate = $("#rate").val();
    derate = $("#derate").val();
    addNew = $("#addNew").is(":checked");
    var training = (100/parseInt(circle)) - 1;
    var testing = 20;

    stream = rpc.trainAgain({
      size: size,
      circle: circle,
      epoch: epoch,
      Rate: rate,
      deRate: derate,
      addNew: addNew
    });

    var div = 1;
    stream.on("data", function(info) {
      if (div == 1) training = parseInt(info.mes);
      else if (div == 2) testing = parseInt(info.mes);
      else if (div == 3) {
        // $("#text-result").html(info.mes.slice(0, 5));
        // var $arg = $("#text-result");
        // console.log($arg.html());

        ipcRenderer.send("open-information-dialog", info.mes);
        ipcRenderer.on("information-dialog-selection", (event, index) => {
          if (index === 0) {
            rpc.coverModel(() => {
              $("#dialog-reply").html("操作成功，已经覆盖");
            });
          } else {
            $("#dialog-reply").html("操作成功，未进行覆盖");
          }
        });
      }
    });

    obj = setInterval(() => {
      if (training >= 100) {
        training = 100;
        div = 2;
        $(".training #bar").css({ width: "100%" });
        $(".testing").fadeIn(1000);
        obj1 = setInterval(() => {
          if (testing >= 100) {
            testing = 100;
            div = 3;
            $(".testing #bar").css({ width: "100%" });
            $("#close").toggle("display");
            clearInterval(obj1);
            // 按钮恢复
            // $(this).toggleClass("active");
            // $(this).removeAttr("disabled");
            // $(this).toggleClass("verity");
          }
          $(".testing #bar").css({ width: testing + "%" });
          $(".testing #text-progress").html("testing..." + testing + "%");
        }, 100);
        clearInterval(obj);
      }
      $(".training #bar").css({ width: training + "%" });
      $(".training #text-progress").html("training..." + training + "%");
    }, 100);
  });
});
