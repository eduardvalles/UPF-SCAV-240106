# Construir la imagen Docker:
cd "your_git_clone_path"
docker-compose build
docker-compose up

## 1. Video transcoder

# Open Git Bash, go to the video directory to transcode the video
# You can change the file name and the output format

curl -X POST \
  -F "file=@input.mp4" \
  -F "format=vp8" \
  http://127.0.0.1:8000/transcode
  
 
 ## 2. transcoder
 
 # We create another python function to generate different versions of a video, with different resolution and bitrate.
 # The Ladder was created in main.py with some examples.
