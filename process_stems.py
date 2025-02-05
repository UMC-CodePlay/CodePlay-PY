import soundfile as sf
import pyrubberband as pyrb
import numpy as np
import os
from pydub import AudioSegment
import io

def save_audio(y, sr, output_path):
    """오디오 저장 (WAV -> MP3 변환 포함)"""
    # 임시 WAV 파일로 저장
    temp_wav = io.BytesIO()
    sf.write(temp_wav, y, sr, format='WAV')
    temp_wav.seek(0)
    
    # WAV를 MP3로 변환
    audio_segment = AudioSegment.from_wav(temp_wav)
    audio_segment.export(output_path, format='mp3')

def process_audio(input_path, output_path, effect_type, value=None):
    """오디오 파일 처리"""
    print(f"\n{input_path} 처리 중...")
    
    # 오디오 파일 로드
    y, sr = sf.read(input_path)
    
    # 스테레오를 모노로 변환 (필요한 경우)
    if len(y.shape) > 1:
        y = y.mean(axis=1)
    
    # 효과 적용
    if effect_type == 1:  # 템포 변경
        print(f"템포 변경 (비율: {value})")
        y = pyrb.time_stretch(y, sr, value)
    
    elif effect_type == 2:  # 피치 변경
        print(f"피치 변경 ({value} 반음)")
        y = pyrb.pitch_shift(y, sr, value)
    
    elif effect_type == 3:  # 코러스 효과
        print("코러스 효과 추가")
        delay_samples1 = int(0.03 * sr)  # 30ms
        delay_samples2 = int(0.06 * sr)  # 60ms
        
        chorus1 = np.pad(y, (delay_samples1, 0))[:-delay_samples1]
        chorus2 = np.pad(y, (delay_samples2, 0))[:-delay_samples2]
        
        y = y + 0.5 * chorus1 + 0.5 * chorus2
        y = y / np.max(np.abs(y))

    elif effect_type == 4:  # 공간감 효과
        print(f"공간감 추가 (mix: {value})")
        # 여러 개의 짧은 딜레이로 공간감 생성
        delays = [15, 30, 45]  # ms
        decays = [0.3, 0.2, 0.1]  # 각 딜레이의 감쇠율
        
        y_reverb = np.zeros_like(y)
        for delay_ms, decay in zip(delays, decays):
            delay_samples = int(delay_ms * sr / 1000)
            delayed = np.pad(y, (delay_samples, 0))[:-delay_samples]
            y_reverb += delayed * decay
        
        # 원본과 공간감 효과 믹스 (value는 0.0 ~ 1.0 사이)
        y = (1 - value) * y + value * y_reverb
        y = y / np.max(np.abs(y))  # 노멀라이즈
    
    # 결과 저장
    save_audio(y, sr, output_path)
    print(f"처리된 파일이 {output_path}에 저장되었습니다.")
    return output_path

def get_effect_value(effect_type):
    """효과에 따른 값 입력 받기"""
    if effect_type == 1:
        while True:
            try:
                value = float(input("템포 변경 비율을 입력하세요 (1.0=원본, 0.5=2배 느리게, 2.0=2배 빠르게): "))
                if 0.1 <= value <= 4.0:
                    return value
                print("0.1에서 4.0 사이의 값을 입력해주세요.")
            except ValueError:
                print("올바른 숫자를 입력해주세요.")
    
    elif effect_type == 2:
        while True:
            try:
                value = int(input("변경할 피치를 입력하세요 (반음 단위, -12 ~ +12): "))
                if -12 <= value <= 12:
                    return value
                print("-12에서 +12 사이의 값을 입력해주세요.")
            except ValueError:
                print("올바른 숫자를 입력해주세요.")
    
    elif effect_type == 3:
        return True  # 코러스 효과는 항상 적용

    elif effect_type == 4:
        while True:
            try:
                value = float(input("공간감의 강도를 입력하세요 (0.0=원본, 1.0=최대, 권장:0.1~0.3): "))
                if 0.0 <= value <= 1.0:
                    return value
                print("0.0에서 1.0 사이의 값을 입력해주세요.")
            except ValueError:
                print("올바른 숫자를 입력해주세요.")

def apply_effect(input_file):
    """효과 선택 및 적용"""
    print("\n적용할 효과를 선택하세요:")
    print("1. 템포 변경")
    print("2. 피치 변경")
    print("3. 코러스 추가")
    print("4. 공간감 추가")
    print("5. 완료")
    
    while True:
        try:
            effect = int(input("선택 (1-5): "))
            if 1 <= effect <= 5:
                break
            print("1에서 5 사이의 숫자를 입력해주세요.")
        except ValueError:
            print("숫자를 입력해주세요.")
    
    if effect == 5:
        return None
    
    # 효과 값 입력 받기
    value = get_effect_value(effect)
    
    # 출력 파일명 생성
    effect_names = {1: 'tempo', 2: 'pitch', 3: 'chorus', 4: 'space'}
    name, ext = os.path.splitext(input_file)
    if '/' in name:  # 경로에서 파일명만 추출
        name = name.split('/')[-1]
    output_path = os.path.join('processed', f"{name}_{effect_names[effect]}{ext}")
    
    # 오디오 처리
    return process_audio(input_file, output_path, effect, value)

def process_stems():
    """사용자 입력을 받아 스템 처리"""
    # 출력 디렉토리 생성
    os.makedirs('processed', exist_ok=True)
    
    # 파일 선택
    while True:
        try:
            file_name = input("\n처리할 파일명을 입력하세요: ")
            if os.path.exists(file_name):
                break
            print("파일을 찾을 수 없습니다. 정확한 파일명을 입력해주세요.")
        except Exception as e:
            print(f"오류 발생: {e}")
    
    # 첫 번째 효과 적용
    current_file = file_name
    processed_file = apply_effect(current_file)
    
    # 추가 효과 적용
    while processed_file:
        current_file = processed_file
        processed_file = apply_effect(current_file)

if __name__ == "__main__":
    process_stems() 