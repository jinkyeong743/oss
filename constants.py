import numpy as np

SAMPLE_RATE = 44100 # WAV 오디오 샘플링 레이트
CANVAS_WIDTH = 750 # 캔버스 가로 길이
CANVAS_HEIGHT = 500 # 캔버스 세로 길이

# X 좌표를 음 이름으로 매핑하기 위한 기본 7음계 (도-레-미-파-솔-라-시)
BASE_NOTES_DIATONIC = ['c', 'd', 'e', 'f', 'g', 'a', 'b'] 

# 선의 복잡도에 따라 사용할 음계
SCALE_PENTATONIC = ['c', 'd', 'e', 'g', 'a'] # 직선에 가까운 선
SCALE_MAJOR = BASE_NOTES_DIATONIC # 일반적인 선
SCALE_CHROMATIC = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b'] # 복잡한 선

# 복잡도 기준값
SHARP_HIGH = 0.5  # 복잡한 선
SHARP_MID = 0.25  # 중간 수준의 선

MAX_EXPECTED_LENGTH = 2500 # 선의 최대 길이

# 감정별 음악 특징(템포와 옥타브)을 저장한 구조체
EMOTION_PARAMETERS = {
    "기쁨 (Joy)":      {"octave_base": 4, "duration_ratio": 0.5, "description": "경쾌하고 빠른 템포 (기준 옥타브: 4)"},
    "희망 (Hope)":       {"octave_base": 4, "duration_ratio": 0.8, "description": "밝고 보통 속도의 템포 (기준 옥타브: 4)"},
    "평온 (Serene)":     {"octave_base": 3, "duration_ratio": 1.5, "description": "편안하고 느린 템포 (기준 옥타브: 3)"},
    "분노 (Angry)":      {"octave_base": 3, "duration_ratio": 0.4, "description": "강렬하고 매우 빠른 템포 (기준 옥타브: 3)"},
    "격렬 (Intense)":    {"octave_base": 4, "duration_ratio": 0.5, "description": "높고 빠른 템포 (기준 옥타브: 4)"},
    "슬픔 (Sorrow)":     {"octave_base": 2, "duration_ratio": 2.0, "description": "매우 느리고 낮은 템포 (기준 옥타브: 2)"},
    "불안 (Anxious)":    {"octave_base": 3, "duration_ratio": 0.7, "description": "불규칙하고 빠른 템포 (기준 옥타브: 3)"},
}