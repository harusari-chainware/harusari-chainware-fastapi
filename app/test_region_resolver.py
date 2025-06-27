from services.region_resolver import resolve_region_from_address

# 테스트할 주소
address = "서울 강남구 테헤란로 123"

# 함수 호출
region = resolve_region_from_address(address)

# 결과 출력
print(f"주소: {address}")
print(f"추출된 지역: {region}")
