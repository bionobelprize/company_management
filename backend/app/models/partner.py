"""Partner models (Suppliers and Customers) for biotech inventory system."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PartnerType(str, Enum):
    """合作伙伴类型"""
    SUPPLIER = "供应商"
    CUSTOMER = "客户"
    BOTH = "供应商/客户"


class PartnerBase(BaseModel):
    """合作伙伴基础模型"""
    name: str = Field(..., description="名称")
    partner_code: str = Field(..., description="编号")
    partner_type: PartnerType = Field(..., description="类型")
    contact_person: Optional[str] = Field(None, description="联系人")
    phone: Optional[str] = Field(None, description="电话")
    email: Optional[str] = Field(None, description="邮箱")
    address: Optional[str] = Field(None, description="地址")
    bank_account: Optional[str] = Field(None, description="银行账户")
    tax_number: Optional[str] = Field(None, description="税号")
    remark: Optional[str] = Field(None, description="备注")
    is_active: bool = Field(default=True, description="是否启用")


class PartnerCreate(PartnerBase):
    """创建合作伙伴请求"""
    pass


class PartnerUpdate(BaseModel):
    """更新合作伙伴请求"""
    name: Optional[str] = None
    partner_type: Optional[PartnerType] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    bank_account: Optional[str] = None
    tax_number: Optional[str] = None
    remark: Optional[str] = None
    is_active: Optional[bool] = None


class PartnerInDB(PartnerBase):
    """数据库中的合作伙伴模型"""
    id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True


class PartnerResponse(PartnerBase):
    """合作伙伴响应模型"""
    id: str
    created_at: datetime
    updated_at: datetime
