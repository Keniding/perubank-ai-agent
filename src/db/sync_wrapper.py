"""Synchronous wrappers for async MongoDB operations."""

import asyncio
import concurrent.futures
import logging
from typing import Any

from src.db import mongodb

logger = logging.getLogger(__name__)


def run_async(coro):
    """
    Run async coroutine in sync context safely.

    Strategy:
    - If there IS a running loop (e.g. inside FastAPI/pytest-asyncio): use a
      ThreadPoolExecutor so we don't block or nest event loops.
    - If there is NO running loop (e.g. CLI, sync agent call): use asyncio.run()
      which creates a fresh loop, runs the coroutine, and closes it cleanly.
    """
    try:
        asyncio.get_running_loop()
        # There is already a running loop — delegate to a worker thread
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        # No running loop — safe to call asyncio.run() directly
        return asyncio.run(coro)


def get_config(config_type: str) -> dict[str, Any] | None:
    """
    Get system configuration from database (sync wrapper).

    Args:
        config_type: Type of configuration (sbs_regulations, fraud_config, etc.)

    Returns:
        Configuration data dict or None if not found
    """
    try:
        return run_async(mongodb.get_config(config_type))
    except Exception as e:
        logger.error(f"Error getting config {config_type}: {e}")
        return None


def get_customer(customer_id: str) -> dict[str, Any] | None:
    """
    Get customer by ID (sync wrapper).

    Args:
        customer_id: Customer ID

    Returns:
        Customer data dict or None if not found
    """
    try:
        return run_async(mongodb.get_customer(customer_id))
    except Exception as e:
        logger.error(f"Error getting customer {customer_id}: {e}")
        return None


def get_customer_transactions(customer_id: str, limit: int = 5) -> list[dict[str, Any]]:
    """
    Get recent transactions for customer (sync wrapper).

    Args:
        customer_id: Customer ID
        limit: Maximum number of transactions to return

    Returns:
        List of transaction dicts
    """
    try:
        return run_async(mongodb.get_customer_transactions(customer_id, limit))
    except Exception as e:
        logger.error(f"Error getting transactions for {customer_id}: {e}")
        return []


def create_customer(customer_data: dict[str, Any]) -> str:
    """
    Create new customer (sync wrapper).

    Args:
        customer_data: Customer data dict

    Returns:
        Customer ID
    """
    try:
        return run_async(mongodb.create_customer(customer_data))
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        raise


def update_customer(customer_id: str, update_data: dict[str, Any]) -> bool:
    """
    Update customer data (sync wrapper).

    Args:
        customer_id: Customer ID
        update_data: Data to update

    Returns:
        True if updated, False if not found
    """
    try:
        return run_async(mongodb.update_customer(customer_id, update_data))
    except Exception as e:
        logger.error(f"Error updating customer {customer_id}: {e}")
        return False


def save_compliance_check(check_data: dict[str, Any]) -> str:
    """
    Save compliance check result (sync wrapper).

    Args:
        check_data: Compliance check data

    Returns:
        Check ID
    """
    try:
        return run_async(mongodb.save_compliance_check(check_data))
    except Exception as e:
        logger.error(f"Error saving compliance check: {e}")
        raise


def save_fraud_check(fraud_data: dict[str, Any]) -> str:
    """
    Save fraud check result (sync wrapper).

    Args:
        fraud_data: Fraud check data

    Returns:
        Fraud check ID
    """
    try:
        return run_async(mongodb.save_fraud_check(fraud_data))
    except Exception as e:
        logger.error(f"Error saving fraud check: {e}")
        raise


def save_credit_calculation(calc_data: dict[str, Any]) -> str:
    """
    Save credit capacity calculation (sync wrapper).

    Args:
        calc_data: Calculation data

    Returns:
        Calculation ID
    """
    try:
        return run_async(mongodb.save_credit_calculation(calc_data))
    except Exception as e:
        logger.error(f"Error saving credit calculation: {e}")
        raise


def save_conversation(conversation_data: dict[str, Any]) -> str:
    """
    Save or update conversation (sync wrapper).

    Args:
        conversation_data: Conversation data

    Returns:
        Conversation ID
    """
    try:
        return run_async(mongodb.save_conversation(conversation_data))
    except Exception as e:
        logger.error(f"Error saving conversation: {e}")
        raise


def get_conversation(conversation_id: str) -> dict[str, Any] | None:
    """
    Get conversation by ID (sync wrapper).

    Args:
        conversation_id: Conversation ID

    Returns:
        Conversation data or None
    """
    try:
        return run_async(mongodb.get_conversation(conversation_id))
    except Exception as e:
        logger.error(f"Error getting conversation {conversation_id}: {e}")
        return None
