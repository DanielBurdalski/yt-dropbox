import os
import sys
import subprocess

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

def split_file(file_path, max_size=1.7 * 1024 * 1024 * 1024):
    file_size = get_file_size(file_path)
    video_duration = get_video_duration(file_path)
    part_duration = video_duration / (file_size / max_size)

    if file_size <= max_size:
        print(f"The file is smaller than {max_size} bytes, no need to split.")
        return
    
    part = 1
    start_time = 0
    output_files = []

    while start_time < video_duration:
        output_file = f"{os.path.splitext(file_path)[0]}_part{part}.mp4"
        cmd = [
            'ffmpeg',
            '-i', file_path,
            '-ss', str(start_time),
            '-t', str(part_duration),
            '-c', 'copy',
            output_file
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output_files.append(output_file)
        start_time += part_duration
        part += 1

    return output_files

def main(file_path):
    output_files = split_file(file_path)
    if output_files:
        print("Generated files and their sizes:")
        for output_file in output_files:
            size = get_file_size(output_file)
            print(f"{output_file}: {human_readable_size(size)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python split_mp4.py <path_to_mp4_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    main(file_path)
