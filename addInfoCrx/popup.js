let crawledData = null;

function showPreview(data) {
  const previewArea = document.getElementById('previewArea');
  const table = document.getElementById('previewTable');
  const thead = table.querySelector('thead tr');
  const tbody = table.querySelector('tbody');
  const buttons = document.querySelector('.buttons');
  
  // 清空现有内容
  thead.innerHTML = '';
  tbody.innerHTML = '';
  
  // 显示预览区域和按钮
  previewArea.style.display = 'block';
  buttons.style.display = 'block';
  
  // 添加表头
  const headers = Object.keys(data[0]);
  headers.forEach(header => {
    const th = document.createElement('th');
    th.textContent = header;
    thead.appendChild(th);
  });
  
  // 添加前5条数据
  const previewData = data.slice(0, 5);
  previewData.forEach(record => {
    const tr = document.createElement('tr');
    headers.forEach(header => {
      const td = document.createElement('td');
      td.textContent = record[header] || '';
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
}

// 修改爬取按钮事件
document.getElementById('crawlBtn').addEventListener('click', async () => {
  const statusDiv = document.getElementById('status');
  const btn = document.getElementById('crawlBtn');
  let progressDiv = document.querySelector('.progress');
  
  try {
    btn.disabled = true;
    statusDiv.textContent = '正在爬取数据，请稍候...';
    
    const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
    console.log('当前页面URL:', tab.url);  // 添加URL日志

    // 创建或重置进度条
    if (!progressDiv) {
      progressDiv = document.createElement('div');
      progressDiv.className = 'progress';
      statusDiv.after(progressDiv);
    }
    progressDiv.style.display = 'none';
    progressDiv.innerHTML = `
      <div class="progress-bar">
        <div class="progress-fill"></div>
      </div>
      <div class="progress-text"></div>
    `;

    // 创建端口连接监听
    chrome.runtime.onConnect.addListener((port) => {
      if (port.name === "crawlProgress") {
        port.onMessage.addListener((response) => {
          try {
            if (!response.success) {
              throw new Error(response.error || '爬取失败');
            }

            if (response.type === 'progress') {
              const progress = response.progress;
              switch (progress.type) {
                case 'total':
                  progressDiv.style.display = 'block';
                  statusDiv.textContent = `共找到 ${progress.total} 个房源`;
                  break;
                case 'progress':
                  progressDiv.style.display = 'block';
                  const percent = (progress.current / progress.total * 100).toFixed(1);
                  progressDiv.querySelector('.progress-fill').style.width = `${percent}%`;
                  progressDiv.querySelector('.progress-text').textContent = progress.message;
                  break;
                case 'error':
                  console.warn(progress.message);
                  break;
                case 'complete':
                  progressDiv.style.display = 'none';
                  statusDiv.textContent = `爬取完成，共获取 ${progress.total} 条记录`;
                  break;
              }
            }
          } catch (error) {
            statusDiv.textContent = '错误：' + error.message;
            console.error('消息处理错误:', error);
            btn.disabled = false;
            progressDiv.style.display = 'none';
          }
        });
      }
    });

    // 根据URL判断页面类型并发送对应的爬取命令
    const isChengjiao = tab.url.includes('/chengjiao/');
    const isErshoufang = tab.url.includes('/ershoufang/');
    
    if (!isChengjiao && !isErshoufang) {
      throw new Error('请在某壳成交记录或在售房源页面使用此功能');
    }

    const action = isChengjiao ? 'crawl' : 'crawlOnSale';
    console.log('爬取类型:', action);  // 添加动作类型日志

    // 发送爬取命令
    chrome.tabs.sendMessage(tab.id, {action: action}, (response) => {
      if (chrome.runtime.lastError) {
        console.error('消息发送错误:', chrome.runtime.lastError.message);
        statusDiv.textContent = '当前页面未注入脚本，请在目标页面使用该功能。';
        btn.disabled = false;
        return;
      }

      if (response && response.type === 'data') {
        if (!response.data || response.data.length === 0) {
          statusDiv.textContent = '未找到房源数据';
          btn.disabled = false;
          return;
        }
        
        // 显示数据预览和保存按钮
        statusDiv.textContent = `已找到 ${response.data.length} 条记录，请确认数据是否正确：`;
        crawledData = response.data;
        showPreview(response.data);
        
        // 显示确认和取消按钮
        document.querySelector('.buttons').style.display = 'block';
        
        // 数据获取完成后启用按钮
        btn.disabled = false;
        
        // 滚动到预览区域
        document.getElementById('previewArea').scrollIntoView({ behavior: 'smooth' });
      }
    });

  } catch (error) {
    statusDiv.textContent = '错误：' + error.message;
    console.error('操作错误:', error);
    btn.disabled = false;
  }
});

// 确认按钮事件
document.getElementById('confirmBtn').addEventListener('click', async () => {
  if (!crawledData) return;
  
  const statusDiv = document.getElementById('status');
  const btn = document.getElementById('confirmBtn');
  btn.disabled = true;
  
  try {
    statusDiv.textContent = '正在处理数据...';
    
    // 1. 保存为CSV文件
    chrome.runtime.sendMessage({
      action: 'exportExcel',
      data: crawledData
    }, async (result) => {
      if (chrome.runtime.lastError) {
        statusDiv.textContent = '导出CSV失败：' + chrome.runtime.lastError.message;
        console.error('导出错误:', chrome.runtime.lastError);
        btn.disabled = false;
        return;
      }
      
      if (!result || !result.success) {
        statusDiv.textContent = '导出CSV失败：' + (result?.error || '未知错误');
        console.error('导出失败:', result?.error);
        btn.disabled = false;
        return;
      }
      
      // 移除后端API调用功能，直接更新提示信息
      statusDiv.textContent = `处理完成！
      CSV文件已保存（下载ID: ${result.downloadId}）
      后端API调用功能已移除`;
      
      // 隐藏预览区域和操作按钮
      document.getElementById('previewArea').style.display = 'none';
      document.querySelector('.buttons').style.display = 'none';
    });
  } catch (error) {
    statusDiv.textContent = '处理失败：' + error.message;
    console.error('处理错误:', error);
    btn.disabled = false;
  }
});

// 取消按钮事件
document.getElementById('cancelBtn').addEventListener('click', () => {
  const statusDiv = document.getElementById('status');
  statusDiv.textContent = '已取消导出';
  
  // 隐藏预览和按钮
  document.getElementById('previewArea').style.display = 'none';
  document.querySelector('.buttons').style.display = 'none';
  crawledData = null;
}); 