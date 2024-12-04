import ffmpeg
import cv2
import numpy as np
import tempfile
from fastapi import UploadFile
from typing import Tuple

def resize_video(input_path, output_path, new_width, new_height):
    # Use ffmpeg to resize the video
    ffmpeg.input(input_path).filter('scale', new_width, new_height).output(output_path).run(overwrite_output=True)

def modify_chroma_subsampling(input_path, output_path):

    print("Write '1' to select 4:4:4")
    print("Write '2' to select 4:2:2")
    print("Write '3' to select 4:2:0")
    subsampling = input("Select the pixel format:")

    if subsampling == 1:
        ffmpeg.input(input_path).output(output_path, c='libx264', vf=f'format={'yuv444p'}').run(overwrite_output=True)
    elif subsampling == 2:
        ffmpeg.input(input_path).output(output_path, c='libx264', vf=f'format={'yuv422p'}').run(overwrite_output=True)
    elif subsampling == 3:
        ffmpeg.input(input_path).output(output_path, c='libx264', vf=f'format={'yuv420p'}').run(overwrite_output=True)
    else:
        print("Invalid format. Using default 'yuv420p'.")
        ffmpeg.input(input_path).output(output_path, c='libx264', vf=f'format={'yuv420p'}').run(overwrite_output=True)



def get_video_info(video_path):

    # Use ffmpeg to probe video metadata
    probe = ffmpeg.probe(video_path)
    video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')

    # Data
    info = {"duration": float(probe['format']['duration']), "bit_rate": int(probe['format']['bit_rate']), "width": int(video_info['width']), "height": int(video_info['height']), "codec": video_info['codec_name']}
    
    return info

def process_bbb(input_path, output_path):
    # Cut video to 20 seconds
    ffmpeg.input(input_path, ss=0, t=20).output("/tmp/temp_video.mp4").run(overwrite_output=True)

    try:
        # Export audio as AAC mono
        ffmpeg.input("/tmp/audio_aac.m4a").output("/tmp/audio_aac.m4a", acodec="aac", ac=1).run(overwrite_output=True, capture_stdout=True, capture_stderr=True)

        # Export audio as MP3 stereo with lower bitrate
        ffmpeg.input("/tmp/temp_video.mp4").output("/tmp/audio_mp3.mp3", acodec="libmp3lame", ac=2, ab="128k").run(overwrite_output=True)

        # Export audio as AC3 codec
        ffmpeg.input("/tmp/temp_video.mp4").output("/tmp/audio_ac3.ac3", acodec="ac3").run(overwrite_output=True)

        # Package everything into a single .mp4
        ffmpeg.input("temp_video.mp4").output(output_path, acodec="aac", vcodec="copy").run(overwrite_output=True)

        return output_path
    
    except ffmpeg.Error as e:
        print("stdout:", e.stdout.decode('utf-8'))
        print("stderr:", e.stderr.decode('utf-8'))
        raise


def generate_yuv_histogram_video(file: UploadFile) -> str:
    """
    Generate a YUV histogram video from the given MP4 file.
    """
    # Create a temporary file to store the output video
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp_file_name = temp_file.name
    temp_file.close()

    cap = cv2.VideoCapture(file.file)

    # Video parameters
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4
    out = cv2.VideoWriter(temp_file_name, fourcc, fps, (width, height))

    while cap.isOpened():
        frame = cap.read()
        
        # Convert frame to YUV
        yuv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)

        # Calculate the histograms for Y, U, V channels
        hist_y = cv2.calcHist([yuv_frame], [0], None, [256], [0, 256])
        hist_u = cv2.calcHist([yuv_frame], [1], None, [256], [0, 256])
        hist_v = cv2.calcHist([yuv_frame], [2], None, [256], [0, 256])

        # Normalize the histograms
        hist_y = cv2.normalize(hist_y, None, alpha=0, beta=height, norm_type=cv2.NORM_MINMAX)
        hist_u = cv2.normalize(hist_u, None, alpha=0, beta=height, norm_type=cv2.NORM_MINMAX)
        hist_v = cv2.normalize(hist_v, None, alpha=0, beta=height, norm_type=cv2.NORM_MINMAX)

        # Create an empty frame for histogram
        hist_frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Draw the Y histogram
        for i in range(1, 256):
            cv2.line(hist_frame, (i-1, height - int(hist_y[i-1])), (i, height - int(hist_y[i])), (255, 0, 0), 2)

        # Draw the U histogram in green
        for i in range(1, 256):
            cv2.line(hist_frame, (i-1, height - int(hist_u[i-1])), (i, height - int(hist_u[i])), (0, 255, 0), 2)

        # Draw the V histogram in blue
        for i in range(1, 256):
            cv2.line(hist_frame, (i-1, height - int(hist_v[i-1])), (i, height - int(hist_v[i])), (0, 0, 255), 2)

        # Write the histogram frame to the output video
        out.write(hist_frame)

    # Release resources
    cap.release()
    out.release()

    return temp_file_name








