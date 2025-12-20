"""
Unit tests for transaction aggregation logic.
This validates core data correctness for CRIS.
"""

def aggregate_transactions(transactions):
    """
    Aggregates transaction amounts per account.
    """
    result = {}
    for txn in transactions:
        acc = txn["acc"]
        amt = txn["amt"]
        result.setdefault(acc, 0)
        result[acc] += amt
    return result


def test_transaction_sum_per_account():
    transactions = [
        {"acc": "A1", "amt": 100},
        {"acc": "A1", "amt": 50},
        {"acc": "A2", "amt": 200},
    ]

    result = aggregate_transactions(transactions)

    assert result["A1"] == 150
    assert result["A2"] == 200
