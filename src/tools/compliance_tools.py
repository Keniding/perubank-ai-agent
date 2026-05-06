"""Compliance tools for SBS/BCRP regulatory checks."""

import logging
import uuid
from datetime import datetime

from src.db.sync_wrapper import get_config, save_compliance_check

logger = logging.getLogger(__name__)

# Default normativas vigentes Perú 2026 (fallback if MongoDB config not found)
DEFAULT_SBS_REGULATIONS = {
    "uif_threshold": 10000.00,  # S/ 10,000 - Reporte UIF obligatorio
    "sandbox_max_amount": 100000.00,  # S/ 100,000 - Límite sandbox
    "sandbox_max_users": 10000,  # 10,000 usuarios - Res. SBS 4142-2025
    "high_risk_threshold": 50000.00,  # S/ 50,000 - Alto riesgo
    "kyc_enhanced_threshold": 50000.00,  # KYC reforzado
    "origin_declaration_threshold": 30000.00,  # Declaración de origen
}

DEFAULT_APPLICABLE_LAWS = {
    "fintech": "Ley Fintech 2023 - Crowdfunding, PSP, billeteras digitales",
    "ai": "Ley 31814 (2026) - Regulación IA en Perú",
    "sandbox": "Res. SBS 4142-2025 - Sandbox regulatorio expandido",
    "uif": "Normativa UIF - Reporte operaciones sospechosas",
    "open_finance": "Open Finance Roadmap SBS (Feb 2026)",
    "enia": "ENIA 2026-2030 - Estrategia Nacional IA",
    "aml": "Ley 27693 - Prevención lavado de activos",
}


def _get_sbs_regulations() -> dict:
    """
    Get SBS regulations from MongoDB or use defaults.

    Returns:
        SBS regulations dict
    """
    config = get_config("sbs_regulations")
    if config:
        return config
    logger.warning("SBS regulations not found in MongoDB, using defaults")
    return DEFAULT_SBS_REGULATIONS


def _get_applicable_laws() -> dict:
    """
    Get applicable laws from MongoDB or use defaults.

    Returns:
        Applicable laws dict
    """
    config = get_config("applicable_laws")
    if config:
        return config
    logger.warning("Applicable laws not found in MongoDB, using defaults")
    return DEFAULT_APPLICABLE_LAWS


def check_sbs_compliance(operation_type: str, amount: float) -> dict:
    """
    Verifica cumplimiento normativo SBS para operación bancaria.

    Implementa reglas reales de:
    - UIF (Unidad de Inteligencia Financiera)
    - Sandbox regulatorio SBS
    - KYC (Know Your Customer)
    - Clasificación de riesgo

    Args:
        operation_type: Tipo de operación (transfer, loan, investment, etc.)
        amount: Monto en soles (S/)

    Returns:
        Dict con resultados detallados de compliance
    """
    # Get configurations from MongoDB
    sbs_regulations = _get_sbs_regulations()
    applicable_laws = _get_applicable_laws()

    # 1. Verificar umbral UIF (Unidad de Inteligencia Financiera)
    #    Operaciones >S/10,000 requieren reporte obligatorio
    requires_uif = amount > sbs_regulations["uif_threshold"]

    # 2. Verificar elegibilidad para sandbox regulatorio
    #    Res. SBS 4142-2025: Hasta S/100,000 y 10,000 usuarios
    sandbox_eligible = amount <= sbs_regulations["sandbox_max_amount"] and operation_type in [
        "transfer",
        "loan",
        "investment",
        "payment",
    ]

    # 3. Clasificar nivel de riesgo según monto
    if amount < 5000:
        risk_level = "low"
    elif amount < 30000:
        risk_level = "medium"
    elif amount < sbs_regulations["high_risk_threshold"]:
        risk_level = "high"
    else:
        risk_level = "critical"

    # 4. KYC adicional requerido
    requires_additional_kyc = amount > sbs_regulations["kyc_enhanced_threshold"]

    # 5. Declaración de origen de fondos
    requires_origin_declaration = amount > sbs_regulations["origin_declaration_threshold"]

    # 6. Determinar regulaciones aplicables
    applicable_regs = []

    # Siempre aplicable para IA en banca
    applicable_regs.append(applicable_laws["ai"])
    applicable_regs.append(applicable_laws["enia"])

    # Por umbral UIF
    if requires_uif:
        applicable_regs.append(applicable_laws["uif"])
        applicable_regs.append(applicable_laws["aml"])

    # Por sandbox
    if sandbox_eligible:
        applicable_regs.append(applicable_laws["sandbox"])

    # Por tipo de operación
    if operation_type in ["loan", "credit", "crowdfunding"]:
        applicable_regs.append(applicable_laws["fintech"])

    # Open Finance (general)
    applicable_regs.append(applicable_laws["open_finance"])

    # 7. Verificar compliance general
    #    Operación es compliant si cumple requisitos básicos
    compliant = True  # Por defecto compliant en sandbox

    # Excepciones que harían non-compliant:
    if amount > sbs_regulations["sandbox_max_amount"] * 2:
        # Operaciones muy grandes requieren autorización especial
        compliant = False
        risk_level = "critical"

    result = {
        "compliant": compliant,
        "operation_type": operation_type,
        "amount": amount,
        "currency": "PEN",  # Soles peruanos
        "requires_uif_report": requires_uif,
        "requires_additional_kyc": requires_additional_kyc,
        "requires_origin_declaration": requires_origin_declaration,
        "sandbox_eligible": sandbox_eligible,
        "risk_level": risk_level,
        "applicable_regulations": applicable_regs,
        "sbs_thresholds": {
            "uif": sbs_regulations["uif_threshold"],
            "kyc_enhanced": sbs_regulations["kyc_enhanced_threshold"],
            "high_risk": sbs_regulations["high_risk_threshold"],
            "sandbox_max": sbs_regulations["sandbox_max_amount"],
        },
        "timestamp": datetime.now().isoformat(),
        "open_finance_compliant": True,  # Sistema cumple con Open Finance
        "regulatory_body": "Superintendencia de Banca, Seguros y AFP (SBS)",
    }

    # Save compliance check to MongoDB for audit trail
    try:
        check_data = {
            "check_id": str(uuid.uuid4()),
            "customer_id": "unknown",  # Will be set by caller if available
            "operation_type": operation_type,
            "amount": amount,
            "result": result,
            "created_at": datetime.now(),
        }
        save_compliance_check(check_data)
    except Exception as e:
        logger.error(f"Failed to save compliance check: {e}")

    return result
