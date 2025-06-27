import os
import requests
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, date as DateType
from dotenv import load_dotenv

load_dotenv()


def is_holiday(date: DateType) -> bool:
    """
    주어진 날짜가 법정 공휴일인지 여부를 반환합니다.
    :param date: datetime.date 객체
    :return: True (공휴일) or False
    """
    service_key = urllib.parse.unquote(os.getenv("HOLIDAY_API_KEY"))
    date_str = date.strftime('%Y%m%d')
    year = date.strftime('%Y')
    month = date.strftime('%m')

    url = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo"
    params = {
        "serviceKey": service_key,
        "solYear": year,
        "solMonth": month,
        "numOfRows": 100
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            print("❗ 응답 실패:", response.status_code)
            return False

        root = ET.fromstring(response.content)
        items = root.find('.//items')

        if items is not None:
            for item in items.findall('item'):
                locdate = item.find('locdate').text
                if locdate == date_str:
                    return True
        return False

    except Exception as e:
        print(f"공휴일 API 호출 오류: {e}")
        return False


def is_weekend(date: DateType) -> bool:
    """ 주말 여부 (토: 5, 일: 6) """
    return date.weekday() >= 5


def is_public_or_weekend(date: DateType) -> bool:
    return is_holiday(date) or is_weekend(date)


def get_date_type(date: DateType) -> str:
    """
    날짜가 공휴일/주말/평일인지 분류합니다.
    :return: '공휴일', '주말', '평일'
    """
    if is_holiday(date):
        return "공휴일"
    elif is_weekend(date):
        return "주말"
    else:
        return "평일"
