# Construir la imagen Docker:
cd "your_git_clone_path"
docker-compose build
docker-compose up

## 1. Resize video with FFMPEG:

# Open Git Bash, go to the Big Buck Bunny directory to resize the video and run the code

curl -X POST "http://localhost:8000/resize-image/" \
-F "file=@big_buck_bunny.mp4" \
-F "width=640" \
-F "height=360" \
--output resized_big_buck_bunny.mp4

## 3. Video Info Endpoint:

# Open Git Bash, go to the Big Buck Bunny directory and run the code:
curl -X POST "http://127.0.0.1:8000/video-info/" \
  -H "accept: application/json" \
  -F "file=@big_buck_bunny.mp4"
  
# The terminal should print the following information:
{"filename":"big_buck_bunny.mp4","video_info":{"duration":634.624,"bit_rate":937
1238,"width":3840,"height":2160,"codec":"av1"}}


## 4. BBB Container:

# Open Git Bash, go to the Big Buck Bunny directory and run the code:

curl -X POST "http://127.0.0.1:8000/process-bbb/" \
  -H "accept: video/mp4" \
  -F "file=@big_buck_bunny.mp4" \
  --output big_buck_bunny_processed.mp4
  

## 7. YUV Histogram

# Open Git Bash, go to the video directory to resize the video and run the code:

curl -X POST "http://127.0.0.1:8000/generate_yuv_histogram/" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@big_buck_bunny.mp4" \
     --output yuv_histogram.mp4




