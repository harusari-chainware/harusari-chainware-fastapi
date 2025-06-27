from services.holiday_fetcher import is_public_or_weekend

test_dates = ["20250603", "20250606", "20250607", "20250605"]
for d in test_dates:
    print(f"{d}은 공휴일 또는 주말인가요? → {is_public_or_weekend(d)}")
