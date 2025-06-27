import traceback
from app.services.predict_order_quantity import predict_store_order_quantity

if __name__ == "__main__":
    try:
        print("🚀 가맹점 주문량 예측 시작")
        predict_store_order_quantity()
        print("✅ 예측 완료 및 저장 성공")
    except Exception as e:
        print(f"❌ 예측 생성 중 예외 발생: {e}")
        traceback.print_exc() 
