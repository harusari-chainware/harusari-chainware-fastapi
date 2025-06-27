import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def get_sentiment_index(ym: str) -> float | None:
    """
    KOSIS에서 특정 월의 소비자심리지수를 가져옵니다.
    ym: '202507' 또는 '2025-07' 형태 모두 허용
    """
    try:
        # ✅ YYYY-MM 형태로 들어온 경우 YYYYMM으로 변환
        if "-" in ym:
            ym = datetime.strptime(ym, "%Y-%m").strftime("%Y%m")
    except Exception as e:
        print(f"❌ 날짜 형식 변환 실패: {ym} → {e}")
        return None

    url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
    params = {
        "method": "getList",
        "apiKey": os.getenv("KOSIS_API_KEY"),
        "format": "json",
        "jsonVD": "Y",
        "orgId": "301",
        "tblId": "DT_511Y002",
        "itmId": "13103134688999",  # 소비자심리지수
        "objL1": "ALL",
        "objL2": "ALL",
        "prdSe": "M",
        "startPrdDe": ym,
        "endPrdDe": ym
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        if isinstance(data, list):
            for item in data:
                if item.get("C2_NM") == "전체":
                    return float(item.get("DT"))
            print("⚠️ '전체' 항목이 응답에 없습니다.")
        else:
            print("⚠️ 예상하지 못한 응답 형식:", data)

    except Exception as e:
        print(f"❗ KOSIS 응답 파싱 오류: {e}")
        print("📦 응답 원문:", resp.text)

    return None
