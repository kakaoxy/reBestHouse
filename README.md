# Vue FastAPI Admin - 房源管理系统

一个基于 Vue 3 和 FastAPI 的现代化房源管理系统。

## 功能特点

- 🏠 小区管理
  - 按城市筛选小区
  - 小区基本信息维护
  - 支持多城市数据管理

- 🏢 二手房管理
  - 房源信息录入与管理
  - 按小区、价格、面积等多维度筛选
  - 自动计算单价

- 👥 用户权限管理
  - 基于角色的访问控制
  - 完整的用户管理功能
  - 操作日志审计

## 技术栈

### 后端
- FastAPI
- Tortoise ORM
- SQLite
- Python 3.8+

### 前端
- Vue 3
- Naive UI
- Pinia
- Vue Router

## 快速开始

### 后端启动

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows 使用 venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python fix_db.py

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 9999 --reload
```

### 前端启动

```bash
cd web

# 安装依赖
npm install

# 开发环境启动
npm run dev

# 生产环境构建
npm run build
```

## 项目结构

```
.
├── app/                    # 后端代码
│   ├── api/               # API 路由
│   ├── models/            # 数据模型
│   ├── schemas/           # 数据验证
│   └── core/             # 核心功能
├── web/                   # 前端代码
│   ├── src/              
│   │   ├── views/        # 页面组件
│   │   ├── components/   # 通用组件
│   │   ├── stores/       # 状态管理
│   │   └── api/         # API 调用
└── tests/                # 测试代码
```

## 开发指南

1. 添加新的小区：
   - 选择城市
   - 填写小区基本信息
   - 提交保存

2. 添加新的房源：
   - 选择所属小区
   - 填写房源详细信息
   - 系统自动计算单价

## 许可证

[MIT License](LICENSE)
