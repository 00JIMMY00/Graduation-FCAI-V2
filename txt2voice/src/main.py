
from gtts import gTTS
import tempfile
import os
import pathlib
import subprocess

def text_to_speech(text, lang='ar'):
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            temp_filename = f.name

        tts = gTTS(text=text, lang=lang)
        tts.save(temp_filename)
        
        # Use Windows native player for WSL paths
        if '/mnt/c/' in temp_filename:
            win_path = temp_filename.replace('/mnt/c/', 'C:\\').replace('/', '\\')
            subprocess.run(['cmd.exe', '/c', 'start', '/B', 'wmplayer.exe', win_path], check=True)
        else:
            subprocess.run(['mpg123', temp_filename], check=True)
            
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

def read_text_from_file(file_path):
    """Handle Windows-style paths in WSL"""
    if file_path.startswith('C:\\'):
        unix_path = file_path.replace('C:\\', '/mnt/c/').replace('\\', '/')
        return pathlib.Path(unix_path).read_text(encoding='utf-8')
    return pathlib.Path(file_path).read_text(encoding='utf-8')

if __name__ == "__main__":
    file_path = input("Enter the path to the text file: ").strip()
    
    try:
        print(f"Trying to access: {file_path}")
        text = read_text_from_file(file_path)
        text_to_speech(text)
    except Exception as e:
        print(f"Error: {e}")
