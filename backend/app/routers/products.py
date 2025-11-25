"""Product management API routes."""
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from ..database import get_database
from ..models.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductType
)

router = APIRouter(prefix="/products", tags=["产品管理"])


def product_helper(product) -> dict:
    """Convert MongoDB document to response format."""
    return {
        "id": str(product["_id"]),
        "name": product.get("name"),
        "product_code": product.get("product_code"),
        "product_type": product.get("product_type"),
        "specification": product.get("specification"),
        "unit": product.get("unit"),
        "description": product.get("description"),
        "storage_conditions": product.get("storage_conditions"),
        "shelf_life": product.get("shelf_life"),
        "category": product.get("category"),
        "created_at": product.get("created_at"),
        "updated_at": product.get("updated_at"),
    }


@router.get("/", response_model=List[ProductResponse])
async def get_products(
    product_type: Optional[ProductType] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """获取产品列表"""
    db = get_database()
    query = {}
    
    if product_type:
        query["product_type"] = product_type.value
    if category:
        query["category"] = category
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"product_code": {"$regex": search, "$options": "i"}},
        ]
    
    products = []
    cursor = db.products.find(query).skip(skip).limit(limit)
    async for product in cursor:
        products.append(product_helper(product))
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """获取单个产品详情"""
    db = get_database()
    
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的产品ID"
        )
    
    product = await db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    return product_helper(product)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate):
    """创建新产品"""
    db = get_database()
    
    # Check if product code already exists
    existing = await db.products.find_one({"product_code": product.product_code})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="产品编号已存在"
        )
    
    now = datetime.now()
    product_dict = product.model_dump()
    product_dict["product_type"] = product.product_type.value
    product_dict["created_at"] = now
    product_dict["updated_at"] = now
    
    result = await db.products.insert_one(product_dict)
    created = await db.products.find_one({"_id": result.inserted_id})
    return product_helper(created)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, product: ProductUpdate):
    """更新产品信息"""
    db = get_database()
    
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的产品ID"
        )
    
    update_data = {k: v for k, v in product.model_dump().items() if v is not None}
    if "product_type" in update_data:
        update_data["product_type"] = update_data["product_type"].value
    update_data["updated_at"] = datetime.now()
    
    result = await db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    
    updated = await db.products.find_one({"_id": ObjectId(product_id)})
    return product_helper(updated)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str):
    """删除产品"""
    db = get_database()
    
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的产品ID"
        )
    
    result = await db.products.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
