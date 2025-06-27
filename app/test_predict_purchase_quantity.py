import traceback
from app.services.predict_purchase_quantity import predict_purchase_order_quantity

if __name__ == "__main__":
    try:
        print("🚛 본사 발주량 예측 시작")
        predict_purchase_order_quantity()
        print("✅ 발주량 예측 및 저장 완료")
    except Exception as e:
        print(f"❌ 예측 생성 중 예외 발생: {e}")
        traceback.print_exc() 
