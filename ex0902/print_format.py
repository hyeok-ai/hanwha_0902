title = "AI 서비스 백엔드 프로그래밍 실무"
lectures = [("파이썬 기본 문법", 8), ("클래스", 8), ("데코레이터", 8), ("예외 처리", 8), ("로깅", 8)]

line = "="*10

print(title)
print(line)

format_string = "{}, 시간:{}"

for lecture in lectures:
    print(format_string.format(*lecture))