"""Sales order management API routes."""
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import uuid

from ..database import get_database
from ..models.sales import (
    SalesOrderCreate,
    SalesOrderUpdate,
    SalesOrderResponse,
    SalesOrderStatus
)

router = APIRouter(prefix="/sales", tags=["销售管理"])


def generate_order_number():
    """Generate unique order number."""
    return f"SO{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:4].upper()}"


def order_helper(order) -> dict:
    """Convert MongoDB document to response format."""
    return {
        "id": str(order["_id"]),
        "order_number": order.get("order_number"),
        "customer_id": order.get("customer_id"),
        "customer_name": order.get("customer_name"),
        "items": order.get("items", []),
        "total_amount": order.get("total_amount"),
        "status": order.get("status"),
        "order_date": order.get("order_date"),
        "expected_date": order.get("expected_date"),
        "shipping_address": order.get("shipping_address"),
        "remark": order.get("remark"),
        "created_at": order.get("created_at"),
        "updated_at": order.get("updated_at"),
        "created_by": order.get("created_by"),
    }


@router.get("/", response_model=List[SalesOrderResponse])
async def get_sales_orders(
    status: Optional[SalesOrderStatus] = None,
    customer_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """获取销售订单列表"""
    db = get_database()
    query = {}
    
    if status:
        query["status"] = status.value
    if customer_id:
        query["customer_id"] = customer_id
    
    orders = []
    cursor = db.sales_orders.find(query).sort("created_at", -1).skip(skip).limit(limit)
    async for order in cursor:
        orders.append(order_helper(order))
    return orders


@router.get("/{order_id}", response_model=SalesOrderResponse)
async def get_sales_order(order_id: str):
    """获取销售订单详情"""
    db = get_database()
    
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的订单ID"
        )
    
    order = await db.sales_orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="销售订单不存在"
        )
    return order_helper(order)


@router.post("/", response_model=SalesOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_sales_order(order: SalesOrderCreate):
    """创建销售订单"""
    db = get_database()
    
    # Check if customer exists
    if not ObjectId.is_valid(order.customer_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的客户ID"
        )
    
    customer = await db.partners.find_one({"_id": ObjectId(order.customer_id)})
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="客户不存在"
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
        "customer_id": order.customer_id,
        "customer_name": customer.get("name"),
        "items": items_list,
        "total_amount": total_amount,
        "status": SalesOrderStatus.DRAFT.value,
        "order_date": now,
        "expected_date": order.expected_date,
        "shipping_address": order.shipping_address,
        "remark": order.remark,
        "created_at": now,
        "updated_at": now,
    }
    
    result = await db.sales_orders.insert_one(order_dict)
    created = await db.sales_orders.find_one({"_id": result.inserted_id})
    return order_helper(created)


@router.put("/{order_id}", response_model=SalesOrderResponse)
async def update_sales_order(order_id: str, order: SalesOrderUpdate):
    """更新销售订单"""
    db = get_database()
    
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的订单ID"
        )
    
    existing = await db.sales_orders.find_one({"_id": ObjectId(order_id)})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="销售订单不存在"
        )
    
    update_data = {k: v for k, v in order.model_dump().items() if v is not None}
    
    if "customer_id" in update_data:
        customer = await db.partners.find_one({"_id": ObjectId(update_data["customer_id"])})
        if customer:
            update_data["customer_name"] = customer.get("name")
    
    if "items" in update_data:
        total_amount = sum(item["quantity"] * item["unit_price"] for item in update_data["items"])
        update_data["total_amount"] = total_amount
    
    if "status" in update_data:
        update_data["status"] = update_data["status"].value
    
    update_data["updated_at"] = datetime.now()
    
    await db.sales_orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": update_data}
    )
    
    updated = await db.sales_orders.find_one({"_id": ObjectId(order_id)})
    return order_helper(updated)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sales_order(order_id: str):
    """删除销售订单"""
    db = get_database()
    
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的订单ID"
        )
    
    result = await db.sales_orders.delete_one({"_id": ObjectId(order_id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="销售订单不存在"
        )


@router.post("/{order_id}/approve", response_model=SalesOrderResponse)
async def approve_sales_order(order_id: str):
    """审核销售订单"""
    db = get_database()
    
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的订单ID"
        )
    
    order = await db.sales_orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="销售订单不存在"
        )
    
    if order.get("status") != SalesOrderStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有待审核状态的订单可以审核"
        )
    
    await db.sales_orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": SalesOrderStatus.APPROVED.value, "updated_at": datetime.now()}}
    )
    
    updated = await db.sales_orders.find_one({"_id": ObjectId(order_id)})
    return order_helper(updated)
