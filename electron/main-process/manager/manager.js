const { ipcMain, dialog, BrowserWindow} = require("electron");
const path = require('path');

ipcMain.on("open-error-dialog", function(event) {
  dialog.showErrorBox("错误信息", "您并未选中任何条目");
});

ipcMain.on("create-window", function() {
  // $("body").addClass("mask");
  const modalPath = path.join(
    "file://",
    __dirname,
    "../../sections/manager/train.html"
  );
  // dialog.showErrorBox('123',mainWin.getBounds())
  let win = new BrowserWindow({
    frame: false,
    resizable: false,
    // parent: mainWindow,
    // modal: true,
    
    webPreferences: {
      nodeIntegration: true
    }
  });
  win.on("close", function() {
    // $("body").removeClass("mask");
    win = null;
  });
  win.loadURL(modalPath);
  win.show();
});

ipcMain.on('open-information-dialog', (event,arg) => {
  const options = {
    type: 'info',
    title: '训练结果',
    message: "本次训练结果为：\n"+arg+"\n是否覆盖分类器",
    buttons: ['是', '否']
  }
  dialog.showMessageBox(options, (index) => {
    event.sender.send('information-dialog-selection', index)
  })
})
