"""Inventory models for biotech inventory system."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class InventoryOperationType(str, Enum):
    """库存操作类型"""
    IN = "入库"
    OUT = "出库"
    ADJUST = "调整"
    RETURN = "退货"


class InventoryBase(BaseModel):
    """库存基础模型"""
    product_id: str = Field(..., description="产品ID")
    warehouse: str = Field(default="主仓库", description="仓库")
    batch_number: Optional[str] = Field(None, description="批次号")
    quantity: int = Field(default=0, description="数量")
    unit_price: float = Field(default=0.0, description="单价")
    location: Optional[str] = Field(None, description="货位")


class InventoryCreate(InventoryBase):
    """创建库存记录请求"""
    pass


class InventoryUpdate(BaseModel):
    """更新库存记录请求"""
    warehouse: Optional[str] = None
    batch_number: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    location: Optional[str] = None


class InventoryInDB(InventoryBase):
    """数据库中的库存模型"""
    id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True


class InventoryResponse(InventoryBase):
    """库存响应模型"""
    id: str
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class InventoryRecordBase(BaseModel):
    """库存流水记录基础模型"""
    product_id: str = Field(..., description="产品ID")
    inventory_id: str = Field(..., description="库存ID")
    operation_type: InventoryOperationType = Field(..., description="操作类型")
    quantity: int = Field(..., description="操作数量")
    batch_number: Optional[str] = Field(None, description="批次号")
    related_order_id: Optional[str] = Field(None, description="关联订单ID")
    operator: Optional[str] = Field(None, description="操作人")
    remark: Optional[str] = Field(None, description="备注")


class InventoryRecordCreate(InventoryRecordBase):
    """创建库存流水记录请求"""
    pass


class InventoryRecordInDB(InventoryRecordBase):
    """数据库中的库存流水记录模型"""
    id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True


class InventoryRecordResponse(InventoryRecordBase):
    """库存流水记录响应模型"""
    id: str
    product_name: Optional[str] = None
    created_at: datetime
