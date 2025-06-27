import re

# 지역 → 중기예보 지역 코드 매핑
region_code_map = {
    "서울 강남구": "11B10101",
    "서울 서대문구": "11B10101",
    "부산 부산진구": "11H20201"
}

def resolve_region_from_address(address: str) -> str:
    address = address.strip()
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