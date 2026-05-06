"""Unit tests for banking tools."""

from src.tools.banking_tools import check_customer_balance, calculate_credit_capacity
from src.tools.compliance_tools import check_sbs_compliance
from src.tools.fraud_tools import detect_fraud_patterns


class TestBankingTools:
    def test_check_customer_balance(self):
        result = check_customer_balance("CLI-TEST")
        assert "balance_soles" in result
        assert "credit_score" in result
        assert result["credit_score"] > 0

    def test_calculate_credit_capacity_compliant(self):
        result = calculate_credit_capacity(monthly_income=10000, existing_debt=1000)
        assert result["compliant_sbs"] is True
        assert result["available_monthly_capacity"] > 0

    def test_calculate_credit_capacity_non_compliant(self):
        result = calculate_credit_capacity(monthly_income=5000, existing_debt=2000)
        assert result["debt_ratio_current"] > 0.30 or result["compliant_sbs"] is False


class TestComplianceTools:
    def test_low_amount_no_uif(self):
        result = check_sbs_compliance("transfer", 5000)
        assert result["requires_uif_report"] is False

    def test_high_amount_requires_uif(self):
        result = check_sbs_compliance("transfer", 15000)
        assert result["requires_uif_report"] is True

    def test_very_high_amount_requires_kyc(self):
        result = check_sbs_compliance("transfer", 60000)
        assert result["requires_additional_kyc"] is True


class TestFraudTools:
    def test_normal_transaction(self):
        result = detect_fraud_patterns("CLI-TEST", 1000)
        assert result["recommendation"] == "APPROVE"
        assert result["risk_score"] < 0.5
