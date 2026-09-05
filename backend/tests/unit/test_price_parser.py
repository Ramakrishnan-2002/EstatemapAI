from app.utils.price_parser import IndianPriceParser


def test_parse_lakhs():
    assert IndianPriceParser.parse_inr("70 lakh") == 7_000_000.0
    assert IndianPriceParser.parse_inr("70 lakhs") == 7_000_000.0
    assert IndianPriceParser.parse_inr("70L") == 7_000_000.0
    assert IndianPriceParser.parse_inr("₹70L") == 7_000_000.0
    assert IndianPriceParser.parse_inr("Rs. 85 Lakhs") == 8_500_000.0
    assert IndianPriceParser.parse_inr("45.5 lakh") == 4_550_000.0


def test_parse_crores():
    assert IndianPriceParser.parse_inr("1 crore") == 10_000_000.0
    assert IndianPriceParser.parse_inr("1.2 crore") == 12_000_000.0
    assert IndianPriceParser.parse_inr("1.25 crores") == 12_500_000.0
    assert IndianPriceParser.parse_inr("₹1.5 Cr") == 15_000_000.0
    assert IndianPriceParser.parse_inr("2cr") == 20_000_000.0


def test_parse_thousands_and_raw_numeric():
    assert IndianPriceParser.parse_inr("50k") == 50_000.0
    assert IndianPriceParser.parse_inr("85 thousand") == 85_000.0
    assert IndianPriceParser.parse_inr("70,00,000") == 7_000_000.0
    assert IndianPriceParser.parse_inr("₹ 8,500,000") == 8_500_000.0
    assert IndianPriceParser.parse_inr(7500000) == 7_500_000.0


def test_parse_invalid_inputs():
    assert IndianPriceParser.parse_inr(None) is None
    assert IndianPriceParser.parse_inr("") is None
    assert IndianPriceParser.parse_inr("free luxury villa") is None
    assert IndianPriceParser.parse_inr(-500) is None
