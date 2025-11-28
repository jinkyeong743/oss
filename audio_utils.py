import numpy as np
from scipy.io.wavfile import write
from constants import SAMPLE_RATE, CANVAS_WIDTH, CANVAS_HEIGHT, MAX_EXPECTED_LENGTH
from constants import SCALE_PENTATONIC, SCALE_MAJOR, SCALE_CHROMATIC
from constants import SHARP_HIGH, SHARP_MID, EMOTION_PARAMETERS

# 특정 주파수와 특정 길이의 사인파 오디오 데이터 생성하는 함수
def generate_note_wave(note_freq, duration_seconds, amplitude=4096):
    t = np.linspace(0, duration_seconds, int(SAMPLE_RATE * duration_seconds), False)
    audio = amplitude * np.sin(note_freq * 2 * np.pi * t)
    return audio.astype(np.int16)

# 음표 문자열(예: c#4)을 실제 주파수로 변환하는 함수
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