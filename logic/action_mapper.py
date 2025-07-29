def map_action(category: str, description: str) -> str:
    category = category.lower()
    description = description.lower()

    if "플라스틱" in category:
        return "우측 플라스틱 통으로 이송"
    elif "종이" in category:
        if "오염" in description or "더러움" in description:
            return "일반 쓰레기로 이송 (세척 필요)"
        else:
            return "좌측 종이 통으로 이송"
    elif "캔" in category or "금속" in category:
        return "금속류 통으로 이송"
    elif "일반 쓰레기" in category or "분리 불가" in description:
        return "사용자 경고 및 제거 요청"
    else:
        return "판단 불가 – 수동 확인 필요"
