
import pytest

from bookstore_trade_in import (
    process_book_buybacks,
    inspect_scanner_calibration
)


# 1. Test invalid input
def test_invalid_batches():
    with pytest.raises(ValueError):
        process_book_buybacks("invalid", 5.0)


def test_negative_store_credit_bonus():
    with pytest.raises(ValueError):
        process_book_buybacks([], -5.0)


# 2. Test all supported book formats
@pytest.mark.parametrize(
    "book_format, expected",
    [
        ("textbook", 40.0),
        ("hardcover", 15.0),
        ("paperback", 8.0)
    ]
)
def test_book_formats(book_format, expected):
    batches = [{
        "intake_approved": True,
        "format": book_format,
        "books": [{}]
    }]

    result = process_book_buybacks(batches, 5.0)

    assert result["total_payout"] == expected
    assert result["status"] == "COMPLETED"


# 3. Test book conditions
def test_mint_condition():
    batches = [{
        "intake_approved": True,
        "format": "textbook",
        "books": [{"condition": "mint"}]
    }]

    result = process_book_buybacks(batches, 5.0)

    assert result["total_payout"] == 50.0


def test_poor_condition():
    batches = [{
        "intake_approved": True,
        "format": "hardcover",
        "books": [{"condition": "poor"}]
    }]

    result = process_book_buybacks(batches, 5.0)

    assert result["total_payout"] == 6.0


# 4. Test unapproved batches
def test_unapproved_batch():
    batches = [{
        "intake_approved": False,
        "format": "paperback",
        "books": [{}]
    }]

    result = process_book_buybacks(batches, 5.0)

    assert result["total_payout"] == 0.0
    assert result["status"] == "ZERO_CREDIT"


# 5. Test unsupported book format
def test_unsupported_format():
    batches = [{
        "intake_approved": True,
        "format": "magazine",
        "books": [{}]
    }]

    result = process_book_buybacks(batches, 5.0)

    assert result["status"] == "ZERO_CREDIT"


# 6. Test books with missing pages
def test_missing_pages():
    batches = [{
        "intake_approved": True,
        "format": "paperback",
        "books": [{"missing_pages": 2}]
    }]

    result = process_book_buybacks(batches, 5.0)

    assert result["status"] == "ZERO_CREDIT"


# 7. Test counterfeit paperback
def test_counterfeit_paperback():
    batches = [{
        "intake_approved": True,
        "format": "paperback",
        "books": [{"counterfeit": True}]
    }]

    result = process_book_buybacks(batches, 5.0)

    assert result["total_payout"] == 0.0


# 8. Test counterfeit textbook
def test_counterfeit_textbook():
    batches = [{
        "intake_approved": True,
        "format": "textbook",
        "books": [
            {"counterfeit": True},
            {"condition": "mint"}
        ]
    }]

    result = process_book_buybacks(batches, 5.0)

    assert result["total_payout"] == 0.0


# 9. Test store credit bonus
def test_store_credit_bonus():
    batches = [{
        "intake_approved": True,
        "format": "paperback",
        "payout_in_credit": True,
        "books": []
    }]

    result = process_book_buybacks(batches, 5.0)

    assert result["total_payout"] == 5.0
    assert result["status"] == "COMPLETED"


# 10. Test audit rejection
def test_audit_rejection():
    batches = [{
        "intake_approved": True,
        "format": "paperback",
        "books": [{"missing_pages": 1} for _ in range(5)]
    }]

    result = process_book_buybacks(batches, 5.0)

    assert result["status"] == "AUDIT_REJECTED"


# 11. Test empty batches
def test_empty_batches():
    result = process_book_buybacks([], 5.0)

    assert result["total_payout"] == 0.0
    assert result["status"] == "ZERO_CREDIT"


# 12. Test scanner with no data
def test_scanner_no_data():
    assert inspect_scanner_calibration([]) == "NO_DATA"


# 13. Test calibrated scanner
def test_scanner_calibrated():
    matrix = [[1, 2, 3], [4, 5, 2]]

    assert inspect_scanner_calibration(matrix) == "CALIBRATED"


# 14. Test scanner requiring recalibration
def test_scanner_recalibration():
    matrix = [[6, 7]]

    assert inspect_scanner_calibration(matrix) == "RECALIBRATE"


# 15. Test reset of consecutive misread streak
def test_scanner_streak_reset():
    matrix = [[6, 3, 7]]

    assert inspect_scanner_calibration(matrix) == "CALIBRATED"


# ==========================================
# ADDITIONAL BRANCH COVERAGE TEST CASES
# ==========================================

# 1. Test counterfeit hardcover
def test_counterfeit_hardcover():
    batches = [{
        "intake_approved": True,
        "format": "hardcover",
        "books": [{"counterfeit": True}]
    }]

    result = process_book_buybacks(batches, 5.0)

    assert result["total_payout"] == 0.0


# 2. Test missing pages
def test_missing_pages_boundary():
    batches = [{
        "intake_approved": True,
        "format": "paperback",
        "books": [{"missing_pages": 5}]
    }]

    result = process_book_buybacks(batches, 5.0)

    assert result["status"] == "ZERO_CREDIT"


# 3. Test exactly five rejected books
def test_exactly_five_rejected_books():
    batches = [{
        "intake_approved": True,
        "format": "paperback",
        "books": [{"missing_pages": 1} for _ in range(5)]
    }]

    result = process_book_buybacks(batches, 5.0)

    assert result["status"] == "AUDIT_REJECTED"


# 4. Test four rejected books
def test_four_rejected_books():
    batches = [{
        "intake_approved": True,
        "format": "paperback",
        "books": [{"missing_pages": 1} for _ in range(4)]
    }]

    result = process_book_buybacks(batches, 5.0)

    assert result["status"] == "ZERO_CREDIT"


# 5. Test single high scanner reading
def test_single_high_scanner_reading():
    matrix = [[6]]

    assert inspect_scanner_calibration(matrix) == "CALIBRATED"


# 6. Test scanner error rate exactly 5
def test_scanner_error_rate_boundary():
    matrix = [[5, 5, 5]]

    assert inspect_scanner_calibration(matrix) == "CALIBRATED"


# 7. Test recalibration on second device
def test_scanner_second_device_recalibration():
    matrix = [[6], [7, 8]]

    assert inspect_scanner_calibration(matrix) == "RECALIBRATE"

