"""Seed script to populate MongoDB with initial data."""

import asyncio
import logging
from datetime import datetime

from src.db.mongodb import Collections, connect_to_mongodb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_configurations():
    """Seed system configurations."""
    db = await connect_to_mongodb()
    logger.info("Seeding system configurations...")

    # Banking configuration
    banking_config = {
        "config_id": "banking_config_v1",
        "config_type": "banking_config",
        "config_data": {
            "max_debt_ratio_sbs": 0.30,
            "tea_default": 0.18,
            "income_ranges": [3000, 4500, 5500, 8000, 10000, 12000, 15000],
            "credit_score_min": 550,
            "credit_score_max": 850,
            "balance_soles_min": 1000,
            "balance_soles_max": 50000,
            "balance_dolares_min": 500,
            "balance_dolares_max": 10000,
        },
        "version": "1.0",
        "active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    # SBS regulations
    sbs_regulations = {
        "config_id": "sbs_regulations_v1",
        "config_type": "sbs_regulations",
        "config_data": {
            "uif_threshold": 10000.00,
            "sandbox_max_amount": 100000.00,
            "sandbox_max_users": 10000,
            "high_risk_threshold": 50000.00,
            "kyc_enhanced_threshold": 50000.00,
            "origin_declaration_threshold": 30000.00,
        },
        "version": "1.0",
        "active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    # Applicable laws
    applicable_laws = {
        "config_id": "applicable_laws_v1",
        "config_type": "applicable_laws",
        "config_data": {
            "fintech": "Ley Fintech 2023 - Crowdfunding, PSP, billeteras digitales",
            "ai": "Ley 31814 (2026) - Regulación IA en Perú",
            "sandbox": "Res. SBS 4142-2025 - Sandbox regulatorio expandido",
            "uif": "Normativa UIF - Reporte operaciones sospechosas",
            "open_finance": "Open Finance Roadmap SBS (Feb 2026)",
            "enia": "ENIA 2026-2030 - Estrategia Nacional IA",
            "aml": "Ley 27693 - Prevención lavado de activos",
        },
        "version": "1.0",
        "active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    # Fraud detection configuration
    fraud_config = {
        "config_id": "fraud_config_v1",
        "config_type": "fraud_config",
        "config_data": {
            "max_transactions_per_hour": 10,
            "max_transaction_amount_normal": 15000.00,
            "suspicious_countries": ["VE", "NG", "PK", "RU"],
            "device_change_risk_increase": 0.2,
            "unusual_hour_start": 23,
            "unusual_hour_end": 6,
            "high_amount_multiplier": 2.0,
        },
        "version": "1.0",
        "active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    # Insert or update configurations
    configs = [banking_config, sbs_regulations, applicable_laws, fraud_config]

    for config in configs:
        await db[Collections.SYSTEM_CONFIG].update_one(
            {"config_id": config["config_id"]}, {"$set": config}, upsert=True
        )
        logger.info(f"  ✓ Seeded {config['config_type']}")

    logger.info("System configurations seeded successfully!")


async def seed_customers():
    """Seed sample customer data."""
    db = await connect_to_mongodb()
    logger.info("Seeding customer data...")

    customers = [
        {
            "customer_id": "CLI-2026-001",
            "name": "Juan Pérez García",
            "dni": "12345678",
            "monthly_income": 8500.00,
            "current_debt": 1200.00,
            "credit_score": 745,
            "account_soles": 15420.50,
            "account_dolares": 3200.00,
            "employment_type": "dependiente",
            "years_employed": 3,
            "sector": "servicios",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
        {
            "customer_id": "CLI-2026-002",
            "name": "María Rodriguez Lopez",
            "dni": "87654321",
            "monthly_income": 12000.00,
            "current_debt": 3500.00,
            "credit_score": 820,
            "account_soles": 32500.75,
            "account_dolares": 8500.00,
            "employment_type": "independiente",
            "years_employed": 5,
            "sector": "comercio",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
        {
            "customer_id": "CLI-2026-003",
            "name": "Carlos Gomez Sanchez",
            "dni": "45678912",
            "monthly_income": 5500.00,
            "current_debt": 1800.00,
            "credit_score": 680,
            "account_soles": 8200.30,
            "account_dolares": 1500.00,
            "employment_type": "dependiente",
            "years_employed": 2,
            "sector": "manufactura",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
        {
            "customer_id": "CLI-2026-DEMO",
            "name": "Cliente Demo Hackathon",
            "dni": "99999999",
            "monthly_income": 8500.00,
            "current_debt": 1200.00,
            "credit_score": 745,
            "account_soles": 15420.50,
            "account_dolares": 3200.00,
            "employment_type": "dependiente",
            "years_employed": 3,
            "sector": "tecnologia",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
    ]

    for customer in customers:
        await db[Collections.CUSTOMERS].update_one(
            {"customer_id": customer["customer_id"]}, {"$set": customer}, upsert=True
        )
        logger.info(f"  ✓ Seeded customer {customer['customer_id']}")

    logger.info("Customer data seeded successfully!")


async def seed_transactions():
    """Seed sample transaction data."""
    db = await connect_to_mongodb()
    logger.info("Seeding transaction data...")

    transactions = [
        {
            "transaction_id": "TXN-001",
            "customer_id": "CLI-2026-001",
            "amount": -250.00,
            "type": "pago",
            "description": "Luz del Sur",
            "date": datetime(2026, 5, 4),
            "location_country": "PE",
            "device_fingerprint": "known",
            "created_at": datetime.now(),
        },
        {
            "transaction_id": "TXN-002",
            "customer_id": "CLI-2026-001",
            "amount": 5000.00,
            "type": "deposito",
            "description": "Nómina",
            "date": datetime(2026, 5, 3),
            "location_country": "PE",
            "device_fingerprint": "known",
            "created_at": datetime.now(),
        },
        {
            "transaction_id": "TXN-003",
            "customer_id": "CLI-2026-001",
            "amount": -1200.00,
            "type": "transferencia",
            "description": "Alquiler",
            "date": datetime(2026, 5, 2),
            "location_country": "PE",
            "device_fingerprint": "known",
            "created_at": datetime.now(),
        },
        {
            "transaction_id": "TXN-004",
            "customer_id": "CLI-2026-001",
            "amount": -85.50,
            "type": "compra",
            "description": "Supermercado",
            "date": datetime(2026, 5, 1),
            "location_country": "PE",
            "device_fingerprint": "known",
            "created_at": datetime.now(),
        },
        {
            "transaction_id": "TXN-005",
            "customer_id": "CLI-2026-001",
            "amount": -120.00,
            "type": "pago",
            "description": "Teléfono",
            "date": datetime(2026, 4, 30),
            "location_country": "PE",
            "device_fingerprint": "known",
            "created_at": datetime.now(),
        },
        {
            "transaction_id": "TXN-006",
            "customer_id": "CLI-2026-002",
            "amount": 8000.00,
            "type": "deposito",
            "description": "Venta comercio",
            "date": datetime(2026, 5, 5),
            "location_country": "PE",
            "device_fingerprint": "known",
            "created_at": datetime.now(),
        },
        {
            "transaction_id": "TXN-007",
            "customer_id": "CLI-2026-002",
            "amount": -2500.00,
            "type": "pago",
            "description": "Proveedor",
            "date": datetime(2026, 5, 3),
            "location_country": "PE",
            "device_fingerprint": "known",
            "created_at": datetime.now(),
        },
        {
            "transaction_id": "TXN-008",
            "customer_id": "CLI-2026-002",
            "amount": -450.00,
            "type": "transferencia",
            "description": "Alquiler local",
            "date": datetime(2026, 5, 1),
            "location_country": "PE",
            "device_fingerprint": "known",
            "created_at": datetime.now(),
        },
        {
            "transaction_id": "TXN-009",
            "customer_id": "CLI-2026-002",
            "amount": 6500.00,
            "type": "deposito",
            "description": "Venta comercio",
            "date": datetime(2026, 4, 29),
            "location_country": "PE",
            "device_fingerprint": "known",
            "created_at": datetime.now(),
        },
    ]

    for txn in transactions:
        await db[Collections.TRANSACTIONS].update_one(
            {"transaction_id": txn["transaction_id"]}, {"$set": txn}, upsert=True
        )

    logger.info(f"  ✓ Seeded {len(transactions)} transactions")
    logger.info("Transaction data seeded successfully!")


async def seed_all():
    """Seed all data."""
    logger.info("=" * 60)
    logger.info("Starting MongoDB data seeding...")
    logger.info("=" * 60)

    await seed_configurations()
    await seed_customers()
    await seed_transactions()

    logger.info("=" * 60)
    logger.info("All data seeded successfully! 🎉")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed_all())
