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

def split_file(file_path, target_size=1.85 * 1024 * 1024 * 1024):
    file_size = get_file_size(file_path)
    video_duration = get_video_duration(file_path)
    bitrate = get_bitrate(file_path)

    if file_size <= target_size:
        print(f"The file is smaller than {human_readable_size(target_size)}, no need to split.")
        return

    if bitrate is None:
        print(f"Could not determine the bitrate of the file '{file_path}'. Cannot split the file.")
        return

    # Calculate the target duration of each part based on the target size and bitrate
    target_duration = (target_size * 8) / bitrate

    part = 1
    start_time = 0
    output_files = []
    while start_time < video_duration:
        output_file = f"{os.path.splitext(file_path)[0]}_part{part}.mp4"
        end_time = min(start_time + target_duration, video_duration)

        cmd = [
            'ffmpeg',
            '-i', file_path,
            '-ss', str(start_time),
            '-to', str(end_time),
            '-c', 'copy',
            output_file
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        output_files.append(output_file)
        start_time = end_time
        part += 1

    if output_files:
        os.remove(file_path)
        print(f"Source file '{file_path}' has been removed.")

    return output_files

def main(file_paths):
    for file_path in file_paths:
        output_files = split_file(file_path)
        if output_files:
            print("Generated files and their sizes:")
            for output_file in output_files:
                size = get_file_size(output_file)
                print(f"{output_file}: {human_readable_size(size)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_paths = sys.argv[1:]
    else:
        files = glob('*.mp4')
        if not files:
            print("No MP4 files found in the current directory.")
            sys.exit(1)
        file_paths = files

    main(file_paths)
