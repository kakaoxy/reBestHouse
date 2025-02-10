// 将getCommunityId函数移到最外层作用域
const getCommunityId = (url) => {
  // 尝试从URL中提取小区ID
  const match = url.match(/\/(?:pg\d+)?c(\d+)/);
  if (match) {
    return match[1];
  }
  return '';
};

// 新增辅助函数：将中文城市名转换为对应拼音（映射可根据需要添加）
const cityMapping = {
  "上海": "shanghai",
  "北京": "beijing",
  "广州": "guangzhou",
  "深圳": "shenzhen",
  // 可根据需要添加更多映射...
};

const convertCityToPinyin = (city) => {
  for (const key in cityMapping) {
    if (city.includes(key)) {
      return cityMapping[key];
    }
  }
  return city.toLowerCase();
};

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'crawl') {
    console.log('开始爬取流程...');
    console.log('当前页面URL:', window.location.href);
    
    // 创建一个端口连接
    const port = chrome.runtime.connect({name: "crawlProgress"});

    const scrollAndCollectData = async () => {
      try {
        // 检查是否为成交页面，只要URL包含chengjiao即可
        if (!window.location.href.match(/\.ke\.com\/.*chengjiao/)) {
          console.error('页面URL不符合要求');
          throw new Error('请在某壳成交记录页面使用此功能');
        }

        // 获取小区ID
        const communityId = getCommunityId(window.location.href);
        console.log('提取的小区ID:', communityId);

        // 滚动加载函数
        const scrollToBottom = async () => {
          return new Promise((resolve) => {
            let currentPosition = 0;
            const maxPosition = document.documentElement.scrollHeight;
            const scrollStep = window.innerHeight / 2; // 每次滚动半个屏幕高度
            const scrollDelay = 500; // 滚动间隔时间

            console.log('开始页面滚动加载...');
            console.log('页面总高度:', maxPosition);

            const scroll = async () => {
              if (currentPosition >= maxPosition) {
                window.scrollTo(0, 0); // 滚回顶部
                console.log('滚动加载完成');
                // 等待最后的图片加载
                await new Promise(resolve => setTimeout(resolve, 1000));
                resolve();
                return;
              }

              currentPosition = Math.min(currentPosition + scrollStep, maxPosition);
              window.scrollTo(0, currentPosition);
              console.log(`滚动到位置: ${currentPosition}/${maxPosition}`);

              // 等待图片加载
              await new Promise(resolve => setTimeout(resolve, scrollDelay));

              // 检查当前可见区域内的图片是否已加载
              const visibleImages = document.querySelectorAll('img[data-original]');
              console.log(`检测到 ${visibleImages.length} 张待加载的图片`);

              visibleImages.forEach(img => {
                if (img.src.includes('default_block.png')) {
                  const original = img.getAttribute('data-original');
                  if (original) {
                    console.log('加载图片:', original);
                    img.src = original;
                  }
                }
              });

              scroll();
            };

            scroll();
          });
        };

        // 执行滚动加载
        await scrollToBottom();

        console.log('开始查找成交记录...');
        // 获取所有成交记录列表项
        const deals = document.querySelectorAll('#beike > div.dealListPage > div.content > div.leftContent > div:nth-child(4) > ul > li');
        console.log('找到成交记录数量:', deals.length);

        if (!deals || deals.length === 0) {
          throw new Error('页面上未找到成交记录');
        }

        // 发送总数信息
        port.postMessage({
          success: true,
          type: 'progress',
          progress: {
            type: 'total',
            total: deals.length
          }
        });

        const pageData = [];

        for (const [index, deal] of deals.entries()) {
          try {
            // 发送进度信息
            port.postMessage({
              success: true,
              type: 'progress',
              progress: {
                type: 'progress',
                current: index + 1,
                total: deals.length,
                message: `正在处理第 ${index + 1}/${deals.length} 个房源...`
              }
            });

            console.log(`开始处理第 ${index + 1} 条记录...`);
            
            // 优化后的成交信息记录构造
            // 1. 小区名称*（使用新选择器）
            const communityElem = document.querySelector('#beike > div.dealListPage > div.content > div.leftContent > div.contentBottom.clear > div.crumbs.fl > h1 > a');
            const communityName = communityElem ? communityElem.textContent.trim().replace(/二手房成交/g, "") : '';

            // 2. 所在区域和所在商圈（使用新的选择器）
            const areaElem = document.querySelector('#beike > div.dealListPage > div.content > div.leftContent > div.contentBottom.clear > div.crumbs.fl > a:nth-child(5)');
            const areaField = areaElem ? areaElem.textContent.trim().replace(/二手房成交/g, "") : '';
            const commerceElem = document.querySelector('#beike > div.dealListPage > div.content > div.leftContent > div.contentBottom.clear > div.crumbs.fl > a:nth-child(7)');
            const commerceField = commerceElem ? commerceElem.textContent.trim().replace(/二手房成交/g, "") : '';

            // 3. 户型与建筑面积*（从标题获取，格式形如 "馨浦苑东区 2室1厅 74.49平米"）
            const titleElem = deal.querySelector('div.title > a');
            const titleText = titleElem ? titleElem.textContent.trim() : '';
            const titleParts = titleText.split(' ');
            const huxing = titleParts[1] || '';
            const mianji = titleParts[2] ? titleParts[2].replace('平米', '') : '';

            // 4. 楼层信息、所在楼层、总楼层、建筑年代与建筑结构（皆从位置详情中取值）
            const posElem = deal.querySelector('div.flood > div.positionInfo');
            const posText = posElem ? posElem.textContent.trim() : '';
            let currentFloor = "";
            let totalFloor = "";
            let floorPrefix = "";

            // 先尝试提取总楼层（这个是最容易确定的）
            let totalFloorMatch = posText.match(/共(\d+)层/);
            totalFloor = totalFloorMatch ? totalFloorMatch[1] : "";

            // 尝试提取楼层前缀（低楼层/中楼层/高楼层）
            let prefixMatch = posText.match(/(低|中|高)楼层/);
            if (prefixMatch) {
                floorPrefix = prefixMatch[1] + "楼层";
            }

            // 尝试提取具体楼层数字
            let specificFloorMatch = posText.match(/^(\d+)层/);
            if (specificFloorMatch) {
                currentFloor = specificFloorMatch[1];
            }

            // 组装楼层信息
            let floorInfoFormatted = "";
            if (currentFloor) {
                // 如果有具体楼层
                floorInfoFormatted = `${currentFloor}/共${totalFloor}层`;
            } else if (floorPrefix) {
                // 如果有楼层前缀（低/中/高）
                floorInfoFormatted = `${floorPrefix}/共${totalFloor}层`;
            } else if (totalFloor) {
                // 如果只有总楼层
                floorInfoFormatted = `/共${totalFloor}层`;
            }

            // 提取建筑年代：匹配 4 位数字后紧跟 "年"
            let yearMatch = posText.match(/(\d{4})年/);
            let buildingYear = yearMatch ? yearMatch[1] : "";

            // 提取建筑结构：如 "2014年板楼"，取 "年" 后面的内容
            let structureMatch = posText.match(/\d{4}年\s*(.+)/);
            let buildingStructure = structureMatch ? structureMatch[1].trim() : "";

            // 5. 房屋朝向和装修（从houseInfo中，预期格式 "南 | 简装"）
            const houseInfoElem = deal.querySelector('div.address > div.houseInfo');
            let houseInfoText = houseInfoElem ? houseInfoElem.textContent.trim() : '';
            let infoParts = houseInfoText.split('|');
            let orientation = infoParts[0] ? infoParts[0].trim().replace(/\s+/g, "") : '';
            if(orientation && !orientation.startsWith("朝")){
              orientation = "朝" + orientation;
            }
            let decoration = infoParts[1] ? infoParts[1].trim() : '';

            // 6. 挂牌价（从dealCycleeInfo中提取，去除"挂牌"与"万"）
            const guapaiElem = deal.querySelector('div.dealCycleeInfo > span.dealCycleTxt > span:nth-child(1)');
            let guapaiText = guapaiElem ? guapaiElem.textContent.trim() : '';
            let guapai = guapaiText.replace("挂牌", "").replace("万", "").trim();

            // 7. 成交价*（从totalPrice中）
            const chengjiaoElem = deal.querySelector('div.address > div.totalPrice > span');
            let chengjiaoPrice = chengjiaoElem ? chengjiaoElem.textContent.trim() : '';

            // 8. 单价(元/平)（从unitPrice中）
            const danjiaElem = deal.querySelector('div.flood > div.unitPrice > span');
            let danjia = danjiaElem ? danjiaElem.textContent.trim() : '';

            // 9. 成交时间*（从dealDate中，替换点为斜杠）
            const timeElem = deal.querySelector('div.address > div.dealDate');
            let chengjiaoTime = timeElem ? timeElem.textContent.trim().replace(/\./g, "/") : '';

            // 10. 成交周期（去除"成交周期"与"天"）
            const cycleElem = deal.querySelector('div.dealCycleeInfo > span.dealCycleTxt > span:nth-child(2)');
            let cycleText = cycleElem ? cycleElem.textContent.trim() : '';
            let chengjiaoCycle = cycleText.replace("成交周期", "").replace("天", "").trim();

            // 11. 标签（如有）
            const spans = deal.querySelectorAll('div.dealHouseInfo > span.dealHouseTxt > span');
            let tagText = '';
            let locationText = '';
            if (spans && spans.length >= 2) {
                // 两个 span 均存在：第一个为标签，第二个为位置
                tagText = spans[0].textContent.trim();
                locationText = spans[1].textContent.trim();
            } else if (spans && spans.length === 1) {
                const text = spans[0].textContent.trim();
                if (text.startsWith('距')) {
                    // 单个 span且以"距"开头，视为位置
                    locationText = text;
                } else if (text.includes('满')) {
                    // 单个 span且含"满"，视为标签
                    tagText = text;
                } else {
                    // 其他情况归为位置
                    locationText = text;
                }
            }

            // 12. 户型图链接（图片src，从a下的img）
            const imgElem = deal.querySelector('a > img');
            let huXingImage = imgElem ? imgElem.getAttribute("src") : '';

            // 13. 房源链接（从标题链接）
            const houseLink = titleElem ? titleElem.href : '';

            // 14. 所在城市（全局，取页面底部城市并转为拼音）
            const cityElem = document.querySelector('#beike > div.dealListPage > div.content > div.leftContent > div.contentBottom.clear > div.crumbs.fl > a:nth-child(1)');
            let city = cityElem ? cityElem.textContent.trim().replace("房产", "") : "";
            city = convertCityToPinyin(city);

            // 16. 中介公司（此处假设使用经纪人信息，如果不存在则为空）
            const brokerElem = deal.querySelector('div.agentCardWrap > div.agentName');
            let broker = brokerElem ? brokerElem.textContent.trim() : '链家';

            // 17. 平台房源ID（从房源链接中提取数字ID）
            let platformID = "";
            if(houseLink){
              let idMatch = houseLink.match(/\/(\d+)\.html/);
              if(idMatch) platformID = idMatch[1];
            }

            const record = {
              '小区名称*': communityName,
              '所在区域': areaField,
              '所在商圈': commerceField,
              '户型': huxing,
              '建筑面积*': mianji,
              '楼层信息': floorInfoFormatted,
              '所在楼层': currentFloor,
              '总楼层': totalFloor,
              '房屋朝向': orientation,
              '挂牌价': guapai,
              '成交价*': chengjiaoPrice,
              '单价(元/平)': danjia,
              '成交时间*': chengjiaoTime,
              '成交周期': chengjiaoCycle,
              '标签': tagText,
              '户型图链接': huXingImage,
              '房源链接': houseLink,
              '所在城市': city,
              '建筑年代': buildingYear,
              '建筑结构': buildingStructure,
              '位置': locationText,
              '装修': decoration,
              '中介公司': broker,
              '数据来源': 'import',
              '平台房源ID': platformID
            };

            console.log(`第 ${index + 1} 条记录的小区ID:`, communityId);
            pageData.push(record);
          } catch (err) {
            console.error(`处理第 ${index + 1} 条记录时出错:`, err);
            port.postMessage({
              success: true,
              type: 'progress',
              progress: {
                type: 'error',
                message: `处理第 ${index + 1} 个房源时出错: ${err.message}`
              }
            });
          }
        }

        if (pageData.length === 0) {
          throw new Error('未能成功提取任何记录数据');
        }

        console.log('所有记录处理完成，总数:', pageData.length);
        
        // 发送完成信息
        port.postMessage({
          success: true,
          type: 'progress',
          progress: {
            type: 'complete',
            total: pageData.length
          }
        });

        // 最终数据直接使用 pageData，字段顺序已在 record 对象中设定
        const finalData = pageData;

        // 发送响应时使用finalData
        sendResponse({
          success: true,
          type: 'data',
          data: finalData
        });

        return finalData;

      } catch (error) {
        console.error('爬取过程发生错误:', error);
        port.postMessage({
          success: false,
          error: error.message
        });
        port.disconnect();
        throw error;
      }
    };

    // 执行爬取流程并发送响应
    scrollAndCollectData()
      .then(data => {
        console.log('爬取流程成功完成，准备发送数据...');
        sendResponse({
          success: true,
          type: 'data',
          data: data
        });
      })
      .catch(error => {
        console.error('爬取流程失败:', error.message);
        sendResponse({
          success: false,
          error: error.message
        });
      });

    // 告诉Chrome我们会异步发送响应
    return true;
  }

  // 添加在售房源爬取功能
  if (request.action === 'crawlOnSale') {
    console.log('开始爬取在售房源...');
    console.log('当前页面URL:', window.location.href);

    // 创建一个端口连接
    const port = chrome.runtime.connect({name: "crawlProgress"});

    const crawlOnSaleData = async () => {
      try {
        // 简化URL判断，只检查是否包含ershoufang
        if (!window.location.href.match(/\.ke\.com\/.*ershoufang/)) {
          throw new Error('请在某壳在售房源页面使用此功能');
        }

        // 获取小区ID
        const communityId = getCommunityId(window.location.href);
        console.log('提取的小区ID:', communityId);

        // 获取所有房源链接
        const houseLinks = document.querySelectorAll('#beike > div.sellListPage > div.content > div.leftContent > div:nth-child(4) > ul > li > div > div.title > a');
        console.log('找到房源链接数量:', houseLinks.length);

        // 发送总数信息
        port.postMessage({
          success: true,
          type: 'progress',
          progress: {
            type: 'total',
            total: houseLinks.length
          }
        });

        const pageData = [];

        // 遍历每个房源链接
        for (const [index, link] of Array.from(houseLinks).entries()) {
          try {
            // 发送进度信息
            port.postMessage({
              success: true,
              type: 'progress',
              progress: {
                type: 'progress',
                current: index + 1,
                total: houseLinks.length,
                message: `正在处理第 ${index + 1}/${houseLinks.length} 个房源...`
              }
            });

            console.log(`开始处理第 ${index + 1}/${houseLinks.length} 个房源...`);
            
            // 打开新窗口获取详情
            const response = await fetch(link.href);
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            const getTextContent = (selector, removeText = '') => {
              const element = doc.querySelector(selector);
              if (!element) return '';
              let text = element.textContent.trim();
              if (removeText) text = text.replace(removeText, '');
              return text;
            };

            // 提取房源信息
            const record = {
              // 按目标项目导入要求优化字段顺序
              '小区名称*': getTextContent('#beike > div.sellDetailPage > div:nth-child(6) > div.overview > div.content > div.aroundInfo > div.communityName > a.info.no_resblock_a'),
              '所在区域': getTextContent('#beike > div.sellDetailPage > div:nth-child(6) > div.overview > div.content > div.aroundInfo > div.areaName > span.info > a:nth-child(1)'),
              '所在商圈': getTextContent('#beike > div.sellDetailPage > div:nth-child(6) > div.overview > div.content > div.aroundInfo > div.areaName > span.info > a:nth-child(2)'),
              '户型*': getTextContent('#beike > div.sellDetailPage > div:nth-child(6) > div.overview > div.content > div.houseInfo > div.room > div.mainInfo'),
              '建筑面积*': getTextContent('#beike > div.sellDetailPage > div:nth-child(6) > div.overview > div.content > div.houseInfo > div.area > div.mainInfo')
                                .replace(/[建筑面积㎡平米]/g, '').trim(),
              '楼层信息': getTextContent('#beike > div.sellDetailPage > div:nth-child(6) > div.overview > div.content > div.houseInfo > div.room > div.subInfo'),
              '所在楼层': '',   // 将从"楼层信息"中解析出所在楼层
              '总楼层': '',     // 将从"楼层信息"中解析出总楼层
              '房屋朝向': getTextContent('#beike > div.sellDetailPage > div:nth-child(6) > div.overview > div.content > div.houseInfo > div.type > div.mainInfo')
                        .replace(/\s+/g, ''), // 移除所有空格
              '梯户比': getTextContent('#introduction > div > div > div.base > div.content > ul > li:nth-child(11)', '梯户比例').replace(/\s+/g, ''),
              '总价(万)*': getTextContent('#beike > div.sellDetailPage > div:nth-child(6) > div.overview > div.content > div.price-container > div > span.total'),
              '单价(元/平)': getTextContent('#beike > div.sellDetailPage > div:nth-child(6) > div.overview > div.content > div.price-container > div > div.text > div.unitPrice > span'),
              '挂牌时间': getTextContent('#introduction > div > div > div.transaction > div.content > ul > li:nth-child(1)', '挂牌时间'),
              '上次交易时间': getTextContent('#introduction > div > div > div.transaction > div.content > ul > li:nth-child(3)', '上次交易'),
              '抵押信息': getTextContent('#introduction > div > div > div.transaction > div.content > ul > li:nth-child(7) > span:nth-child(2)'),
              '户型图链接': doc.querySelector('#layout > div.layout > div.content > div.imgdiv > img')?.src || '',
              '房源链接': link.href,
              '所在城市': getTextContent('#beike > div.sellDetailPage > div:nth-child(4) > div.intro.clear > div > div > a:nth-child(1)')
                        .replace(/房产$/, '').trim(),  // 移除"房产"后缀
              '建筑年代': '',    // 后续解析填充
              '建筑结构': '',    // 后续解析填充
              '数据来源': 'import',
              '平台房源ID': getTextContent('#beike > div.sellDetailPage > div:nth-child(6) > div.overview > div.content > div.aroundInfo > div.houseRecord > span.info')
                                .replace(/[^\d]/g, '')
            };

            // 解析"楼层信息"，提取"所在楼层"和"总楼层"
            const floorInfo = record['楼层信息'];
            const floorNumbers = floorInfo.match(/(\d+)/g);
            if (floorNumbers && floorNumbers.length >= 2) {
              record['所在楼层'] = floorNumbers[0];
              record['总楼层'] = floorNumbers[1];
            }

            // 处理建筑信息，解析出建筑年代与建筑结构
            const buildingInfo = getTextContent('#beike > div.sellDetailPage > div:nth-child(6) > div.overview > div.content > div.houseInfo > div.area > div.subInfo.noHidden');
            if (buildingInfo) {
              const yearMatch = buildingInfo.match(/(\d{4})年/);
              // 提取斜杠后的所有内容作为建筑结构
              let structureMatch = buildingInfo.match(/\/\s*(.+)/);
              record['建筑年代'] = yearMatch ? yearMatch[1] : '';
              record['建筑结构'] = structureMatch ? structureMatch[1].trim() : '';
            }

            console.log(`第 ${index + 1} 条记录:`, record);
            pageData.push(record);

            // 随机等待1-3秒
            const waitTime = Math.floor(Math.random() * 2000) + 1000;
            await new Promise(resolve => setTimeout(resolve, waitTime));

          } catch (err) {
            console.error(`处理第 ${index + 1} 个房源时出错:`, err);
            port.postMessage({
              success: true,
              type: 'progress',
              progress: {
                type: 'error',
                message: `处理第 ${index + 1} 个房源时出错: ${err.message}`
              }
            });
          }
        }

        if (pageData.length === 0) {
          throw new Error('未能成功提取任何记录数据');
        }

        console.log('所有记录处理完成，总数:', pageData.length);
        
        // 发送完成信息
        port.postMessage({
          success: true,
          type: 'progress',
          progress: {
            type: 'complete',
            total: pageData.length
          }
        });

        // 最终数据直接使用 pageData，字段顺序已在 record 对象中设定
        const finalData = pageData;

        // 发送响应时使用finalData
        sendResponse({
          success: true,
          type: 'data',
          data: finalData
        });

        return finalData;

      } catch (error) {
        console.error('爬取过程发生错误:', error);
        port.postMessage({
          success: false,
          error: error.message
        });
        port.disconnect();
        
        // 确保错误也通过sendResponse发送
        sendResponse({
          success: false,
          error: error.message
        });
        
        throw error;
      }
    };

    // 执行爬取流程
    crawlOnSaleData().catch(error => {
      console.error('爬取流程失败:', error.message);
    });

    return true; // 保持消息通道开启
  }
}); 