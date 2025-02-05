from basic_pitch.inference import predict_and_save
import os
import shutil

def extract_midi(audio_path, output_path):
    """오디오 파일에서 MIDI 추출"""
    print(f"Converting {audio_path} to MIDI...")
    
    # 임시 디렉토리 생성
    temp_dir = 'temp_midi'
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Basic Pitch로 MIDI 예측 및 저장
        predict_and_save(
            audio_path_list=[audio_path],
            output_dir=temp_dir,
            save_midi=True,
            sonify_midi=False,
            min_note_length=0.05,
            min_frequency=30,
            max_frequency=1000,
            multiple_pitch_bends=False
        )
        
        # 생성된 MIDI 파일 찾기
        temp_midi = os.path.join(temp_dir, os.path.basename(audio_path).replace('.mp3', '_basic_pitch.mid'))
        
        # 최종 위치로 이동
        if os.path.exists(temp_midi):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            shutil.move(temp_midi, output_path)
            print(f"MIDI saved to {output_path}")
            return True
            
    except Exception as e:
        print(f"Error converting {audio_path}: {str(e)}")
        return False
        
    finally:
        # 임시 디렉토리 정리
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    return False

def process_all_stems(input_dir='separated', output_dir='midi_files'):
    """모든 스템 파일을 MIDI로 변환"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 처리할 파일 매핑
    stems = {
        'vocals.mp3': 'vocals.mid',
        'drums.mp3': 'drums.mid',
        'bass.mp3': 'bass.mid',
        'MR.mp3': 'mr.mid'
    }
    
    # 원본 파일도 처리
    original_path = 'test.mp3'
    if os.path.exists(original_path):
        output_path = os.path.join(output_dir, 'original.mid')
        success = extract_midi(original_path, output_path)
        if success:
            print(f"Original file converted successfully")
    
    # 각 스템 처리
    for input_file, output_file in stems.items():
        input_path = os.path.join(input_dir, input_file)
        if os.path.exists(input_path):
            output_path = os.path.join(output_dir, output_file)
            success = extract_midi(input_path, output_path)
            if success:
                print(f"{input_file} converted successfully")

if __name__ == "__main__":
    process_all_stems() 