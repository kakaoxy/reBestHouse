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

class AIReportController:
    def __init__(self):
        self.url = "https://api.coze.cn/v3/chat"
        self.headers = {
            "Authorization": "Bearer pat_OvFpYuXNYoSi6iHIN4rBF6EUVy40i8DiBOpAbnXXUs1VOKsghsvApTnjCofyj4dG",
            "Content-Type": "application/json"
        }
        self.bot_id = "7468925434710310912"

    async def generate_report(self, data: AIReportRequest):
        """生成AI分析报告（流式响应）"""
        async def generate():
            try:
                # 添加商机查询日志
                logging.info(f"正在查询商机ID: {data.opportunity_id}")
                opportunity = await Opportunity.get_or_none(id=data.opportunity_id).prefetch_related('community')
                if not opportunity:
                    logging.error(f"商机不存在，ID: {data.opportunity_id}")
                    raise HTTPException(status_code=404, detail="商机不存在")

                # 添加数据统计日志
                listing_count = await opportunity.community.houses.all().count()
                deal_count = await opportunity.community.deal_records.all().count()
                logging.info(f"商机统计数据 - 在售: {listing_count}, 成交: {deal_count}")

                # 构建提示词
                prompt = f"""请对以下房产信息进行分析并生成投资建议报告：
                小区名称：{opportunity.community.name}
                户型：{opportunity.layout or '--'}
                楼层：{opportunity.floor or '--'}
                面积：{opportunity.area or '--'}平方米
                总价：{opportunity.total_price or '--'}万元
                在售房源数：{listing_count}套
                成交数量：{deal_count}套"""

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
                logging.info(f"准备发送到Coze API的数据: {request_data}")

                response = requests.post(
                    self.url,
                    headers=self.headers,
                    json=request_data,
                    stream=True
                )

                if response.status_code == 200:
                    event_type = None
                    for line in response.iter_lines():
                        if line:
                            try:
                                sse_line = line.decode('utf-8').strip()
                                if sse_line.startswith('event:'):
                                    event_type = sse_line.split(':', 1)[1].strip()
                                elif sse_line.startswith('data:'):
                                    json_str = sse_line.split(':', 1)[1].strip()
                                    if json_str:
                                        response_data = json.loads(json_str)
                                        if event_type == 'conversation.message.delta':
                                            content = response_data.get('content', '')
                                            if content:
                                                # 只发送增量内容
                                                yield f"data: {json.dumps({'content': content})}\n\n"
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