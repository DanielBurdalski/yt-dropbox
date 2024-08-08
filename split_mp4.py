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
    file_size = get_file_size(file_path)
    video_duration = get_video_duration(file_path)
    bitrate = get_bitrate(file_path)
    
    if file_size <= target_size + tolerance:
        print(f"The file is smaller than {human_readable_size(target_size + tolerance)}, no need to split.")
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
        
        # Adjust the part duration to get the file size within the desired range
        adjusted_duration = target_duration
        while True:
            cmd = [
                'ffmpeg',
                '-i', file_path,
                '-ss', str(start_time),
                '-t', str(adjusted_duration),
                '-c', 'copy',
                output_file
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            part_size = get_file_size(output_file)
            
            if target_size - tolerance <= part_size <= target_size + tolerance or start_time + adjusted_duration >= video_duration:
                break
            else:
                adjusted_duration *= (target_size / part_size)
                os.remove(output_file)
        
        output_files.append(output_file)
        start_time += adjusted_duration
        part += 1
    # Remove the source file if splitting was successful
    if output_files:
        os.remove(file_path)
        print(f"Source file '{file_path}' has been removed.")
    
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
