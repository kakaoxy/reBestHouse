# 房源管理系统

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
  - 支持批量导入
  - 支持楼层、朝向筛选
  - 支持面积区间筛选

- 📊 成交记录管理
  - 成交房源信息录入
  - 支持户型、楼层筛选
  - 支持批量导入导出
  - 自动计算单价
  - 成交周期统计

- 💡 商机管理
  - 潜在房源信息录入
  - 商机状态跟踪
  - 支持标记满二/满五年
  - 支持户型图/室内图管理
  - 商机所有权分配
  - 商机评估与备注

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

### 快速开始
#### 方法一：dockerhub拉取镜像

```sh
docker pull mizhexiaoxiao/reBestHouse:latest 
docker run -d --restart=always --name=reBestHouse -p 9999:80 mizhexiaoxiao/reBestHouse
```

#### 方法二：dockerfile构建镜像
##### docker安装(版本17.05+)

```sh
yum install -y docker-ce
systemctl start docker
```

##### 构建镜像

```sh
git clone https://github.com/kakaoxy/reBestHouse.git
cd reBestHouse
docker build --no-cache . -t reBestHouse
```

##### 启动容器

```sh
docker run -d --restart=always --name=reBestHouse -p 9999:80 reBestHouse
```

##### 访问

http://localhost:9999

username：admin

password：123456

### 本地启动
#### 后端
启动项目需要以下环境：
- Python 3.11

#### 方法一（推荐）：[Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer) 安装依赖
1. 创建虚拟环境
```sh
poetry shell
```
2. 安装依赖
```sh
poetry install
```
3. 启动服务
```sh
make run
```
#### 方法二：Pip 安装依赖
1. 创建虚拟环境
```sh
python3.11 -m venv venv
```
2. 激活虚拟环境
```sh
source venv/bin/activate
```
3. 安装依赖
```sh
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
3. 启动服务
```sh
python run.py
```

服务现在应该正在运行，访问 http://localhost:9999/docs 查看API文档

#### 前端
启动项目需要以下环境：
- node v18.8.0+

1. 进入前端目录
```sh
cd web
```

2. 安装依赖(建议使用pnpm: https://pnpm.io/zh/installation)
```sh
npm i -g pnpm # 已安装可忽略
pnpm i # 或者 npm i
```

3. 启动
```sh
pnpm dev
```

## 项目结构

```
├── app                     // 应用程序目录
│   ├── api                // API接口目录
│   │   └── v1             // 版本1的API接口
│   │       ├── apis       // API相关接口
│   │       ├── base       // 基础信息接口
│   │       ├── house      // 房源相关接口
│   │       ├── menus      // 菜单相关接口
│   │       ├── roles      // 角色相关接口
│   │       └── users      // 用户相关接口
│   ├── controllers        // 控制器目录
│   ├── core               // 核心功能模块
│   ├── log               // 日志目录
│   ├── models            // 数据模型目录
│   ├── schemas           // 数据模式/结构定义
│   ├── settings          // 配置设置目录
│   └── utils             // 工具类目录
├── deploy                // 部署相关目录
│   └── sample-picture    // 示例图片目录
└── web                   // 前端网页目录
    ├── build             // 构建脚本和配置目录
    │   ├── config        // 构建配置
    │   ├── plugin        // 构建插件
    │   └── script        // 构建脚本
    ├── public            // 公共资源目录
    │   └── resource      // 公共资源文件
    ├── settings          // 前端项目配置
    └── src               // 源代码目录
        ├── api           // API接口定义
        ├── assets        // 静态资源目录
        │   ├── images    // 图片资源
        │   ├── js        // JavaScript文件
        │   └── svg       // SVG矢量图文件
        ├── components    // 组件目录
        │   ├── common    // 通用组件
        │   ├── icon      // 图标组件
        │   ├── page      // 页面组件
        │   ├── query-bar // 查询栏组件
        │   └── table     // 表格组件
        ├── composables   // 可组合式功能块
        ├── directives    // 指令目录
        ├── layout        // 布局目录
        │   └── components // 布局组件
        ├── router        // 路由目录
        │   ├── guard     // 路由守卫
        │   └── routes    // 路由定义
        ├── store         // 状态管理(pinia)
        │   └── modules   // 状态模块
        ├── styles        // 样式文件目录
        ├── utils         // 工具类目录
        │   ├── auth      // 认证相关工具
        │   ├── common    // 通用工具
        │   ├── http      // 封装axios
        │   └── storage   // 封装localStorage和sessionStorage
        └── views         // 视图/页面目录
            ├── error-page // 错误页面
            ├── house      // 房源管理页面
            │   ├── community     // 小区管理
            │   ├── deal-record   // 成交记录
            │   ├── ershoufang    // 在售房源
            │   └── opportunity   // 商机管理
            ├── login      // 登录页面
            ├── profile    // 个人资料页面
            ├── system     // 系统管理页面
            └── workbench  // 工作台页面
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

3. 添加成交记录：
   - 选择所属小区
   - 填写成交信息
   - 支持批量导入

4. 添加商机：
   - 选择所属小区
   - 填写房源基本信息
   - 上传户型图/室内图
   - 分配商机所有权
   - 添加评估意见

## 许可证

[MIT License](LICENSE)
