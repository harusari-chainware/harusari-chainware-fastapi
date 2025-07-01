from apscheduler.schedulers.blocking import BlockingScheduler
from app.services.accuracy_calculator import calculate_accuracy_for_all_predictions

scheduler = BlockingScheduler()

# 매일 오전 1시에 실행
@scheduler.scheduled_job('cron', hour=1, minute=0)
def scheduled_job():
    print("[SCHEDULER] 🕐 정확도 계산 시작 (어제까지 반영)")
    calculate_accuracy_for_all_predictions()
    print("[SCHEDULER] ✅ 완료")


if __name__ == "__main__":
    print("[SCHEDULER] 스케줄러 시작")
    scheduler.start()
