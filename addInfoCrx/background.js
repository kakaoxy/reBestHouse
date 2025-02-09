chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'exportExcel') {
    const data = request.data;
    
    if (data.length === 0) {
      console.error('没有数据可导出');
      sendResponse({ success: false, error: '没有数据可导出' });
      return true;
    }
    
    try {
      // 获取表头
      const headers = Object.keys(data[0]);
      
      // 创建CSV内容
      let csvContent = '\ufeff'; // 添加BOM标记支持中文
      
      // 添加表头
      csvContent += headers.map(header => `"${header}"`).join(',') + '\n';
      
      // 添加数据行
      data.forEach(record => {
        const row = headers.map(header => {
          const value = record[header] || '';
          // 处理包含逗号、换行符或引号的值
          if (/[,\n"]/.test(value)) {
            return `"${value.replace(/"/g, '""')}"`;
          }
          return value;
        });
        csvContent += row.join(',') + '\n';
      });

      // 将CSV内容转换为Base64
      const base64Content = btoa(unescape(encodeURIComponent(csvContent)));
      const dataUrl = 'data:text/csv;charset=utf-8;base64,' + base64Content;
      
      // 获取当前时间作为文件名的一部分
      const now = new Date();
      const timestamp = now.toISOString().replace(/[:.]/g, '-');
      
      // 根据导出数据类型生成文件名
      // 如果数据记录中存在 "成交价*" 字段，则认为为"成交信息"，否则为"在售信息"
      let exportType = data[0]['成交价*'] ? '成交信息' : '在售信息';
      // 使用 "小区名称*" 作为文件名前缀，若不存在则用 "未知小区"
      let community = data[0]['小区名称*'] || '未知小区';
      community = community.trim();
      const filename = `${community}_${exportType}-${timestamp}.csv`;
      
      // 下载文件
      chrome.downloads.download({
        url: dataUrl,
        filename: filename,
        saveAs: true
      }, (downloadId) => {
        // 检查下载是否成功启动
        if (chrome.runtime.lastError) {
          console.error('下载出错:', chrome.runtime.lastError);
          sendResponse({ 
            success: false, 
            error: chrome.runtime.lastError.message 
          });
        } else {
          console.log('下载已开始，ID:', downloadId);
          sendResponse({ 
            success: true, 
            downloadId: downloadId 
          });
        }
      });
      
      return true; // 保持消息通道开启
    } catch (error) {
      console.error('导出CSV时出错:', error);
      sendResponse({ 
        success: false, 
        error: error.message 
      });
      return true;
    }
  }
  return true;
});

// 监听所有端口连接
chrome.runtime.onConnect.addListener((port) => {
  if (port.name === "crawlProgress") {
    console.log("接收到 crawlProgress 端口连接");

    // 可选：监听来自内容脚本的消息
    port.onMessage.addListener((msg) => {
      console.log("接收到 crawlProgress 消息：", msg);
      // 根据需要处理消息，或直接保持空实现
    });

    // 监听端口断开
    port.onDisconnect.addListener(() => {
      console.log("crawlProgress 端口已断开");
    });
  }
}); 