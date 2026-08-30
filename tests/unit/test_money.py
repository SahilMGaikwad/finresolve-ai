"""
FinResolve AI — Money Arithmetic Tests

Verifies integer-only monetary arithmetic. No float anywhere.
"""

import pytest

from data.schemas.enums import Currency
from data.schemas.money import Money


class TestMoneyCreation:
    """Tests for Money object creation."""

    def test_from_minor(self):
        m = Money.from_minor(5000, Currency.INR)
        assert m.amount_minor == 5000
        assert m.currency == Currency.INR

    def test_from_major(self):
        m = Money.from_major(500, Currency.INR)
        assert m.amount_minor == 50000  # 500 * 100

    def test_from_major_rejects_float(self):
        with pytest.raises(TypeError, match="Float is not allowed"):
            Money.from_major(500.50, Currency.INR)

    def test_from_minor_rejects_float(self):
        with pytest.raises(TypeError, match="Float is not allowed"):
            Money.from_minor(500.0, Currency.INR)

    def test_zero(self):
        m = Money.zero(Currency.INR)
        assert m.amount_minor == 0

    def test_amount_minor_is_int(self):
        m = Money.from_minor(100, Currency.INR)
        assert isinstance(m.amount_minor, int)


class TestMoneyArithmetic:
    """Tests for Money arithmetic — all integer, no float."""

    def test_addition(self):
        a = Money.from_minor(5000, Currency.INR)
        b = Money.from_minor(3000, Currency.INR)
        result = a + b
        assert result.amount_minor == 8000
        assert isinstance(result.amount_minor, int)

    def test_subtraction(self):
        a = Money.from_minor(5000, Currency.INR)
        b = Money.from_minor(3000, Currency.INR)
        result = a - b
        assert result.amount_minor == 2000

    def test_multiplication_by_int(self):
        m = Money.from_minor(5000, Currency.INR)
        result = m * 3
        assert result.amount_minor == 15000

    def test_multiplication_rejects_float(self):
        m = Money.from_minor(5000, Currency.INR)
        with pytest.raises(TypeError, match="Cannot multiply Money by float"):
            m * 1.5

    def test_rmul(self):
        m = Money.from_minor(5000, Currency.INR)
        result = 3 * m
        assert result.amount_minor == 15000

    def test_currency_mismatch_addition(self):
        a = Money.from_minor(5000, Currency.INR)
        b = Money.from_minor(3000, Currency.USD)
        with pytest.raises(ValueError, match="Currency mismatch"):
            a + b

    def test_currency_mismatch_subtraction(self):
        a = Money.from_minor(5000, Currency.INR)
        b = Money.from_minor(3000, Currency.USD)
        with pytest.raises(ValueError, match="Currency mismatch"):
            a - b


class TestMoneyBasisPoints:
    """Tests for basis-point multiplication — critical for fee calculations."""

    def test_two_percent_fee(self):
        """200 bps = 2.00% fee"""
        payment = Money.from_minor(5000000, Currency.INR)  # ₹50,000
        fee = payment.multiply_bps(200)
        assert fee.amount_minor == 100000  # ₹1,000
        assert isinstance(fee.amount_minor, int)

    def test_eighteen_percent_gst(self):
        """1800 bps = 18% GST on a fee"""
        fee = Money.from_minor(100000, Currency.INR)  # ₹1,000
        gst = fee.multiply_bps(1800)
        assert gst.amount_minor == 18000  # ₹180

    def test_full_fee_chain(self):
        """Payment → platform fee → GST on fee → net settlement"""
        payment = Money.from_minor(5000000, Currency.INR)  # ₹50,000
        platform_fee = payment.multiply_bps(200)            # 2%
        gst = platform_fee.multiply_bps(1800)               # 18% of fee
        total_fee = platform_fee + gst
        net = payment - total_fee

        assert platform_fee.amount_minor == 100000  # ₹1,000
        assert gst.amount_minor == 18000            # ₹180
        assert total_fee.amount_minor == 118000     # ₹1,180
        assert net.amount_minor == 4882000          # ₹48,820

        # Verify all values are integers
        for m in [platform_fee, gst, total_fee, net]:
            assert isinstance(m.amount_minor, int)

    def test_bps_rejects_float(self):
        m = Money.from_minor(5000, Currency.INR)
        with pytest.raises(TypeError, match="basis_points must be int"):
            m.multiply_bps(200.5)

    def test_zero_bps(self):
        m = Money.from_minor(5000, Currency.INR)
        result = m.multiply_bps(0)
        assert result.amount_minor == 0


class TestMoneyComparison:
    """Tests for Money comparison operators."""

    def test_equality(self):
        a = Money.from_minor(5000, Currency.INR)
        b = Money.from_minor(5000, Currency.INR)
        assert a == b

    def test_inequality(self):
        a = Money.from_minor(5000, Currency.INR)
        b = Money.from_minor(3000, Currency.INR)
        assert a != b

    def test_less_than(self):
        a = Money.from_minor(3000, Currency.INR)
        b = Money.from_minor(5000, Currency.INR)
        assert a < b

    def test_greater_than(self):
        a = Money.from_minor(5000, Currency.INR)
        b = Money.from_minor(3000, Currency.INR)
        assert a > b

    def test_comparison_currency_mismatch(self):
        a = Money.from_minor(5000, Currency.INR)
        b = Money.from_minor(5000, Currency.USD)
        with pytest.raises(ValueError, match="Currency mismatch"):
            a < b


class TestMoneyDisplay:
    """Tests for Money display formatting."""

    def test_amount_major(self):
        m = Money.from_minor(5050, Currency.INR)
        assert m.amount_major == "50.50"

    def test_str(self):
        m = Money.from_minor(5050, Currency.INR)
        assert str(m) == "INR 50.50"

    def test_repr(self):
        m = Money.from_minor(5050, Currency.INR)
        assert "50.50" in repr(m)
        assert "INR" in repr(m)

    def test_immutability(self):
        """Money objects are frozen — cannot be modified."""
        m = Money.from_minor(5000, Currency.INR)
        with pytest.raises(Exception):
            m.amount_minor = 9999
