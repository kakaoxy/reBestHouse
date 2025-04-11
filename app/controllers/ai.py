from typing import Dict
from fastapi import Response, HTTPException
from fastapi.responses import StreamingResponse
from app.core.crud import CRUDBase
from app.schemas.ai import AIReportRequest
from app.models.house import Opportunity
import logging
import json
import os
from dotenv import load_dotenv
from openai import OpenAI


# 初始化日志器
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

class AIReportController:
    def __init__(self):
        # 完全按照官方文档初始化客户端
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv('OPENROUTER_API_KEY')
        )
        self.model = os.getenv('OPENROUTER_MODEL', 'deepseek/deepseek-r1-zero:free')
        self.extra_headers = {
            "HTTP-Referer": os.getenv('SITE_URL', 'https://hitoday.top'),
            "X-Title": os.getenv('SITE_NAME', 'ReBestHouse')
        }

    

    async def generate_report(self, data: AIReportRequest):
        """生成AI分析报告（优化流式响应处理）"""
        print(f"Starting report generation for opportunity: {data.opportunity_id}")
        
        async def generate(data: AIReportRequest):
            try:
                # === 阶段1：获取商机和小区数据 ===
                print("Fetching opportunity and community data...")
                opportunity = await Opportunity.get_or_none(id=data.opportunity_id).prefetch_related('community')
                if not opportunity:
                    error_msg = f"Opportunity not found: {data.opportunity_id}"
                    logger.error(error_msg)
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"
                    return

                # === 阶段2：获取房源和成交数据 ===
                print("Fetching listing and deal records...")
                listing_count = await opportunity.community.houses.all().count()
                deal_count = await opportunity.community.deal_records.all().count()
                print(f"Found {listing_count} listings and {deal_count} deal records")
                
                # 保留原有数据获取方式
                listing_houses = await opportunity.community.houses.all()
                listing_details = [
                    f"在售房源{i+1}: {house.layout}户型, {house.area}平方米, "
                    f"{house.floor or '--'}楼层, "
                    f"{house.total_price}万元, "
                    f"单价{house.unit_price or '--'}元/㎡"
                    for i, house in enumerate(listing_houses)
                ]

                deal_records = await opportunity.community.deal_records.all()
                deal_details = [
                    f"成交记录{i+1}: {record.layout}户型, {record.area}平方米, "
                    f"{record.floor_info or record.floor or '--'}楼层, "
                    f"{record.total_price}万元, "
                    f"单价{record.unit_price or '--'}元/㎡, "
                    f"成交周期{record.deal_cycle or '--'}天, "
                    f"成交时间{record.deal_date}"
                    for i, record in enumerate(deal_records)
                ]

                # === 阶段3：构建提示词（保留原有结构和内容）===
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
                
                logger.debug(f"Constructed prompt with length: {len(prompt)} characters")

                # === 阶段4：调用OpenRouter API ===
                print("Preparing to call OpenRouter API...")
                try:
                    messages = [
                        {"role": "system", "content": "你是一个专业的房产经纪人，需要生成详细的卖房策略报告"},
                        {"role": "user", "content": prompt}
                    ]
                    
                    stream = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        stream=True,
                        extra_headers=self.extra_headers,
                        extra_body={}
                    )
                    print("API request successfully sent")
                except Exception as api_error:
                    logger.error(f"API call failed: {str(api_error)}")
                    yield f"data: {json.dumps({'error': f'API请求失败: {str(api_error)}'})}\n\n"
                    return

                # === 阶段5：优化后的流式响应处理 ===
                print("Processing streaming response...")
                chunk_counter = 0
                
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta:
                        delta = chunk.choices[0].delta
                        chunk_counter += 1
                        
                        # 合并content和reasoning字段
                        response_data = {}
                        if hasattr(delta, 'content') and delta.content:
                            response_data['content'] = delta.content
                        if hasattr(delta, 'reasoning') and delta.reasoning:
                            response_data['reasoning'] = delta.reasoning
                        
                        # 只要有数据就立即发送
                        if response_data:
                            yield f"data: {json.dumps(response_data)}\n\n"
                            print(f"{response_data}")
                
                yield f"data: {json.dumps({'done': True})}\n\n"

            except Exception as e:
                error_msg = f"生成报告时出现异常: {str(e)}"
                logger.error(error_msg, exc_info=True)
                yield f"data: {json.dumps({'error': error_msg})}\n\n"

        # 返回流式响应（增加超时时间）
        return StreamingResponse(
            generate(data),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

# 初始化控制器
try:
    ai_report_controller = AIReportController()
    print("AIReportController initialization complete")
except Exception as e:
    logger.critical(f"Controller initialization failed: {str(e)}")
    raise


# 单例模式初始化
ai_report_controller = AIReportController()
