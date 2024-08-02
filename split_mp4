import os
import sys
import subprocess

def get_file_size(file_path):
    return os.path.getsize(file_path)

def split_file(file_path, max_size=1.7 * 1024 * 1024 * 1024):
    file_size = get_file_size(file_path)
    if file_size <= max_size:
        print(f"The file is smaller than {max_size} bytes, no need to split.")
        return
    
    part = 1
    start_time = 0
    duration = 0
    
    while start_time < file_size:
        output_file = f"{os.path.splitext(file_path)[0]}_part{part}.mp4"
        cmd = [
            'ffmpeg',
            '-i', file_path,
            '-ss', str(start_time),
            '-t', str(max_size),
            '-c', 'copy',
            output_file
        ]
        subprocess.run(cmd)
        start_time += max_size
        part += 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python split_mp4.py <path_to_mp4_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    split_file(file_path)
