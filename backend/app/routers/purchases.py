"""Purchase order management API routes."""
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import uuid

from ..database import get_database
from ..models.purchase import (
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    PurchaseOrderResponse,
    PurchaseOrderStatus
)

router = APIRouter(prefix="/purchases", tags=["采购管理"])


def generate_order_number():
    """Generate unique order number."""
    return f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:4].upper()}"


def order_helper(order) -> dict:
    """Convert MongoDB document to response format."""
    return {
        "id": str(order["_id"]),
        "order_number": order.get("order_number"),
        "supplier_id": order.get("supplier_id"),
        "supplier_name": order.get("supplier_name"),
        "items": order.get("items", []),
        "total_amount": order.get("total_amount"),
        "status": order.get("status"),
        "order_date": order.get("order_date"),
        "expected_date": order.get("expected_date"),
        "remark": order.get("remark"),
        "created_at": order.get("created_at"),
        "updated_at": order.get("updated_at"),
        "created_by": order.get("created_by"),
    }


@router.get("/", response_model=List[PurchaseOrderResponse])
async def get_purchase_orders(
    status: Optional[PurchaseOrderStatus] = None,
    supplier_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """获取采购订单列表"""
    db = get_database()
    query = {}
    
    if status:
        query["status"] = status.value
    if supplier_id:
        query["supplier_id"] = supplier_id
    
    orders = []
    cursor = db.purchase_orders.find(query).sort("created_at", -1).skip(skip).limit(limit)
    async for order in cursor:
        orders.append(order_helper(order))
    return orders


@router.get("/{order_id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(order_id: str):
    """获取采购订单详情"""
    db = get_database()
    
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的订单ID"
        )
    
    order = await db.purchase_orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="采购订单不存在"
        )
    return order_helper(order)


@router.post("/", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(order: PurchaseOrderCreate):
    """创建采购订单"""
    db = get_database()
    
    # Check if supplier exists
    if not ObjectId.is_valid(order.supplier_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的供应商ID"
        )
    
    supplier = await db.partners.find_one({"_id": ObjectId(order.supplier_id)})
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="供应商不存在"
        )
    
    # Calculate total amount
    total_amount = sum(item.quantity * item.unit_price for item in order.items)
    
    # Populate product names
    items_list = []
    for item in order.items:
        item_dict = item.model_dump()
        if ObjectId.is_valid(item.product_id):
            product = await db.products.find_one({"_id": ObjectId(item.product_id)})
            if product:
                item_dict["product_name"] = product.get("name")
        items_list.append(item_dict)
    
    now = datetime.now()
    order_dict = {
        "order_number": generate_order_number(),
        "supplier_id": order.supplier_id,
        "supplier_name": supplier.get("name"),
        "items": items_list,
        "total_amount": total_amount,
        "status": PurchaseOrderStatus.DRAFT.value,
        "order_date": now,
        "expected_date": order.expected_date,
        "remark": order.remark,
        "created_at": now,
        "updated_at": now,
    }
    
    result = await db.purchase_orders.insert_one(order_dict)
    created = await db.purchase_orders.find_one({"_id": result.inserted_id})
    return order_helper(created)


@router.put("/{order_id}", response_model=PurchaseOrderResponse)
async def update_purchase_order(order_id: str, order: PurchaseOrderUpdate):
    """更新采购订单"""
    db = get_database()
    
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的订单ID"
        )
    
    existing = await db.purchase_orders.find_one({"_id": ObjectId(order_id)})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="采购订单不存在"
        )
    
    update_data = {k: v for k, v in order.model_dump().items() if v is not None}
    
    if "supplier_id" in update_data:
        supplier = await db.partners.find_one({"_id": ObjectId(update_data["supplier_id"])})
        if supplier:
            update_data["supplier_name"] = supplier.get("name")
    
    if "items" in update_data:
        total_amount = sum(item["quantity"] * item["unit_price"] for item in update_data["items"])
        update_data["total_amount"] = total_amount
    
    if "status" in update_data:
        update_data["status"] = update_data["status"].value
    
    update_data["updated_at"] = datetime.now()
    
    await db.purchase_orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": update_data}
    )
    
    updated = await db.purchase_orders.find_one({"_id": ObjectId(order_id)})
    return order_helper(updated)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_purchase_order(order_id: str):
    """删除采购订单"""
    db = get_database()
    
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的订单ID"
        )
    
    result = await db.purchase_orders.delete_one({"_id": ObjectId(order_id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="采购订单不存在"
        )


@router.post("/{order_id}/approve", response_model=PurchaseOrderResponse)
async def approve_purchase_order(order_id: str):
    """审核采购订单"""
    db = get_database()
    
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的订单ID"
        )
    
    order = await db.purchase_orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="采购订单不存在"
        )
    
    if order.get("status") != PurchaseOrderStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有待审核状态的订单可以审核"
        )
    
    await db.purchase_orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": PurchaseOrderStatus.APPROVED.value, "updated_at": datetime.now()}}
    )
    
    updated = await db.purchase_orders.find_one({"_id": ObjectId(order_id)})
    return order_helper(updated)
