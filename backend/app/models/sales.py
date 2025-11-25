"""Sales order models for biotech inventory system."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SalesOrderStatus(str, Enum):
    """销售订单状态"""
    DRAFT = "草稿"
    PENDING = "待审核"
    APPROVED = "已审核"
    PROCESSING = "处理中"
    PARTIAL_SHIPPED = "部分出库"
    SHIPPED = "已出库"
    COMPLETED = "已完成"
    CANCELLED = "已取消"


class SalesOrderItem(BaseModel):
    """销售订单明细"""
    product_id: str = Field(..., description="产品ID")
    product_name: Optional[str] = Field(None, description="产品名称")
    quantity: int = Field(..., description="数量")
    unit_price: float = Field(..., description="单价")
    shipped_quantity: int = Field(default=0, description="已出库数量")
    remark: Optional[str] = Field(None, description="备注")


class SalesOrderBase(BaseModel):
    """销售订单基础模型"""
    order_number: str = Field(..., description="订单编号")
    customer_id: str = Field(..., description="客户ID")
    customer_name: Optional[str] = Field(None, description="客户名称")
    items: List[SalesOrderItem] = Field(default=[], description="订单明细")
    total_amount: float = Field(default=0.0, description="总金额")
    status: SalesOrderStatus = Field(default=SalesOrderStatus.DRAFT, description="订单状态")
    order_date: Optional[datetime] = Field(None, description="下单日期")
    expected_date: Optional[datetime] = Field(None, description="预计发货日期")
    shipping_address: Optional[str] = Field(None, description="收货地址")
    remark: Optional[str] = Field(None, description="备注")


class SalesOrderCreate(BaseModel):
    """创建销售订单请求"""
    customer_id: str
    items: List[SalesOrderItem]
    expected_date: Optional[datetime] = None
    shipping_address: Optional[str] = None
    remark: Optional[str] = None


class SalesOrderUpdate(BaseModel):
    """更新销售订单请求"""
    customer_id: Optional[str] = None
    items: Optional[List[SalesOrderItem]] = None
    status: Optional[SalesOrderStatus] = None
    expected_date: Optional[datetime] = None
    shipping_address: Optional[str] = None
    remark: Optional[str] = None


class SalesOrderInDB(SalesOrderBase):
    """数据库中的销售订单模型"""
    id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = Field(None, description="创建人")

    class Config:
        populate_by_name = True


class SalesOrderResponse(SalesOrderBase):
    """销售订单响应模型"""
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
