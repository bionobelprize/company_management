"""Purchase order models for biotech inventory system."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PurchaseOrderStatus(str, Enum):
    """采购订单状态"""
    DRAFT = "草稿"
    PENDING = "待审核"
    APPROVED = "已审核"
    ORDERED = "已下单"
    PARTIAL_RECEIVED = "部分入库"
    COMPLETED = "已完成"
    CANCELLED = "已取消"


class PurchaseOrderItem(BaseModel):
    """采购订单明细"""
    product_id: str = Field(..., description="产品ID")
    product_name: Optional[str] = Field(None, description="产品名称")
    quantity: int = Field(..., description="数量")
    unit_price: float = Field(..., description="单价")
    received_quantity: int = Field(default=0, description="已入库数量")
    remark: Optional[str] = Field(None, description="备注")


class PurchaseOrderBase(BaseModel):
    """采购订单基础模型"""
    order_number: str = Field(..., description="订单编号")
    supplier_id: str = Field(..., description="供应商ID")
    supplier_name: Optional[str] = Field(None, description="供应商名称")
    items: List[PurchaseOrderItem] = Field(default=[], description="订单明细")
    total_amount: float = Field(default=0.0, description="总金额")
    status: PurchaseOrderStatus = Field(default=PurchaseOrderStatus.DRAFT, description="订单状态")
    order_date: Optional[datetime] = Field(None, description="下单日期")
    expected_date: Optional[datetime] = Field(None, description="预计到货日期")
    remark: Optional[str] = Field(None, description="备注")


class PurchaseOrderCreate(BaseModel):
    """创建采购订单请求"""
    supplier_id: str
    items: List[PurchaseOrderItem]
    expected_date: Optional[datetime] = None
    remark: Optional[str] = None


class PurchaseOrderUpdate(BaseModel):
    """更新采购订单请求"""
    supplier_id: Optional[str] = None
    items: Optional[List[PurchaseOrderItem]] = None
    status: Optional[PurchaseOrderStatus] = None
    expected_date: Optional[datetime] = None
    remark: Optional[str] = None


class PurchaseOrderInDB(PurchaseOrderBase):
    """数据库中的采购订单模型"""
    id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = Field(None, description="创建人")

    class Config:
        populate_by_name = True


class PurchaseOrderResponse(PurchaseOrderBase):
    """采购订单响应模型"""
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
