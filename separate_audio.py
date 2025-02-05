# separate_audio.py

import os
import subprocess
from pydub import AudioSegment
import shutil  # 디렉토리 삭제를 위해 추가

def run_demucs(input_file, output_dir, model_name='htdemucs', stems=None):
    """
    Demucs를 사용하여 오디오 파일을 분리하는 함수.

    :param input_file: 분리할 오디오 파일 경로 (예: 'test.mp3')
    :param output_dir: 분리된 파일을 저장할 디렉토리 (예: 'separated')
    :param model_name: Demucs 모델 이름 (기본값: 'htdemucs')
    :param stems: 분리할 스템 옵션 ('two-stems' 또는 None)
    """
    # 기본 Demucs 명령어 설정
    demucs_command = [
        "demucs",
        input_file,
        "--out", output_dir,
        "-n", model_name
    ]

    # 2-stem 분리 옵션 추가
    if stems == 'two-stems':
        demucs_command += ["--two-stems", "vocals"]

    print(f"실행 명령어: {' '.join(demucs_command)}")
    try:
        # Demucs 실행
        subprocess.run(demucs_command, check=True)
        print(f"Demucs 분리 완료: {input_file} ({'2-stems' if stems == 'two-stems' else '4-stems'})")
    except subprocess.CalledProcessError as e:
        print(f"Demucs 실행 중 오류 발생 ({'2-stems' if stems == 'two-stems' else '4-stems'}): {e}")
        return False
    return True

def convert_wav_to_mp3(stem_dir, stems_mapping, output_dir):
    """
    WAV 파일을 MP3로 변환하고, 지정된 파일만 저장하는 함수.

    :param stem_dir: 분리된 WAV 파일들이 있는 디렉토리
    :param stems_mapping: 변환할 스템과 MP3 이름의 딕셔너리
    :param output_dir: 변환된 MP3 파일을 저장할 디렉토리
    """
    for stem, mp3_name in stems_mapping.items():
        wav_filename = f"{stem}.wav"
        wav_path = os.path.join(stem_dir, wav_filename)
        if not os.path.exists(wav_path):
            print(f"스템 파일을 찾을 수 없습니다: {wav_path}")
            continue

        mp3_path = os.path.join(output_dir, mp3_name)

        # WAV to MP3 변환
        try:
            print(f"{wav_filename}을(를) {mp3_name}으로 변환 중...")
            audio = AudioSegment.from_wav(wav_path)
            audio.export(mp3_path, format="mp3", bitrate="192k")
            print(f"{mp3_name} 변환 완료.")
        except Exception as e:
            print(f"{wav_filename}을(를) MP3로 변환 중 오류 발생: {e}")
            continue

    print("MP3 변환 작업이 완료되었습니다.")

def separate_audio(input_file, output_dir='separated', model_name='htdemucs'):
    """
    전체 오디오 분리 및 변환 과정을 수행하는 함수.

    :param input_file: 분리할 오디오 파일 경로 (예: 'test.mp3')
    :param output_dir: 분리된 파일을 저장할 디렉토리 (기본값: 'separated')
    :param model_name: Demucs 모델 이름 (기본값: 'htdemucs')
    """
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    file_base = os.path.splitext(os.path.basename(input_file))[0]

    # 2-stems 분리: 보컬과 MR
    success = run_demucs(input_file, output_dir, model_name=model_name, stems='two-stems')
    if success:
        stem_dir = os.path.join(output_dir, model_name, file_base)
        stems_mapping = {
            'vocals': 'vocals.mp3',
            'no_vocals': 'MR.mp3'
        }
        convert_wav_to_mp3(stem_dir, stems_mapping, output_dir)

    # 4-stems 분리: 보컬, 드럼, 베이스, MR
    success = run_demucs(input_file, output_dir, model_name=model_name, stems=None)
    if success:
        stem_dir = os.path.join(output_dir, model_name, file_base)
        stems_mapping = {
            'drums': 'drums.mp3',
            'bass': 'bass.mp3',
        }
        convert_wav_to_mp3(stem_dir, stems_mapping, output_dir)

    # 모든 MP3 변환이 완료된 후, 'separated' 디렉토리 내의 서브디렉토리들만 삭제
    try:
        print("모든 MP3 변환이 완료되었습니다. 'separated' 디렉토리 내의 서브디렉토리들을 삭제합니다...")
        # 'separated' 디렉토리 내의 모든 항목을 확인
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            # 항목이 디렉토리인 경우 삭제
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"디렉토리 삭제 완료: {item_path}")
        print("'separated' 디렉토리 내의 서브디렉토리 삭제 완료.")
    except Exception as e:
        print(f"'separated' 디렉토리 내의 서브디렉토리 삭제 중 오류 발생: {e}")

    print("모든 스템 변환 및 삭제 작업이 완료되었습니다.")

if __name__ == "__main__":
    separate_audio('test.mp3')
