"""Inventory management API routes."""
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from ..database import get_database
from ..models.inventory import (
    InventoryCreate,
    InventoryUpdate,
    InventoryResponse,
    InventoryRecordCreate,
    InventoryRecordResponse,
    InventoryOperationType
)

router = APIRouter(prefix="/inventory", tags=["库存管理"])


def inventory_helper(inventory, product=None) -> dict:
    """Convert MongoDB document to response format."""
    return {
        "id": str(inventory["_id"]),
        "product_id": inventory.get("product_id"),
        "product_name": product.get("name") if product else None,
        "product_code": product.get("product_code") if product else None,
        "warehouse": inventory.get("warehouse"),
        "batch_number": inventory.get("batch_number"),
        "quantity": inventory.get("quantity"),
        "unit_price": inventory.get("unit_price"),
        "location": inventory.get("location"),
        "created_at": inventory.get("created_at"),
        "updated_at": inventory.get("updated_at"),
    }


def record_helper(record, product=None) -> dict:
    """Convert MongoDB document to response format."""
    return {
        "id": str(record["_id"]),
        "product_id": record.get("product_id"),
        "product_name": product.get("name") if product else None,
        "inventory_id": record.get("inventory_id"),
        "operation_type": record.get("operation_type"),
        "quantity": record.get("quantity"),
        "batch_number": record.get("batch_number"),
        "related_order_id": record.get("related_order_id"),
        "operator": record.get("operator"),
        "remark": record.get("remark"),
        "created_at": record.get("created_at"),
    }


@router.get("/", response_model=List[InventoryResponse])
async def get_inventory_list(
    product_id: Optional[str] = None,
    warehouse: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """获取库存列表"""
    db = get_database()
    query = {}
    
    if product_id:
        query["product_id"] = product_id
    if warehouse:
        query["warehouse"] = warehouse
    
    inventories = []
    cursor = db.inventory.find(query).skip(skip).limit(limit)
    async for inv in cursor:
        product = None
        if inv.get("product_id"):
            try:
                product = await db.products.find_one({"_id": ObjectId(inv["product_id"])})
            except Exception:
                pass
        inventories.append(inventory_helper(inv, product))
    return inventories


@router.get("/{inventory_id}", response_model=InventoryResponse)
async def get_inventory(inventory_id: str):
    """获取库存详情"""
    db = get_database()
    
    if not ObjectId.is_valid(inventory_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的库存ID"
        )
    
    inventory = await db.inventory.find_one({"_id": ObjectId(inventory_id)})
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="库存记录不存在"
        )
    
    product = None
    if inventory.get("product_id"):
        try:
            product = await db.products.find_one({"_id": ObjectId(inventory["product_id"])})
        except Exception:
            pass
    
    return inventory_helper(inventory, product)


@router.post("/", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory(inventory: InventoryCreate):
    """创建库存记录"""
    db = get_database()
    
    # Check if product exists
    if not ObjectId.is_valid(inventory.product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的产品ID"
        )
    
    product = await db.products.find_one({"_id": ObjectId(inventory.product_id)})
    if not product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="产品不存在"
        )
    
    now = datetime.now()
    inventory_dict = inventory.model_dump()
    inventory_dict["created_at"] = now
    inventory_dict["updated_at"] = now
    
    result = await db.inventory.insert_one(inventory_dict)
    created = await db.inventory.find_one({"_id": result.inserted_id})
    return inventory_helper(created, product)


@router.put("/{inventory_id}", response_model=InventoryResponse)
async def update_inventory(inventory_id: str, inventory: InventoryUpdate):
    """更新库存记录"""
    db = get_database()
    
    if not ObjectId.is_valid(inventory_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的库存ID"
        )
    
    update_data = {k: v for k, v in inventory.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now()
    
    result = await db.inventory.update_one(
        {"_id": ObjectId(inventory_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="库存记录不存在"
        )
    
    updated = await db.inventory.find_one({"_id": ObjectId(inventory_id)})
    product = None
    if updated.get("product_id"):
        try:
            product = await db.products.find_one({"_id": ObjectId(updated["product_id"])})
        except Exception:
            pass
    return inventory_helper(updated, product)


@router.post("/in", response_model=InventoryRecordResponse)
async def inventory_in(record: InventoryRecordCreate):
    """入库操作"""
    db = get_database()
    
    # Check if inventory exists
    if not ObjectId.is_valid(record.inventory_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的库存ID"
        )
    
    inventory = await db.inventory.find_one({"_id": ObjectId(record.inventory_id)})
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="库存记录不存在"
        )
    
    # Update inventory quantity
    new_quantity = inventory.get("quantity", 0) + record.quantity
    await db.inventory.update_one(
        {"_id": ObjectId(record.inventory_id)},
        {"$set": {"quantity": new_quantity, "updated_at": datetime.now()}}
    )
    
    # Create inventory record
    now = datetime.now()
    record_dict = record.model_dump()
    record_dict["operation_type"] = InventoryOperationType.IN.value
    record_dict["created_at"] = now
    
    result = await db.inventory_records.insert_one(record_dict)
    created = await db.inventory_records.find_one({"_id": result.inserted_id})
    
    product = None
    if record.product_id:
        try:
            product = await db.products.find_one({"_id": ObjectId(record.product_id)})
        except Exception:
            pass
    
    return record_helper(created, product)


@router.post("/out", response_model=InventoryRecordResponse)
async def inventory_out(record: InventoryRecordCreate):
    """出库操作"""
    db = get_database()
    
    # Check if inventory exists
    if not ObjectId.is_valid(record.inventory_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的库存ID"
        )
    
    inventory = await db.inventory.find_one({"_id": ObjectId(record.inventory_id)})
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="库存记录不存在"
        )
    
    # Check if there's enough quantity
    current_quantity = inventory.get("quantity", 0)
    if current_quantity < record.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"库存不足，当前库存: {current_quantity}"
        )
    
    # Update inventory quantity
    new_quantity = current_quantity - record.quantity
    await db.inventory.update_one(
        {"_id": ObjectId(record.inventory_id)},
        {"$set": {"quantity": new_quantity, "updated_at": datetime.now()}}
    )
    
    # Create inventory record
    now = datetime.now()
    record_dict = record.model_dump()
    record_dict["operation_type"] = InventoryOperationType.OUT.value
    record_dict["created_at"] = now
    
    result = await db.inventory_records.insert_one(record_dict)
    created = await db.inventory_records.find_one({"_id": result.inserted_id})
    
    product = None
    if record.product_id:
        try:
            product = await db.products.find_one({"_id": ObjectId(record.product_id)})
        except Exception:
            pass
    
    return record_helper(created, product)


@router.get("/records/", response_model=List[InventoryRecordResponse])
async def get_inventory_records(
    product_id: Optional[str] = None,
    operation_type: Optional[InventoryOperationType] = None,
    skip: int = 0,
    limit: int = 100
):
    """获取库存流水记录"""
    db = get_database()
    query = {}
    
    if product_id:
        query["product_id"] = product_id
    if operation_type:
        query["operation_type"] = operation_type.value
    
    records = []
    cursor = db.inventory_records.find(query).sort("created_at", -1).skip(skip).limit(limit)
    async for record in cursor:
        product = None
        if record.get("product_id"):
            try:
                product = await db.products.find_one({"_id": ObjectId(record["product_id"])})
            except Exception:
                pass
        records.append(record_helper(record, product))
    return records
