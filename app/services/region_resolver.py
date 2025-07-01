import re

# 지역 → 중기예보 지역 코드 매핑
region_code_map = {
    "서울 강남구": "11B10101",
    "서울 마포구": "11B10101",
    "서울 중구": "11B10101",
    "서울 송파구": "11B10101",
    "서울 노원구": "11B10101",
    "서울 동작구": "11B10101",
    "서울 용산구": "11B10101",
    "서울 서초구": "11B10101",
    "서울 은평구": "11B10101",
    "서울 관악구": "11B10101",
    "서울 강동구": "11B10101",
    "서울 서대문구": "11B10101",
    "부산 부산진구": "11H20201",
    # 필요 시 여기에 더 추가
}

# ✅ 행정구역명 정규화 매핑 (시/도 단위)
normalize_map = {
    "서울시": "서울", "부산시": "부산", "대구시": "대구", "인천시": "인천", "광주시": "광주",
    "대전시": "대전", "울산시": "울산", "세종시": "세종",
    "경기도": "경기", "강원도": "강원", "충청북도": "충북", "충청남도": "충남",
    "전라북도": "전북", "전라남도": "전남", "경상북도": "경북", "경상남도": "경남",
    "제주도": "제주"
}

def normalize_address(address: str) -> str:
    for original, normalized in normalize_map.items():
        if original in address:
            address = address.replace(original, normalized)
    return address.strip()

def resolve_region_from_address(address: str) -> str:
    address = normalize_address(address)
    print(f"📥 원본 주소: {address}")
    match = re.search(
        r'(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)\s+(?:(\S+?[구시군]))',
        address
    )
    if match:
        region_name = f"{match.group(1)} {match.group(2)}"
        print(f"✅ 지역 추출 성공: {region_name}")
        return region_name
    else:
        print(f"❌ 지역 추출 실패")
        return "UNKNOWN"

def resolve_midterm_region_code(address: str) -> tuple[str, str]:
    """
    전체 주소를 받아 지역명과 중기예보용 region_code를 함께 반환
    """
    region_name = resolve_region_from_address(address)
    region_code = region_code_map.get(region_name, "UNKNOWN")
    print(f"📌 주소: {address} → 추출된 지역명: '{region_name}' → 코드: {region_code}")
    return region_code, region_name
