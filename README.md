# Melody Canvas

+ **프로젝트 개요**
캔버스에 그림을 그리면 선을 분석하여 멜로디를 생성하는 프로그램입니다.

+ 결과 화면

+ **실행 방법**
1. 설치
  ```
  pip install streamlit numpy scipy streamlit-drawable-canvas
  ```
2. 실행
  ```
 streamlit run melody_canvas.py
  ```
3. 웹 브라우저에서 자동 실행
  ```
  http://localhost:8501/
  ```

+ **주요 기능**
1. 사용자가 곡의 분위기를 나타낼 감정을 선택하여 그에 맞는 옥타브와 템포를 결정합니다.
2. 캔버스에 그림을 그리면 선의 특징을 분석하여 멜로디를 생성합니다.
   
   선의 길이: 한 음표의 길이
   선의 x좌표/y좌표 위치: 계이름/옥타브 결정
   선의 복잡도: 사용할 음계
3. 여러 개의 선들의 멜로디들을 하나로 믹싱하여 최종 멜로디를 WAV 파일로 생성합니다.
   선들의 멜로디의 길이를 맞춘 뒤 믹싱

+ **주요 함수 설명**
generate_note_wave(freq, duration)
  주파수와 지속 시간을 매개변수로 받아서 사인파 오디오 데이터를 생성하는 함수

note_to_freq(note)
  
