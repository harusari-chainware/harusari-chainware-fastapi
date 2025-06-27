import traceback
from app.services.prediction_generator import generate_weekly_predictions

if __name__ == "__main__":
    try:
        print("📦 예측 생성 테스트 시작")
        generate_weekly_predictions()
        print("✅ 예측 생성 및 저장 완료")
    except Exception as e:
        print(f"❌ 예측 생성 중 예외 발생: {e}")
        traceback.print_exc()  # ✅ 전체 에러 로그 출력!
