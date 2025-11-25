# 生物公司进销存管理系统

本系统是为生物公司（蛋白抗原抗体及相关合成服务）设计的进销存管理软件。

## 技术架构

- **前端**: HTML + CSS + JavaScript (原生Web技术)
- **后端**: Python + FastAPI
- **数据库**: MongoDB

## 系统功能

### 核心模块

1. **产品管理** 🧪
   - 管理蛋白、抗原、抗体及合成服务等产品信息
   - 支持产品分类、规格、储存条件等属性

2. **库存管理** 📦
   - 多仓库库存管理
   - 入库、出库操作
   - 库存流水记录

3. **采购管理** 🛒
   - 采购订单创建与管理
   - 订单审核流程
   - 供应商关联

4. **销售管理** 💰
   - 销售订单创建与管理
   - 订单状态跟踪
   - 客户关联

5. **合作伙伴管理** 🤝
   - 供应商管理
   - 客户管理

## 目录结构

```
company_management/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── models/         # 数据模型
│   │   │   ├── product.py  # 产品模型
│   │   │   ├── inventory.py# 库存模型
│   │   │   ├── purchase.py # 采购模型
│   │   │   ├── sales.py    # 销售模型
│   │   │   └── partner.py  # 合作伙伴模型
│   │   ├── routers/        # API路由
│   │   │   ├── products.py
│   │   │   ├── inventory.py
│   │   │   ├── purchases.py
│   │   │   ├── sales.py
│   │   │   └── partners.py
│   │   ├── config.py       # 配置文件
│   │   ├── database.py     # 数据库连接
│   │   └── main.py         # 主程序入口
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端代码
│   ├── templates/
│   │   └── index.html     # 主页面
│   └── static/
│       ├── css/
│       │   └── style.css  # 样式文件
│       └── js/
│           └── app.js     # 前端逻辑
└── README.md
```

## 快速开始

### 环境要求

- Python 3.8+
- MongoDB 4.4+
- pip (Python包管理器)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd company_management
   ```

2. **安装后端依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **配置MongoDB连接**
   
   创建 `.env` 文件或设置环境变量：
   ```
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=biotech_inventory
   ```

4. **启动后端服务**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **访问系统**
   - 前端界面: http://localhost:8000
   - API文档: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc

## API 接口

### 产品管理
- `GET /api/products/` - 获取产品列表
- `POST /api/products/` - 创建产品
- `GET /api/products/{id}` - 获取产品详情
- `PUT /api/products/{id}` - 更新产品
- `DELETE /api/products/{id}` - 删除产品

### 库存管理
- `GET /api/inventory/` - 获取库存列表
- `POST /api/inventory/` - 创建库存记录
- `POST /api/inventory/in` - 入库操作
- `POST /api/inventory/out` - 出库操作
- `GET /api/inventory/records/` - 获取库存流水

### 采购管理
- `GET /api/purchases/` - 获取采购订单列表
- `POST /api/purchases/` - 创建采购订单
- `GET /api/purchases/{id}` - 获取订单详情
- `PUT /api/purchases/{id}` - 更新订单
- `DELETE /api/purchases/{id}` - 删除订单
- `POST /api/purchases/{id}/approve` - 审核订单

### 销售管理
- `GET /api/sales/` - 获取销售订单列表
- `POST /api/sales/` - 创建销售订单
- `GET /api/sales/{id}` - 获取订单详情
- `PUT /api/sales/{id}` - 更新订单
- `DELETE /api/sales/{id}` - 删除订单
- `POST /api/sales/{id}/approve` - 审核订单

### 合作伙伴管理
- `GET /api/partners/` - 获取合作伙伴列表
- `GET /api/partners/suppliers` - 获取供应商列表
- `GET /api/partners/customers` - 获取客户列表
- `POST /api/partners/` - 创建合作伙伴
- `PUT /api/partners/{id}` - 更新合作伙伴
- `DELETE /api/partners/{id}` - 删除合作伙伴

## 产品类型

- 蛋白 (Protein)
- 抗原 (Antigen)
- 抗体 (Antibody)
- 合成服务 (Synthesis Service)
- 试剂 (Reagent)
- 其他 (Other)

## 许可证

MIT License