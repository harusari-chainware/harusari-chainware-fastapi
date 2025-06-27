from app.services.model_trainer import train_and_save_model
from app.services.training_data_generator import generate_training_data

# 🔍 디버깅용 출력
df = generate_training_data()
print("📊 DataFrame 컬럼 목록:", df.columns)
print("🔍 상위 5개 데이터:")
print(df.head())

train_and_save_model()
