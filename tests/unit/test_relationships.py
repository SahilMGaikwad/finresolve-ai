"""
FinResolve AI — Relationship Integrity Tests

Verifies that all foreign key references are valid in clean datasets.
No orphaned records.
"""

import random

import pytest

from data.generators.config import GeneratorConfig
from data.generators.generate import generate_dataset


class TestRelationshipIntegrity:
    """All references must be valid in clean (uncorrupted) cases."""

    @pytest.fixture
    def clean_cases(self):
        config = GeneratorConfig(seed=42, num_cases=50, corruption_rate=0.0)
        cases, _ = generate_dataset(config)
        return cases

    def test_settlement_references_valid_payment(self, clean_cases):
        for case in clean_cases:
            payment_ids = {p["payment_id"] for p in case.ground_truth.payments}
            for settlement in case.ground_truth.settlements:
                assert settlement["payment_id"] in payment_ids, (
                    f"Settlement {settlement['settlement_id']} references "
                    f"non-existent payment {settlement['payment_id']} "
                    f"in case {case.case_id}"
                )

    def test_fee_references_valid_payment(self, clean_cases):
        for case in clean_cases:
            payment_ids = {p["payment_id"] for p in case.ground_truth.payments}
            for fee in case.ground_truth.fees:
                assert fee["payment_id"] in payment_ids, (
                    f"Fee {fee['fee_id']} references non-existent "
                    f"payment {fee['payment_id']} in case {case.case_id}"
                )

    def test_fee_references_valid_settlement(self, clean_cases):
        for case in clean_cases:
            settlement_ids = {s["settlement_id"] for s in case.ground_truth.settlements}
            for fee in case.ground_truth.fees:
                if fee.get("settlement_id"):
                    assert fee["settlement_id"] in settlement_ids, (
                        f"Fee {fee['fee_id']} references non-existent "
                        f"settlement {fee['settlement_id']}"
                    )

    def test_refund_references_valid_payment(self, clean_cases):
        for case in clean_cases:
            payment_ids = {p["payment_id"] for p in case.ground_truth.payments}
            for refund in case.ground_truth.refunds:
                assert refund["payment_id"] in payment_ids, (
                    f"Refund {refund['refund_id']} references non-existent "
                    f"payment {refund['payment_id']}"
                )

    def test_payment_references_valid_order(self, clean_cases):
        for case in clean_cases:
            order_ids = {o["order_id"] for o in case.ground_truth.orders}
            for payment in case.ground_truth.payments:
                assert payment["order_id"] in order_ids, (
                    f"Payment {payment['payment_id']} references non-existent "
                    f"order {payment['order_id']}"
                )

    def test_no_orphaned_settlements(self, clean_cases):
        """Every settlement should have a corresponding payment."""
        for case in clean_cases:
            payment_ids = {p["payment_id"] for p in case.ground_truth.payments}
            for settlement in case.ground_truth.settlements:
                assert settlement["payment_id"] in payment_ids

    def test_case_ids_unique(self, clean_cases):
        case_ids = [c.case_id for c in clean_cases]
        assert len(case_ids) == len(set(case_ids)), "Duplicate case IDs found"

    def test_merchant_id_consistent_within_case(self, clean_cases):
        """All records in a case should belong to the same merchant."""
        for case in clean_cases:
            merchant_id = case.merchant_id
            for payment in case.ground_truth.payments:
                assert payment["merchant_id"] == merchant_id
            for order in case.ground_truth.orders:
                assert order["merchant_id"] == merchant_id
            for settlement in case.ground_truth.settlements:
                assert settlement["merchant_id"] == merchant_id
