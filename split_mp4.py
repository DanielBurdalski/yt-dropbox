import os
import sys
import subprocess
from glob import glob

def get_file_size(file_path):
    return os.path.getsize(file_path)

def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.{decimal_places}f} {unit}"
        size /= 1024

def get_video_duration(file_path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return float(result.stdout)

def get_bitrate(file_path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=bit_rate', '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    output = result.stdout.decode().strip()
    if output == 'N/A':
        return None
    else:
        return float(output)

def split_file(file_path, target_size=1.85 * 1024 * 1024 * 1024, tolerance=0.05 * 1024 * 1024 * 1024):
    # Rest of the split_file function remains the same
    # ...

def main():
    files = glob('*.mp4')
    if not files:
        print("No MP4 files found in the current directory.")
        return

    if len(files) > 1:
        print("Multiple MP4 files found in the current directory. Please specify the file to split.")
        for i, file in enumerate(files):
            print(f"{i+1}. {file}")
        choice = int(input("Enter the number of the file to split: "))
        file_path = files[choice-1]
    else:
        file_path = files[0]
        print(f"Splitting file: {file_path}")

    output_files = split_file(file_path)
    if output_files:
        print("Generated files and their sizes:")
        for output_file in output_files:
            size = get_file_size(output_file)
            print(f"{output_file}: {human_readable_size(size)}")

if __name__ == "__main__":
    main()
