import asyncio
import httpx
import pytest
from datetime import datetime
import json
from app.models import Community

# 测试配置
BASE_URL = "http://localhost:9999/api/v1/house"
LOGIN_URL = "http://localhost:9999/api/v1/base/access_token"
USERNAME = "admin"
PASSWORD = "123456"

async def get_token():
    """获取登录token"""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Content-Type": "application/json"}
            login_data = {
                "username": USERNAME,
                "password": PASSWORD,
                "type": "account"
            }
            
            print(f"尝试登录: {LOGIN_URL}")
            print(f"登录数据: {login_data}")
            
            response = await client.post(
                LOGIN_URL,
                headers=headers,
                json=login_data,
                timeout=5.0
            )
            
            print(f"登录响应状态码: {response.status_code}")
            print(f"登录响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if "code" in result and result["code"] == 200 and "data" in result:
                    if "access_token" in result["data"]:
                        return result["data"]["access_token"]
                
                print(f"未知的登录响应格式: {result}")
                raise Exception("未知的登录响应格式")
            else:
                print(f"登录失败，状态码: {response.status_code}")
                raise Exception(f"登录失败: {response.text}")
                
        except Exception as e:
            print(f"登录失败: {str(e)}")
            if 'response' in locals():
                print(f"Response status code: {response.status_code}")
                print(f"Response text: {response.text}")
            raise

async def test_community_crud():
    """测试小区CRUD操作"""
    token = await get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "token": token,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        # 1. 创建小区
        create_data = {
            "name": "测试小区",
            "region": "测试区域",
            "area": "测试商圈",
            "address": "测试地址",
            "building_type": "住宅",
            "property_rights": "70年",
            "total_houses": 1000,
            "building_year": 2010
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/communities",
                headers=headers,
                json=create_data
            )
            
            print(f"Create response status: {response.status_code}")
            print(f"Create response headers: {response.headers}")
            print(f"Create response content: {response.text}")
            
            if response.status_code >= 400:
                raise Exception(f"创建小区失败: HTTP {response.status_code} - {response.text}")
            
            try:
                result = response.json()
                community_id = result.get("id") or result.get("data", {}).get("id")
                if not community_id:
                    raise Exception("响应中没有找到 community_id")
                print(f"创建小区成功: {result}")
            except json.JSONDecodeError as e:
                print(f"解析响应JSON失败: {str(e)}")
                print(f"原始响应内容: {response.text}")
                raise
                
        except Exception as e:
            print(f"创建小区时出错: {str(e)}")
            if 'response' in locals():
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {response.headers}")
                print(f"Response content: {response.text}")
            raise

        # 2. 获取小区列表
        response = await client.get(
            f"{BASE_URL}/communities",
            headers=headers,
            params={"name": "测试小区"}
        )
        assert response.status_code == 200
        assert len(response.json()) > 0
        print(f"获取小区列表成功: {response.json()}")

        # 3. 更新小区
        update_data = {
            "name": "更新后的测试小区",
            "total_houses": 1200
        }
        response = await client.put(
            f"{BASE_URL}/communities/{community_id}",
            headers=headers,
            json=update_data
        )
        assert response.status_code == 200
        print(f"更新小区成功: {response.json()}")

        # 4. 删除小区
        response = await client.delete(
            f"{BASE_URL}/communities/{community_id}",
            headers=headers
        )
        assert response.status_code == 200
        print("删除小区成功")

async def test_ershoufang_crud():
    """测试二手房CRUD操作"""
    token = await get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "token": token,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        # 首先创建一个小区
        community_data = {
            "name": "测试小区-二手房",
            "region": "测试区域",
            "area": "测试商圈"
        }
        response = await client.post(
            f"{BASE_URL}/communities",
            headers=headers,
            json=community_data
        )
        community_id = response.json()["id"]

        # 1. 创建二手房
        create_data = {
            "community_id": community_id,
            "house_id": "TEST001",
            "community_name": "测试小区-二手房",
            "region": "测试区域",
            "area": "测试商圈",
            "layout": "三室两厅",
            "size": 120.5,
            "floor": "中层/18层",
            "orientation": "南北通透",
            "total_price": 580.0,
            "unit_price": 48130.0,
            "data_source": "manual_input"
        }
        
        response = await client.post(
            f"{BASE_URL}/ershoufangs",
            headers=headers,
            json=create_data
        )
        assert response.status_code == 200
        ershoufang_id = response.json()["id"]
        print(f"创建二手房成功: {response.json()}")

        # 2. 获取二手房列表
        response = await client.get(
            f"{BASE_URL}/ershoufangs",
            headers=headers,
            params={
                "community_name": "测试小区-二手房",
                "total_price_min": 500,
                "total_price_max": 600
            }
        )
        assert response.status_code == 200
        assert len(response.json()) > 0
        print(f"获取二手房列表成功: {response.json()}")

        # 3. 更新二手房
        update_data = {
            "total_price": 600.0,
            "unit_price": 49793.0
        }
        response = await client.put(
            f"{BASE_URL}/ershoufangs/{ershoufang_id}",
            headers=headers,
            json=update_data
        )
        assert response.status_code == 200
        print(f"更新二手房成功: {response.json()}")

        # 4. 删除二手房
        response = await client.delete(
            f"{BASE_URL}/ershoufangs/{ershoufang_id}",
            headers=headers
        )
        assert response.status_code == 200
        print("删除二手房成功")

        # 最后删除试小区
        await client.delete(
            f"{BASE_URL}/communities/{community_id}",
            headers=headers
        )

@pytest.mark.asyncio
async def test_get_communities_by_city():
    token = await get_token()
    headers = {"token": token}
    
    # 创建测试数据
    await Community.create(
        name="测试北京",
        city="beijing",
        region="测试区域",
        area="测试商圈"
    )
    await Community.create(
        name="测试上海",
        city="shanghai",
        region="测试区域",
        area="测试商圈"
    )

    # 测试北京筛选
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/communities",
            params={"city": "beijing"},
            headers=headers
        )
        result = response.json()
        assert response.status_code == 200
        assert len(result["data"]["items"]) == 1
        assert result["data"]["items"][0]["city"] == "beijing"

    # 测试上海筛选
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/communities",
            params={"city": "shanghai"},
            headers=headers
        )
        result = response.json()
        assert response.status_code == 200
        assert len(result["data"]["items"]) == 1
        assert result["data"]["items"][0]["city"] == "shanghai"

async def test_deal_record_crud(client, token_headers):
    # 创建测试小区
    community_data = {
        "name": "测试小区",
        "city": "shanghai",
        "region": "浦东新区",
        "area": "陆家嘴"
    }
    community_response = await client.post("/v1/house/communities", json=community_data, headers=token_headers)
    community_id = community_response.json()["data"]["id"]

    # 测试创建成交记录
    deal_data = {
        "community_id": community_id,
        "source": "manual",
        "deal_date": "2024-03-20",
        "total_price": 500.0,
        "unit_price": 50000.0,
        "layout": "2室1厅",
        "size": 89.5,
        "floor_info": "中楼层/33层",
        "orientation": "南",
        "agency": "测试中介"
    }
    response = await client.post("/v1/house/deal-records", json=deal_data, headers=token_headers)
    assert response.status_code == 200
    deal_id = response.json()["data"]["id"]

    # 测试获取成交记录列表
    response = await client.get("/v1/house/deal-records", headers=token_headers)
    assert response.status_code == 200
    assert len(response.json()["data"]["items"]) > 0

    # 测试更新成交记录
    update_data = {
        "total_price": 520.0,
        "unit_price": 52000.0
    }
    response = await client.put(f"/v1/house/deal-records/{deal_id}", json=update_data, headers=token_headers)
    assert response.status_code == 200

    # 测试删除成交记录
    response = await client.delete(f"/v1/house/deal-records/{deal_id}", headers=token_headers)
    assert response.status_code == 200

async def main():
    """运行所有测试"""
    try:
        print("开始测试小区API...")
        await test_community_crud()
        print("\n开始测试二手房API...")
        await test_ershoufang_crud()
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 