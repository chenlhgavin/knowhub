"""Exercise 02: Custom Exceptions and BankAccount

Practice defining custom exception classes and using them in a
realistic class hierarchy:
- ValidationError for invalid inputs
- InsufficientFundsError for overdraft attempts
- BankAccount with deposit, withdraw, and transfer operations
"""


class ValidationError(Exception):
    """Raised when input validation fails.

    Attributes:
        message: A human-readable description of the validation failure.

    Implement __init__ that accepts a message string, stores it as
    self.message, and passes it to super().__init__().
    """

    def __init__(self, message: str):
        raise NotImplementedError("Implement ValidationError.__init__")


class InsufficientFundsError(Exception):
    """Raised when a withdrawal exceeds available balance.

    Attributes:
        amount: The amount that was requested.
        balance: The current balance at the time of the request.

    Implement __init__ that accepts amount and balance keyword arguments,
    stores them as attributes, and passes a descriptive string to
    super().__init__().
    """

    def __init__(self, amount: float, balance: float):
        raise NotImplementedError("Implement InsufficientFundsError.__init__")


class BankAccount:
    """A simple bank account with deposit, withdraw, and transfer.

    Attributes:
        owner: The name of the account holder.
        balance: The current balance (default 0).
    """

    def __init__(self, owner: str, balance: float = 0):
        raise NotImplementedError("Implement BankAccount.__init__")

    def deposit(self, amount: float) -> None:
        """Deposit money into the account.

        Args:
            amount: The amount to deposit. Must be positive.

        Raises:
            ValidationError: If amount is not positive.
        """
        raise NotImplementedError("Implement deposit")

    def withdraw(self, amount: float) -> None:
        """Withdraw money from the account.

        Args:
            amount: The amount to withdraw. Must be positive.

        Raises:
            ValidationError: If amount is not positive.
            InsufficientFundsError: If amount exceeds current balance.
        """
        raise NotImplementedError("Implement withdraw")

    def transfer(self, other: "BankAccount", amount: float) -> None:
        """Transfer money from this account to another.

        Args:
            other: The destination BankAccount.
            amount: The amount to transfer.

        Raises:
            ValidationError: If amount is not positive.
            InsufficientFundsError: If amount exceeds current balance.
        """
        raise NotImplementedError("Implement transfer")


if __name__ == "__main__":
    # --- ValidationError tests ---
    err = ValidationError("invalid input")
    assert err.message == "invalid input"
    assert str(err) == "invalid input"
    assert isinstance(err, Exception)

    # --- InsufficientFundsError tests ---
    err = InsufficientFundsError(amount=500, balance=100)
    assert err.amount == 500
    assert err.balance == 100
    assert isinstance(err, Exception)

    # --- BankAccount basic tests ---
    acc = BankAccount("Alice", 100)
    assert acc.owner == "Alice"
    assert acc.balance == 100

    acc.deposit(50)
    assert acc.balance == 150

    acc.withdraw(30)
    assert acc.balance == 120

    # --- BankAccount default balance ---
    acc2 = BankAccount("Bob")
    assert acc2.balance == 0

    # --- Deposit validation ---
    try:
        acc.deposit(0)
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert e.message  # Should have a message

    try:
        acc.deposit(-10)
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert e.message

    # --- Withdraw validation ---
    try:
        acc.withdraw(0)
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass

    try:
        acc.withdraw(-5)
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass

    # --- Insufficient funds ---
    try:
        acc.withdraw(9999)
        assert False, "Should have raised InsufficientFundsError"
    except InsufficientFundsError as e:
        assert e.amount == 9999
        assert e.balance == 120  # Balance unchanged from earlier

    # --- Transfer tests ---
    alice = BankAccount("Alice", 200)
    bob = BankAccount("Bob", 50)

    alice.transfer(bob, 75)
    assert alice.balance == 125
    assert bob.balance == 125

    # Transfer insufficient funds
    try:
        bob.transfer(alice, 500)
        assert False, "Should have raised InsufficientFundsError"
    except InsufficientFundsError:
        assert bob.balance == 125  # Balance unchanged
        assert alice.balance == 125  # Balance unchanged

    # Transfer invalid amount
    try:
        alice.transfer(bob, -10)
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass

    print("All ex02_custom_exceptions tests passed!")
