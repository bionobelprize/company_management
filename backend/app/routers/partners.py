"""Partner (Supplier/Customer) management API routes."""
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from ..database import get_database
from ..models.partner import (
    PartnerCreate,
    PartnerUpdate,
    PartnerResponse,
    PartnerType
)

router = APIRouter(prefix="/partners", tags=["合作伙伴管理"])


def partner_helper(partner) -> dict:
    """Convert MongoDB document to response format."""
    return {
        "id": str(partner["_id"]),
        "name": partner.get("name"),
        "partner_code": partner.get("partner_code"),
        "partner_type": partner.get("partner_type"),
        "contact_person": partner.get("contact_person"),
        "phone": partner.get("phone"),
        "email": partner.get("email"),
        "address": partner.get("address"),
        "bank_account": partner.get("bank_account"),
        "tax_number": partner.get("tax_number"),
        "remark": partner.get("remark"),
        "is_active": partner.get("is_active", True),
        "created_at": partner.get("created_at"),
        "updated_at": partner.get("updated_at"),
    }


@router.get("/", response_model=List[PartnerResponse])
async def get_partners(
    partner_type: Optional[PartnerType] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """获取合作伙伴列表"""
    db = get_database()
    query = {}
    
    if partner_type:
        query["partner_type"] = partner_type.value
    if is_active is not None:
        query["is_active"] = is_active
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"partner_code": {"$regex": search, "$options": "i"}},
        ]
    
    partners = []
    cursor = db.partners.find(query).skip(skip).limit(limit)
    async for partner in cursor:
        partners.append(partner_helper(partner))
    return partners


@router.get("/suppliers", response_model=List[PartnerResponse])
async def get_suppliers(
    is_active: Optional[bool] = True,
    skip: int = 0,
    limit: int = 100
):
    """获取供应商列表"""
    db = get_database()
    query = {
        "$or": [
            {"partner_type": PartnerType.SUPPLIER.value},
            {"partner_type": PartnerType.BOTH.value}
        ]
    }
    
    if is_active is not None:
        query["is_active"] = is_active
    
    suppliers = []
    cursor = db.partners.find(query).skip(skip).limit(limit)
    async for supplier in cursor:
        suppliers.append(partner_helper(supplier))
    return suppliers


@router.get("/customers", response_model=List[PartnerResponse])
async def get_customers(
    is_active: Optional[bool] = True,
    skip: int = 0,
    limit: int = 100
):
    """获取客户列表"""
    db = get_database()
    query = {
        "$or": [
            {"partner_type": PartnerType.CUSTOMER.value},
            {"partner_type": PartnerType.BOTH.value}
        ]
    }
    
    if is_active is not None:
        query["is_active"] = is_active
    
    customers = []
    cursor = db.partners.find(query).skip(skip).limit(limit)
    async for customer in cursor:
        customers.append(partner_helper(customer))
    return customers


@router.get("/{partner_id}", response_model=PartnerResponse)
async def get_partner(partner_id: str):
    """获取合作伙伴详情"""
    db = get_database()
    
    if not ObjectId.is_valid(partner_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的合作伙伴ID"
        )
    
    partner = await db.partners.find_one({"_id": ObjectId(partner_id)})
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="合作伙伴不存在"
        )
    return partner_helper(partner)


@router.post("/", response_model=PartnerResponse, status_code=status.HTTP_201_CREATED)
async def create_partner(partner: PartnerCreate):
    """创建合作伙伴"""
    db = get_database()
    
    # Check if partner code already exists
    existing = await db.partners.find_one({"partner_code": partner.partner_code})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="合作伙伴编号已存在"
        )
    
    now = datetime.now()
    partner_dict = partner.model_dump()
    partner_dict["partner_type"] = partner.partner_type.value
    partner_dict["created_at"] = now
    partner_dict["updated_at"] = now
    
    result = await db.partners.insert_one(partner_dict)
    created = await db.partners.find_one({"_id": result.inserted_id})
    return partner_helper(created)


@router.put("/{partner_id}", response_model=PartnerResponse)
async def update_partner(partner_id: str, partner: PartnerUpdate):
    """更新合作伙伴信息"""
    db = get_database()
    
    if not ObjectId.is_valid(partner_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的合作伙伴ID"
        )
    
    update_data = {k: v for k, v in partner.model_dump().items() if v is not None}
    if "partner_type" in update_data:
        update_data["partner_type"] = update_data["partner_type"].value
    update_data["updated_at"] = datetime.now()
    
    result = await db.partners.update_one(
        {"_id": ObjectId(partner_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="合作伙伴不存在"
        )
    
    updated = await db.partners.find_one({"_id": ObjectId(partner_id)})
    return partner_helper(updated)


@router.delete("/{partner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_partner(partner_id: str):
    """删除合作伙伴"""
    db = get_database()
    
    if not ObjectId.is_valid(partner_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的合作伙伴ID"
        )
    
    result = await db.partners.delete_one({"_id": ObjectId(partner_id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="合作伙伴不存在"
        )
