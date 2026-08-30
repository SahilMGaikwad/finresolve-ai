"""
FinResolve AI — Money Value Object

Integer-only monetary arithmetic. No floats anywhere in the financial data path.

All amounts are stored as integers in minor currency units:
- INR: paise (1 INR = 100 paise)
- USD: cents  (1 USD = 100 cents)

This eliminates floating-point rounding errors in financial calculations.
"""

from __future__ import annotations

from data.schemas.enums import Currency, CURRENCY_MINOR_UNITS
from pydantic import BaseModel, model_validator


class Money(BaseModel):
    """
    Immutable money value object with integer-only arithmetic.

    Attributes:
        amount_minor: Amount in minor currency units (paise, cents, etc.).
                      Must be non-negative for most operations.
        currency: ISO 4217 currency code.
    """

    amount_minor: int
    currency: Currency

    model_config = {"frozen": True}

    # ---- Factories ----

    @classmethod
    def from_major(cls, amount_major: int | str, currency: Currency) -> Money:
        """
        Create Money from a major-unit integer (e.g., rupees, dollars).

        Args:
            amount_major: Amount in major units. Must be an integer or
                          a string representation of an integer.
            currency: Currency code.

        Raises:
            TypeError: If amount_major is a float.
            ValueError: If amount_major cannot be converted to int.
        """
        if isinstance(amount_major, float):
            raise TypeError(
                "Float is not allowed for monetary values. "
                "Use an integer major amount or Money.from_minor() with exact paise/cents."
            )
        amount_int = int(amount_major)
        multiplier = CURRENCY_MINOR_UNITS[currency]
        return cls(amount_minor=amount_int * multiplier, currency=currency)

    @classmethod
    def from_minor(cls, amount_minor: int, currency: Currency) -> Money:
        """Create Money directly from minor units."""
        if isinstance(amount_minor, float):
            raise TypeError("Float is not allowed for monetary values.")
        return cls(amount_minor=int(amount_minor), currency=currency)

    @classmethod
    def zero(cls, currency: Currency) -> Money:
        """Create a zero-value Money object."""
        return cls(amount_minor=0, currency=currency)

    # ---- Validation ----

    @model_validator(mode="after")
    def _validate_amount_type(self) -> Money:
        """Ensure amount_minor is truly an integer, not a float that was coerced."""
        if not isinstance(self.amount_minor, int):
            raise TypeError(
                f"amount_minor must be int, got {type(self.amount_minor).__name__}"
            )
        return self

    # ---- Arithmetic (returns new Money, never mutates) ----

    def _check_currency(self, other: Money) -> None:
        """Raise if currencies don't match."""
        if self.currency != other.currency:
            raise ValueError(
                f"Currency mismatch: {self.currency.value} vs {other.currency.value}. "
                "Cannot perform arithmetic on different currencies."
            )

    def __add__(self, other: Money) -> Money:
        self._check_currency(other)
        return Money(amount_minor=self.amount_minor + other.amount_minor, currency=self.currency)

    def __sub__(self, other: Money) -> Money:
        self._check_currency(other)
        return Money(amount_minor=self.amount_minor - other.amount_minor, currency=self.currency)

    def __mul__(self, factor: int) -> Money:
        """Multiply by an integer factor."""
        if isinstance(factor, float):
            raise TypeError("Cannot multiply Money by float. Use multiply_bps() for percentage calculations.")
        return Money(amount_minor=self.amount_minor * int(factor), currency=self.currency)

    def __rmul__(self, factor: int) -> Money:
        return self.__mul__(factor)

    def multiply_bps(self, basis_points: int) -> Money:
        """
        Multiply by a rate expressed in basis points (1 bps = 0.01%).

        Uses integer arithmetic with banker's rounding.
        10000 bps = 100%.

        Example:
            fee = payment.multiply_bps(200)  # 2% fee
        """
        if isinstance(basis_points, float):
            raise TypeError("basis_points must be int.")
        # Integer division with rounding: (a * b + 5000) // 10000
        result = (self.amount_minor * basis_points + 5000) // 10000
        return Money(amount_minor=result, currency=self.currency)

    # ---- Comparison ----

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount_minor == other.amount_minor and self.currency == other.currency

    def __lt__(self, other: Money) -> bool:
        self._check_currency(other)
        return self.amount_minor < other.amount_minor

    def __le__(self, other: Money) -> bool:
        self._check_currency(other)
        return self.amount_minor <= other.amount_minor

    def __gt__(self, other: Money) -> bool:
        self._check_currency(other)
        return self.amount_minor > other.amount_minor

    def __ge__(self, other: Money) -> bool:
        self._check_currency(other)
        return self.amount_minor >= other.amount_minor

    def __hash__(self) -> int:
        return hash((self.amount_minor, self.currency))

    # ---- Display ----

    @property
    def amount_major(self) -> str:
        """
        Human-readable major-unit string (e.g., '500.00').

        For display only — never use this for calculations.
        """
        multiplier = CURRENCY_MINOR_UNITS[self.currency]
        major = self.amount_minor // multiplier
        minor = abs(self.amount_minor) % multiplier
        return f"{major}.{minor:02d}"

    def __repr__(self) -> str:
        return f"Money({self.amount_major} {self.currency.value})"

    def __str__(self) -> str:
        return f"{self.currency.value} {self.amount_major}"
