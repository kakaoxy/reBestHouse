from typing import Dict
from fastapi import Response, HTTPException
from fastapi.responses import StreamingResponse
from app.core.crud import CRUDBase
from app.schemas.ai import AIReportRequest
from app.models.house import Opportunity
import logging
import requests
import json
import asyncio
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# print(os.getenv('COZE_API_KEY'))
# print(os.getenv('COZE_BOT_ID'))

class AIReportController:
    def __init__(self):
        self.url = "https://api.coze.cn/v3/chat"
        self.headers = {
            "Authorization": f"Bearer {os.getenv('COZE_API_KEY')}",
            "Content-Type": "application/json"
        }
        self.bot_id = os.getenv('COZE_BOT_ID')

    async def generate_report(self, data: AIReportRequest):
        """生成AI分析报告（流式响应）"""
        print(data)
        async def generate():
            try:
                # 添加商机查询日志
                # logging.info(f"正在查询商机ID: {data.opportunity_id}")
                opportunity = await Opportunity.get_or_none(id=data.opportunity_id).prefetch_related('community')
                if not opportunity:
                    # logging.error(f"商机不存在，ID: {data.opportunity_id}")
                    raise HTTPException(status_code=404, detail="商机不存在")

                # 添加数据统计日志
                listing_count = await opportunity.community.houses.all().count()
                deal_count = await opportunity.community.deal_records.all().count()
                # logging.info(f"商机统计数据 - 在售: {listing_count}, 成交: {deal_count}")

                # 构建提示词
                # 获取在售房源数据
                listing_houses = await opportunity.community.houses.all()
                listing_details = [
                    f"在售房源{i+1}: {house.layout}户型, {house.area}平米, "
                    f"{house.floor or '--'}楼层, "
                    f"{house.total_price}万元, "
                    f"单价{house.unit_price or '--'}元/㎡"
                    for i, house in enumerate(listing_houses)
                ]

                # 获取成交房源数据
                deal_records = await opportunity.community.deal_records.all()
                deal_details = [
                    f"成交记录{i+1}: {record.layout}户型, {record.area}平米, "
                    f"{record.floor_info or record.floor or '--'}楼层, "
                    f"{record.total_price}万元, "
                    f"单价{record.unit_price or '--'}元/㎡, "
                    f"成交周期{record.deal_cycle or '--'}天, "
                    f"成交时间{record.deal_date}"
                    for i, record in enumerate(deal_records)
                ]

                prompt = f"""请对以下房产信息进行分析并输出卖房建议报告，报告的用户是业主，主要目标是说服业主以合理价格进行委托，业主的目标是在3个月内完成销售，报告内容需要简单易懂说人话，逻辑清晰，理论依据充分，需要考虑市场趋势和房屋户型以及所在楼层的优缺点，目标销售周期要控制在3个月以内：
                小区名称：{opportunity.community.name}
                户型：{opportunity.layout or '--'}
                楼层：{opportunity.floor or '--'}
                面积：{opportunity.area or '--'}平方米
                总价：{opportunity.total_price or '--'}万元
                在售房源数：{listing_count}套
                成交数量：{deal_count}套

                在售房源详情：
                {chr(10).join(listing_details) if listing_details else "暂无在售房源"}

                历史成交记录：
                {chr(10).join(deal_details) if deal_details else "暂无成交记录"}"""

                # 记录API请求数据
                request_data = {
                    "bot_id": self.bot_id,
                    "user_id": "system",
                    "stream": True,
                    "auto_save_history": True,
                    "additional_messages": [
                        {
                            "role": "user",
                            "content": prompt,
                            "content_type": "text"
                        }
                    ]
                }
                # logging.info(f"准备发送到Coze API的数据: {request_data}")

                response = requests.post(
                    self.url,
                    headers=self.headers,
                    json=request_data,
                    stream=True
                )

                if response.status_code == 200:
                    event_type = None
                    filter_active = False  # 添加过滤标记

                    for line in response.iter_lines():
                        if filter_active:
                            continue

                        if not line:
                            continue

                        try:
                            sse_line = line.decode('utf-8').strip()
                            
                            # 处理事件类型
                            if sse_line.startswith('event:'):
                                event_type = sse_line.split(':', 1)[1].strip()
                                continue

                            # 处理数据
                            if sse_line.startswith('data:'):
                                json_str = sse_line.split(':', 1)[1].strip()
                                if json_str:
                                    response_data = json.loads(json_str)
                                    
                                    # 处理系统消息
                                    if response_data.get('msg_type') == 'generate_answer_finish':
                                        filter_active = True
                                        continue

                                    # 处理 reasoning_content
                                    if 'reasoning_content' in response_data:
                                        content = response_data['reasoning_content']
                                        if content:
                                            yield f"data: {json.dumps({'content': content})}\n\n"
                                    
                                    # 处理普通内容
                                    if event_type == 'conversation.message.delta':
                                        content = response_data.get('content', '')
                                        if isinstance(content, dict):
                                            content = content.get('text', '')
                                        if content and not filter_active:
                                            yield f"data: {json.dumps({'content': content})}\n\n"
                                    
                                    # 处理完成事件
                                    elif event_type == 'conversation.message.completed':
                                        yield f"data: {json.dumps({'done': True})}\n\n"
                                        break

                        except json.JSONDecodeError as e:
                            logging.error(f"解析响应数据失败: {e}")
                            continue
                else:
                    error_msg = f"API请求失败: {response.status_code}"
                    logging.error(error_msg)
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"

            except Exception as e:
                error_msg = f"生成AI报告失败: {str(e)}"
                logging.error(error_msg)
                yield f"data: {json.dumps({'error': error_msg})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )

ai_report_controller = AIReportController()