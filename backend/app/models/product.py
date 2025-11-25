"""Product models for biotech inventory system."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ProductType(str, Enum):
    """产品类型枚举"""
    PROTEIN = "蛋白"
    ANTIGEN = "抗原"
    ANTIBODY = "抗体"
    SYNTHESIS_SERVICE = "合成服务"
    REAGENT = "试剂"
    OTHER = "其他"


class ProductBase(BaseModel):
    """产品基础模型"""
    name: str = Field(..., description="产品名称")
    product_code: str = Field(..., description="产品编号")
    product_type: ProductType = Field(..., description="产品类型")
    specification: Optional[str] = Field(None, description="规格")
    unit: str = Field(default="个", description="单位")
    description: Optional[str] = Field(None, description="产品描述")
    storage_conditions: Optional[str] = Field(None, description="储存条件")
    shelf_life: Optional[int] = Field(None, description="保质期(天)")
    category: Optional[str] = Field(None, description="产品分类")


class ProductCreate(ProductBase):
    """创建产品请求模型"""
    pass


class ProductUpdate(BaseModel):
    """更新产品请求模型"""
    name: Optional[str] = None
    product_type: Optional[ProductType] = None
    specification: Optional[str] = None
    unit: Optional[str] = None
    description: Optional[str] = None
    storage_conditions: Optional[str] = None
    shelf_life: Optional[int] = None
    category: Optional[str] = None


class ProductInDB(ProductBase):
    """数据库中的产品模型"""
    id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True


class ProductResponse(ProductBase):
    """产品响应模型"""
    id: str
    created_at: datetime
    updated_at: datetime
