import streamlit as st
import numpy as np
from streamlit_drawable_canvas import st_canvas
from scipy.io.wavfile import write

# --------------------------------------------------------------------
# A. 필요 상수와 함수 정의 
# --------------------------------------------------------------------

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

# 특정 주파수와 특정 길이의 사인파 오디오 데이터 생성하는 함수
def generate_note_wave(note_freq, duration_seconds, amplitude=4096):
    t = np.linspace(0, duration_seconds, int(SAMPLE_RATE * duration_seconds), False)
    audio = amplitude * np.sin(note_freq * 2 * np.pi * t)
    return audio.astype(np.int16)

# 음표 문자열(c#4)을 실제 주파수로 변환하는 함수
def note_to_freq(note_str):
    notes = {
        'c': 261.63, 'c#': 277.18, 'd': 293.66, 'd#': 311.13, 
        'e': 329.63, 'f': 349.23, 'f#': 369.99, 'g': 392.00, 
        'g#': 415.30, 'a': 440.00, 'a#': 466.16, 'b': 493.88
    } # 4옥타브 기준 주파수
    
    base_note = note_str[:-1].lower()
    try:
        octave = int(note_str[-1])
    except ValueError:
        octave = 4 # 4옥타브를 기본으로 설정

    freq = notes.get(base_note, 0)
    if freq == 0: return 0
    
    return freq * (2 ** (octave - 4))

# 하나의 선을 분석하여 하나의 멜로디를 생성하는 함수
def generate_voice_melody(path_coords, params):
    
    coords = np.array(path_coords)
    x = coords[:, 0]
    y = coords[:, 1]
    
    # 감정 구조체의 요소 불러오기
    octave_base = params["octave_base"]
    note_duration_ratio = params["duration_ratio"]
    
    # 선 길이 계산
    dx = np.diff(x)
    dy = np.diff(y)
    total_length = np.sum(np.sqrt(dx**2 + dy**2)) 
    
    # 기울기 변화량(복잡도) 계산
    slopes = np.divide(dy, dx, out=np.zeros_like(dy, dtype=float), where=dx!=0)
    slope_changes = np.abs(np.diff(slopes))
    sharpness_score = np.mean(slope_changes)
    
    # 선 길이 50픽셀 당 음표 하나 생성
    num_melody_notes = min(32, int(total_length / 50)) 
    if num_melody_notes == 0:
        return None, total_length, 0.0, None

    # 선 길이에 따른 음표 길이 결정
    length_ratio = min(total_length / MAX_EXPECTED_LENGTH, 1.5)
    base_duration = 0.3 # 기본 음표 길이
    duration_sec = base_duration * length_ratio * note_duration_ratio 
    
    # 복잡도에 따른 음계 결정
    if sharpness_score >= SHARP_HIGH:
        current_scale = SCALE_CHROMATIC
    elif sharpness_score >= SHARP_MID:
        current_scale = SCALE_MAJOR
    else:
        current_scale = SCALE_PENTATONIC
        
    # 사용할 음의 개수
    NUM_SCALE_NOTES = len(current_scale)
    
    # 총 좌표 중에서 샘플링할 좌표 선택
    indices_to_sample = np.linspace(0, len(x) - 1, num_melody_notes, dtype=int)
    
    voice_audio = np.array([], dtype=np.int16)
    
    for i in indices_to_sample:
        # x좌표에 따른 음 이름 선택
        X_norm = x[i] / CANVAS_WIDTH
        note_index = int(np.clip(X_norm * NUM_SCALE_NOTES, 0, NUM_SCALE_NOTES - 1))
        base_note_name = current_scale[note_index]
        
        # y좌표에 따른 옥타브 결정
        Y_inverted_norm = 1.0 - (y[i] / CANVAS_HEIGHT)
        octave_shift = int(np.clip(Y_inverted_norm * 4, 0, 3))
        current_octave = octave_base + octave_shift # 2옥타브-7옥타브 사용

        # 최종 음표 생성
        note_str = f'{base_note_name}{current_octave}'
        freq = note_to_freq(note_str)
        
        # 웨이브 생성
        note_wave = generate_note_wave(freq, duration_sec)
        voice_audio = np.concatenate((voice_audio, note_wave))

    return voice_audio, total_length, sharpness_score, current_scale

# 여러 개의 선으로 여러 멜로디를 생성하고 믹싱하는 함수
def analyze_and_compose_polyphony(all_paths, selected_emotion):
    
    # 감정 불러오기
    params = EMOTION_PARAMETERS.get(selected_emotion)
    if not params:
        return None, "선택된 감정에 대한 음악 파라미터를 찾을 수 없습니다."
    
    voice_audios = []
    voice_results = [] # 분석 결과 저장용
    
    # 선 개수만큼 멜로디 생성
    for path_coords in all_paths:
        voice_audio, total_length, sharpness_score, current_scale = generate_voice_melody(path_coords, params)
        
        if voice_audio is not None:
            voice_audios.append(voice_audio)
            
            voice_results.append({
                "length": total_length,
                "sharpness": sharpness_score,
                "scale": current_scale
            })

    if not voice_audios:
        return None, "캔버스에서 유효한 선을 찾을 수 없습니다. 선을 하나 이상 길게 그려주세요."
    
    # 믹싱: 멜로디 길이를 맞추고 합친 후, 볼륨을 조절
    max_len = max(len(audio) for audio in voice_audios)
    mixed_audio_float = np.zeros(max_len, dtype=np.float32)
    
    for audio in voice_audios:
        padded_audio = np.pad(audio, (0, max_len - len(audio)), 'constant')
        mixed_audio_float += padded_audio
        
    # 볼륨 조절
    mixed_audio_float /= len(voice_audios) 
    mixed_audio_int16 = np.clip(mixed_audio_float, -32768, 32767).astype(np.int16)
    
    # WAV 파일 생성
    output_filename = "output_melody.wav"
    try:
        write(output_filename, SAMPLE_RATE, mixed_audio_int16)
        
        # 분석 결과 텍스트 생성
        result_text = f"**선택 감정:** {selected_emotion} | 총 {len(voice_audios)}개 선을 사용해 멜로디 생성 | "
        result_text += params["description"] + "\n\n"
        result_text += "\n**각 선 분석:**\n"
        for idx, res in enumerate(voice_results):
            scale_name = "펜타토닉 (5음)" if len(res['scale']) == 5 else ("온음계 (7음)" if len(res['scale']) == 7 else "반음계 (12음)")
            result_text += (
                f"- 선 {idx+1}: 길이 {res['length']:.0f}px | 복잡도 {res['sharpness']:.2f} "
                f"-> {scale_name} 사용\n"
            )
        
        return output_filename, result_text
    
    except Exception as e:
        return None, f"음악 파일 생성 중 오류가 발생했습니다. (오류: {e})"
    
# --------------------------------------------------------------------
# B. Streamlit UI 구성
# --------------------------------------------------------------------

st.set_page_config(layout="wide", page_title="Drawing to Song 🎶")

st.markdown("""
<style>
.main {
    background-color: #f7f7f7;
}

.stExpander > div:first-child {
    border-radius: 8px;
    background-color: #f0f2f6;
}
.stButton>button {
    background-color: #red !important;
    color: white;
    border-radius: 8px;
    height: 3rem;
    font-size: 1.2rem;
    font-weight: bold;
    border: 2px solid #FFFFFF;
}
.stButton>button:hover {
    color: white;
    border: 2px solid #FFFFFF;
    filter: none;
}
</style>
""", unsafe_allow_html=True)

st.title("🎼 Melody Canvas")
st.markdown("#### 그림을 그리면, 나만의 음악이 됩니다.")

st.subheader("🎹 멜로디 생성 규칙 확인")
with st.expander("규칙 자세히 보기", expanded=False):
    st.markdown("""
    이 캔버스는 가로축(X)과 세로축(Y)의 위치, 그리고 선의 특성을 악보처럼 해석합니다.

    * **선의 가로축 위치**: 왼쪽(도)에서 오른쪽(시)으로 갈수록 계이름이 높아집니다.
    * **선의 세로축 위치**: 위쪽(고음)에서 아래쪽(저음)으로 갈수록 옥타브가 낮아집니다.
    * **선 길이**: 선이 길수록 음표가 길어집니다.
    * **선의 복잡도**: 부드러운 선은 안정적인 5음계, 복잡한 선은 긴장감 있는 12음계를 사용합니다.
    * **감정**: 선택한 감정에 따라서 곡의 분위기가 바뀝니다.
    """)

st.markdown("---")
st.subheader("2. 감정과 색깔 설정하기")

col1, col2, col_space = st.columns([2, 2, 4])
with col1:
    selected_emotion = st.selectbox("감정 선택", EMOTION_PARAMETERS.keys())
with col2:
    stroke_color = st.color_picker("선 색깔 선택", "#FF4B4B") # 기본 색상을 눈에 띄게 변경

# --- 캔버스 구역 ---
st.subheader("3. 캔버스에 자유롭게 그림 그리기")

st.markdown(
    "<div style='text-align: center; color: #6C5CE7; padding-bottom: 5px;'>⬆️ 높은 옥타브</div>",
    unsafe_allow_html=True
)

col_left_marker, col_canvas, col_right_marker = st.columns([1, 8, 1])

with col_canvas:
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.0)",
        stroke_width=5,
        stroke_color=stroke_color,
        background_color="#FFFFFF",
        height=CANVAS_HEIGHT,
        width=CANVAS_WIDTH,
        drawing_mode="freedraw",
        update_streamlit=True,
        key="canvas",
    )

col_footer_left, col_footer_center, col_footer_right = st.columns([1, 8, 1])
with col_footer_center:
    st.markdown(
        "<div style='display: flex; justify-content: space-between; width: 100%; padding-top: 10px;'>"
        "<span style='color: #555; font-weight: bold;'>⬅️ 도, C</span>"
        "<span style='color: #555; font-weight: bold;'> 시, B ➡️</span>"
        "</div>", 
        unsafe_allow_html=True
    )

st.markdown(
    "<div style='text-align: center; color: #6C5CE7; padding-top: 5px;'>⬇️ 낮은 옥타브</div>",
    unsafe_allow_html=True
)

st.markdown("---")

# 멜로디 생성 버튼
if st.button("🎶 4. 멜로디 생성 및 재생", use_container_width=True, type="primary"):
    if canvas_result.json_data: 
        
        all_objects = canvas_result.json_data.get('objects', [])
        all_paths_coords = []
        
        # 1. 모든 선 객체의 좌표를 분리하여 멜로디 생성용 데이터로 변환
        if all_objects:
            for obj in all_objects:
                if obj.get('type') == 'path':
                    path_array = obj.get('path', [])
                    drawing_points = []
                    
                    for command in path_array:
                        command_type = command[0]
                        
                        # 좌표 추출 (M, L, C, Q 명령어에서 모든 점 추출)
                        if command_type == 'M' or command_type == 'L':
                            if len(command) >= 3:
                                drawing_points.append((command[1], command[2]))
                        elif command_type == 'C':
                            if len(command) >= 7:
                                drawing_points.append((command[1], command[2])) 
                                drawing_points.append((command[3], command[4])) 
                                drawing_points.append((command[5], command[6])) 
                        elif command_type == 'Q':
                            if len(command) >= 5:
                                drawing_points.append((command[1], command[2])) 
                                drawing_points.append((command[3], command[4])) 
                    
                    if drawing_points:
                        all_paths_coords.append(drawing_points)
        
        # 2. 추출된 모든 선 리스트를 분석 함수에 전달
        if all_paths_coords:
            
            # 결과 생성
            st.subheader("5. 생성 결과")

            with st.spinner(f"총 {len(all_paths_coords)}개 선의 멜로디를 믹싱 중입니다... 🎵"):
                audio_file_path, analysis_result = analyze_and_compose_polyphony(all_paths_coords, selected_emotion)
            
            if audio_file_path:
                st.success("✅ 멜로디 생성이 완료되었습니다!")
                st.markdown("---")
                st.markdown(analysis_result)
                st.markdown("---")
                try:
                    audio_bytes = open(audio_file_path, 'rb').read()
                    st.audio(audio_bytes, format='audio/wav')
                except FileNotFoundError:
                    st.error("오디오 파일 재생에 실패했습니다.")
            elif analysis_result:
                st.error(f"❌ 생성 실패: {analysis_result}")
            
        else:
            st.warning("⚠️ 캔버스에 선이 인식되지 않았습니다. 선을 하나 이상 길게 그려주세요!")

    else:
        st.warning("⚠️ 캔버스 데이터를 인식할 수 없습니다.") 