from app.services.sentiment_fetcher import get_sentiment_index
print(get_sentiment_index("202506"))  # 현재월
print(get_sentiment_index("202507"))  # 다음월 (예측 대상)
