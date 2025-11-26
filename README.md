# Melody Canvas

### **프로젝트 개요**
캔버스에 그림을 그리면 선을 분석하여 멜로디를 생성하는 프로그램입니다. 사용자가 그린 선의 길이, 위치, 복잡도와 사용자가 선택한 감정을 바탕으로 멜로디를 생성한다.

### **실행 방법**
1. 설치
   ```
   $ pip install streamlit numpy scipy streamlit-drawable-canvas
   ```
   이 repository에 있는 melody_canvas.py 파일 다운로드
2. 실행
   ```
   $ streamlit run melody_canvas.py
   ```
3. 웹 브라우저에서 자동 실행
   ```
   http://localhost:8501/
   ```

## **Melody Canvas 기능 설명**
### 감정 선택 기능
사용자가 곡의 분위기를 나타낼 감정을 선택하면 그에 맞는 기준 옥타브와 기준 템포를 결정합니다.
+ 기쁨 (Joy): 4옥타브, 0.5초
+ 희망 (Hope): 4옥타브, 0.8초
+ 평온 (Serene): 3옥타브, 1.5초
+ 분노 (Angry): 3옥타브, 0.4초
+ 격렬 (Intense): 4옥타브, 0.5초
+ 슬픔 (Sorrow): 2옥타브, 2초
+ 불안 (Anxious): 3옥타브, 0.7초
  
### 멜로디 생성 기능
캔버스에 그림을 그리면 선의 특징을 분석하여 멜로디를 생성합니다.
+ 선의 길이: 50픽셀당 음표 하나 생성
+ 선의 x좌표: 사용할 음(도-레-미-파-솔-라-시) 결정
+ 선의 y좌표: 사용할 옥타브(0옥타브-3옥타브) 결정
+ 선의 복잡도: 사용할 음계(5음계, 7음계, 12음계) 결정
  
### 멜로디 믹싱 기능
여러 개의 선들의 멜로디들을 하나로 믹싱하여 최종 멜로디를 WAV 파일로 생성합니다.

### 주요 함수 설명
```
generate_note_wave(freq, duration)
```
주파수와 음표 길이를 매개변수로 받아서 사인파 오디오 데이터를 생성하는 함수
   * 최종 음표 길이: 기본 길이(0.3초) x 선 길이에 따른 음표 길이 x 감정의 기준 템포
```
note_to_freq(note)
```
음표를 나타낸 문자열(예: c#4)을 매개변수로 받아서 실제 주파수로 변환하는 함수
   * 최종 옥타브: 감정의 기준 옥타브 + y좌표에 따른 옥타브
   * 주파수: 사용할 음의 주파수 x 2^최종 옥타브
```
generate_voice_melody(path_coords, params)
```
하나의 선을 분석하여 하나의 멜로디를 생성하는 함수
```
analyze_and_compose_polyphony(all_paths, selected_emotion)
```
여러 개의 선의 각각의 멜로디의 길이를 맞추고 볼륨을 정규화한 뒤 WAV 파일을 생성하는 함수

## UI 구성요소
+ 멜로디 생성 규칙 확인칸
+ 감정 선택창
+ 선 색깔 변경칸
+ 캔버스
+ 멜로디 생성 버튼
+ 결과 분석 텍스트 출력
+ WAV 오디오 재생

## **결과 화면**
### 메인 화면
![Drawing to Song 🎶](https://github.com/user-attachments/assets/9fd89d38-a8ff-413a-867d-4bd4622c3fd4)

### 실행 화면
![Drawing to Song2 🎶](https://github.com/user-attachments/assets/eff67870-e783-4f3b-8593-452dd853a145)

## 라이센스
MIT License

## 참고 자료
+ 웹 프레임워크: streamlit
+ 캔버스 드로잉 기능: stermalit-drawable-canvas
+ 수치 계산 및 배열 처리: NumPy
+ WAV 파일 입출력 및 신호처리: SciPy
