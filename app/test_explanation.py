from datetime import date
from services.explanation_generator import generate_sales_explanation

explanation = generate_sales_explanation(
    franchise_name="카페하루",
    region="서울 강남구",
    target_date=date(2025, 6, 30),
    predicted_sales=1850000,
    external_factors={
        "avg_temp": 28.6,
        "precipitation": 12.3,
        "sentiment_index": 94.5
    }
)

print("📄 설명 결과:")
print(explanation)
