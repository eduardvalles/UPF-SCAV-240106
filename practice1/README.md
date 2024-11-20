# Construir la imagen Docker:
cd "your_git_clone_path"
docker-compose build
docker-compose up

# Endpoint 1: Resize image:
# Open Git Bash and go to the image directory to resize the image.png
# You can change the parameters "width" and "height" and the name/format of the image
curl -X POST "http://localhost:8000/resize-image/" \
-H "accept: image/png" \
-F "file=@image.png" \
-F "width=50" \
-F "height=70" \
-o resized_image.png

# Endpoint 2: Run Length Encoding:
# Open Git Bash and insert the code to execute Run Length Encoding
# You can change the proposed data
curl -X POST "http://localhost:8000/run-length-encoding/" \
-H "accept: application/json" \
-H "Content-Type: application/json" \
-d "{\"data\": [7,7,7,8,9,9,9,9,9,1,2,3,4,4,4,5,6,6,7,7,8,9,0,0,0]}"

