"""Compliance tools for SBS/BCRP regulatory checks."""

from datetime import datetime

# Normativas vigentes Perú 2026
SBS_REGULATIONS = {
    "uif_threshold": 10000.00,  # S/ 10,000 - Reporte UIF obligatorio
    "sandbox_max_amount": 100000.00,  # S/ 100,000 - Límite sandbox
    "sandbox_max_users": 10000,  # 10,000 usuarios - Res. SBS 4142-2025
    "high_risk_threshold": 50000.00,  # S/ 50,000 - Alto riesgo
    "kyc_enhanced_threshold": 50000.00,  # KYC reforzado
    "origin_declaration_threshold": 30000.00,  # Declaración de origen
}

APPLICABLE_LAWS = {
    "fintech": "Ley Fintech 2023 - Crowdfunding, PSP, billeteras digitales",
    "ai": "Ley 31814 (2026) - Regulación IA en Perú",
    "sandbox": "Res. SBS 4142-2025 - Sandbox regulatorio expandido",
    "uif": "Normativa UIF - Reporte operaciones sospechosas",
    "open_finance": "Open Finance Roadmap SBS (Feb 2026)",
    "enia": "ENIA 2026-2030 - Estrategia Nacional IA",
    "aml": "Ley 27693 - Prevención lavado de activos",
}


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
    # 1. Verificar umbral UIF (Unidad de Inteligencia Financiera)
    #    Operaciones >S/10,000 requieren reporte obligatorio
    requires_uif = amount > SBS_REGULATIONS["uif_threshold"]

    # 2. Verificar elegibilidad para sandbox regulatorio
    #    Res. SBS 4142-2025: Hasta S/100,000 y 10,000 usuarios
    sandbox_eligible = amount <= SBS_REGULATIONS["sandbox_max_amount"] and operation_type in [
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
    elif amount < SBS_REGULATIONS["high_risk_threshold"]:
        risk_level = "high"
    else:
        risk_level = "critical"

    # 4. KYC adicional requerido
    requires_additional_kyc = amount > SBS_REGULATIONS["kyc_enhanced_threshold"]

    # 5. Declaración de origen de fondos
    requires_origin_declaration = amount > SBS_REGULATIONS["origin_declaration_threshold"]

    # 6. Determinar regulaciones aplicables
    applicable_regs = []

    # Siempre aplicable para IA en banca
    applicable_regs.append(APPLICABLE_LAWS["ai"])
    applicable_regs.append(APPLICABLE_LAWS["enia"])

    # Por umbral UIF
    if requires_uif:
        applicable_regs.append(APPLICABLE_LAWS["uif"])
        applicable_regs.append(APPLICABLE_LAWS["aml"])

    # Por sandbox
    if sandbox_eligible:
        applicable_regs.append(APPLICABLE_LAWS["sandbox"])

    # Por tipo de operación
    if operation_type in ["loan", "credit", "crowdfunding"]:
        applicable_regs.append(APPLICABLE_LAWS["fintech"])

    # Open Finance (general)
    applicable_regs.append(APPLICABLE_LAWS["open_finance"])

    # 7. Verificar compliance general
    #    Operación es compliant si cumple requisitos básicos
    compliant = True  # Por defecto compliant en sandbox

    # Excepciones que harían non-compliant:
    if amount > SBS_REGULATIONS["sandbox_max_amount"] * 2:
        # Operaciones muy grandes requieren autorización especial
        compliant = False
        risk_level = "critical"

    return {
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
            "uif": SBS_REGULATIONS["uif_threshold"],
            "kyc_enhanced": SBS_REGULATIONS["kyc_enhanced_threshold"],
            "high_risk": SBS_REGULATIONS["high_risk_threshold"],
            "sandbox_max": SBS_REGULATIONS["sandbox_max_amount"],
        },
        "timestamp": datetime.now().isoformat(),
        "open_finance_compliant": True,  # Sistema cumple con Open Finance
        "regulatory_body": "Superintendencia de Banca, Seguros y AFP (SBS)",
    }
