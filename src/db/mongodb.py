"""MongoDB connection and database operations."""

import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure

from src.config.settings import settings

logger = logging.getLogger(__name__)

# Global client instance
_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def connect_to_mongodb() -> AsyncIOMotorDatabase:
    """
    Connect to MongoDB and return database instance.

    Returns:
        AsyncIOMotorDatabase instance
    """
    global _client, _database

    if _database is not None:
        return _database

    try:
        logger.info("Connecting to MongoDB...")
        _client = AsyncIOMotorClient(settings.MONGODB_URI)

        # Verify connection
        await _client.admin.command("ping")

        _database = _client[settings.MONGODB_DB_NAME]
        logger.info(f"Successfully connected to MongoDB database: {settings.MONGODB_DB_NAME}")

        return _database

    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongodb_connection() -> None:
    """Close MongoDB connection."""
    global _client, _database

    if _client is not None:
        logger.info("Closing MongoDB connection...")
        _client.close()
        _client = None
        _database = None
        logger.info("MongoDB connection closed")


async def get_database() -> AsyncIOMotorDatabase:
    """
    Get current database instance or create new connection.

    Returns:
        AsyncIOMotorDatabase instance
    """
    if _database is None:
        return await connect_to_mongodb()
    return _database


# Collection names
class Collections:
    """MongoDB collection names."""

    CUSTOMERS = "customers"
    TRANSACTIONS = "transactions"
    CONVERSATIONS = "conversations"
    COMPLIANCE_CHECKS = "compliance_checks"
    FRAUD_CHECKS = "fraud_checks"
    SYSTEM_CONFIG = "system_config"
    CREDIT_CALCULATIONS = "credit_calculations"


async def get_config(config_type: str) -> dict[str, Any] | None:
    """
    Get system configuration from database.

    Args:
        config_type: Type of configuration (sbs_regulations, fraud_config, etc.)

    Returns:
        Configuration data dict or None if not found
    """
    db = await get_database()
    config = await db[Collections.SYSTEM_CONFIG].find_one(
        {"config_type": config_type, "active": True}, sort=[("version", -1)]
    )

    if config:
        return config["config_data"]
    return None


async def get_customer(customer_id: str) -> dict[str, Any] | None:
    """
    Get customer by ID.

    Args:
        customer_id: Customer ID

    Returns:
        Customer data dict or None if not found
    """
    db = await get_database()
    customer = await db[Collections.CUSTOMERS].find_one({"customer_id": customer_id})
    return customer


async def get_customer_transactions(customer_id: str, limit: int = 5) -> list[dict[str, Any]]:
    """
    Get recent transactions for customer.

    Args:
        customer_id: Customer ID
        limit: Maximum number of transactions to return

    Returns:
        List of transaction dicts
    """
    db = await get_database()
    cursor = (
        db[Collections.TRANSACTIONS]
        .find({"customer_id": customer_id})
        .sort("date", -1)
        .limit(limit)
    )
    transactions = await cursor.to_list(length=limit)
    return transactions


async def create_customer(customer_data: dict[str, Any]) -> str:
    """
    Create new customer.

    Args:
        customer_data: Customer data dict

    Returns:
        Customer ID
    """
    db = await get_database()
    await db[Collections.CUSTOMERS].insert_one(customer_data)
    return customer_data["customer_id"]


async def update_customer(customer_id: str, update_data: dict[str, Any]) -> bool:
    """
    Update customer data.

    Args:
        customer_id: Customer ID
        update_data: Data to update

    Returns:
        True if updated, False if not found
    """
    db = await get_database()
    update_data["updated_at"] = update_data.get("updated_at", None)
    result = await db[Collections.CUSTOMERS].update_one(
        {"customer_id": customer_id}, {"$set": update_data}
    )
    return result.modified_count > 0


async def create_transaction(transaction_data: dict[str, Any]) -> str:
    """
    Create new transaction.

    Args:
        transaction_data: Transaction data dict

    Returns:
        Transaction ID
    """
    db = await get_database()
    await db[Collections.TRANSACTIONS].insert_one(transaction_data)
    return transaction_data["transaction_id"]


async def save_compliance_check(check_data: dict[str, Any]) -> str:
    """
    Save compliance check result.

    Args:
        check_data: Compliance check data

    Returns:
        Check ID
    """
    db = await get_database()
    await db[Collections.COMPLIANCE_CHECKS].insert_one(check_data)
    return check_data["check_id"]


async def save_fraud_check(fraud_data: dict[str, Any]) -> str:
    """
    Save fraud check result.

    Args:
        fraud_data: Fraud check data

    Returns:
        Fraud check ID
    """
    db = await get_database()
    await db[Collections.FRAUD_CHECKS].insert_one(fraud_data)
    return fraud_data["fraud_check_id"]


async def save_credit_calculation(calc_data: dict[str, Any]) -> str:
    """
    Save credit capacity calculation.

    Args:
        calc_data: Calculation data

    Returns:
        Calculation ID
    """
    db = await get_database()
    await db[Collections.CREDIT_CALCULATIONS].insert_one(calc_data)
    return calc_data["calculation_id"]


async def save_conversation(conversation_data: dict[str, Any]) -> str:
    """
    Save or update conversation.

    Args:
        conversation_data: Conversation data

    Returns:
        Conversation ID
    """
    db = await get_database()
    await db[Collections.CONVERSATIONS].update_one(
        {"conversation_id": conversation_data["conversation_id"]},
        {"$set": conversation_data},
        upsert=True,
    )
    return conversation_data["conversation_id"]


async def get_conversation(conversation_id: str) -> dict[str, Any] | None:
    """
    Get conversation by ID.

    Args:
        conversation_id: Conversation ID

    Returns:
        Conversation data or None
    """
    db = await get_database()
    conversation = await db[Collections.CONVERSATIONS].find_one(
        {"conversation_id": conversation_id}
    )
    return conversation
