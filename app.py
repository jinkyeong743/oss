import streamlit as st
from streamlit_drawable_canvas import st_canvas
from constants import EMOTION_PARAMETERS, CANVAS_HEIGHT, CANVAS_WIDTH
from audio_utils import analyze_and_compose_polyphony

# ------------------------------
# Streamlit 페이지 설정 및 스타일
# ------------------------------
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
    background-color: #FF4B4B !important;
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

# ------------------------------
# 타이틀 및 설명
# ------------------------------
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

# ------------------------------
# 감정과 색상 설정
# ------------------------------
st.subheader("2. 감정과 색깔 설정하기")
col1, col2, col_space = st.columns([2, 2, 4])
with col1:
    selected_emotion = st.selectbox("감정 선택", EMOTION_PARAMETERS.keys())
with col2:
    stroke_color = st.color_picker("선 색깔 선택", "#FF4B4B") 

# ------------------------------
# 캔버스 영역
# ------------------------------
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

# ------------------------------
# 멜로디 생성 버튼
# ------------------------------
if st.button("🎶 4. 멜로디 생성 및 재생", use_container_width=True, type="primary"):
    if canvas_result.json_data: 
        all_objects = canvas_result.json_data.get('objects', [])
        all_paths_coords = []

        # 모든 선 좌표 추출
        if all_objects:
            for obj in all_objects:
                if obj.get('type') == 'path':
                    path_array = obj.get('path', [])
                    drawing_points = []

                    for command in path_array:
                        command_type = command[0]
                        if command_type in ['M', 'L'] and len(command) >= 3:
                            drawing_points.append((command[1], command[2]))
                        elif command_type == 'C' and len(command) >= 7:
                            drawing_points.extend([(command[1], command[2]), (command[3], command[4]), (command[5], command[6])])
                        elif command_type == 'Q' and len(command) >= 5:
                            drawing_points.extend([(command[1], command[2]), (command[3], command[4])])
                    
                    if drawing_points:
                        all_paths_coords.append(drawing_points)

        if all_paths_coords:
            st.subheader("5. 생성 결과")
            with st.spinner(f"총 {len(all_paths_coords)}개 선의 멜로디를 믹싱 중입니다... 🎵"):
                audio_file_path, analysis_result = analyze_and_compose_polyphony(all_paths_coords, selected_emotion)
            
            if audio_file_path:
                st.success("✅ 멜로디 생성 완료!")
                st.markdown("---")
                st.markdown(analysis_result)
                st.markdown("---")
                try:
                    audio_bytes = open(audio_file_path, 'rb').read()
                    st.audio(audio_bytes, format='audio/wav')
                except FileNotFoundError:
                    st.error("오디오 재생 실패")
            else:
                st.error(f"❌ 생성 실패: {analysis_result}")
        else:
            st.warning("⚠️ 캔버스에 선이 인식되지 않았습니다.")
    else:
        st.warning("⚠️ 캔버스 데이터를 인식할 수 없습니다.")
