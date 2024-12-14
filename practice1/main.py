from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from utils.image_processing import resize_image, runLengthEncoding
from utils.video_processing import resize_video, modify_chroma_subsampling, get_video_info, process_bbb, generate_yuv_histogram_video
from utils.transcoding import transcode_video, transcoder
import numpy as np
from typing import List
import shutil
from PIL import Image
import io
import os
from pydantic import BaseModel
from pymediainfo import MediaInfo

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Bienvenido a mi aplicación FastAPI"}


@app.post("/resize-image/")
async def resize_image_endpoint(
    file: UploadFile = File(...),
    width: int = Form(...),
    height: int = Form(...)
):
    # Leer la imagen cargada
    image = Image.open(io.BytesIO(await file.read()))  

    # DEBUG: Confirmación de parámetros y tipo de imagen
    print(f"Resizing image: {file.filename} to width={width}, height={height}")
    
    # Redimensionar la imagen
    resized_image = resize_image(image, width, height)

    # Abrir la imagen redimensionada
    with open(resized_image, "rb") as f:
        resized_image = f.read()

    return StreamingResponse(io.BytesIO(resized_image), media_type="image/png")

class DataModel(BaseModel):
    data: List[int]  # Expecting a list of integers


@app.post("/run-length-encoding/")
async def run_length_encoding_endpoint(input_data: DataModel):
    # Extract data from the request
    data = input_data.data
    
    # Process the data with runLengthEncoding
    encoded_data = runLengthEncoding(data)
    
    # Debugging message
    print(f"Input data: {data}")
    print(f"Encoded data: {encoded_data}")

    return {"encoded_data": encoded_data}


@app.post("/resize-video/")
async def resize_video_endpoint(
    file: UploadFile = File(...),
    width: int = Form(...),
    height: int = Form(...)
):
    # Create a temporary path for the uploaded video
    input_video_path = "/tmp/input_video.mp4"
    output_video_path = "/tmp/resized_video.mp4"

    # Save the uploaded video to a temporary file
    with open(input_video_path, "wb") as f:
        f.write(await file.read())

    # Resize the video using the helper function
    resize_video(input_video_path, output_video_path, width, height)

    # Read the resized video to return as a response
    with open(output_video_path, "rb") as f:
        resized_video = f.read()

    # Clean up temporary files
    os.remove(input_video_path)
    os.remove(output_video_path)

    return StreamingResponse(io.BytesIO(resized_video), media_type="video/mp4")


@app.post("/modify-chroma-subsampling/")
async def modify_chroma_subsampling_endpoint(
    file: UploadFile = File(...), 
    subsampling: int = 1,  # Default to 1 for yuv444p
    output_filename: str = "output_video.mp4"
):
    # Save the uploaded file
    input_path = "/tmp/" + file.filename
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Set output path
    output_path = "/tmp/" + output_filename
    
    # Call your existing function
    modify_chroma_subsampling(input_path, output_path, subsampling)

    # Clean up input file
    os.remove(input_path)

    # Prepare the output file for streaming
    return StreamingResponse(open(output_path, "rb"), media_type="video/mp4")


app = FastAPI()

@app.post("/video-info/")
async def video_info(file: UploadFile = File(...)):
    """
    Endpoint to read video information and return relevant details.
    """
    # Save the uploaded file temporarily
    temp_file = f"/tmp/{file.filename}"
    with open(temp_file, "wb") as f:
        f.write(await file.read())

    # Extract video information
    try:
        info = get_video_info(temp_file)
    except ValueError as e:
        return {"error": str(e)}

    return {
        "filename": file.filename,
        "video_info": info
    }


@app.post("/process-bbb/")
async def process_bbb_endpoint(file: UploadFile = File(...)):
    # Save uploaded video to a temporary path
    input_path = f"/tmp/{file.filename}"
    output_path = "/tmp/bbb_processed.mp4"

    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Process the video
    process_bbb(input_path, output_path)

    # Return the processed video
    return FileResponse(output_path, media_type="video/mp4", filename="big_buck_bunny_processed.mp4")


@app.post("/count_tracks/")
async def count_tracks(file: UploadFile):
    """
    Endpoint to count the number of tracks in an uploaded MP4 file.
    """
    if not file.filename.endswith(".mp4"):
        raise HTTPException(status_code=400, detail="Only MP4 files are supported.")

    try:
        # Save the uploaded file temporarily
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(await file.read())

        # Read the media info
        media_info = MediaInfo.parse(temp_file_path)
        track_count = len(media_info.tracks)

        # Clean up the temporary file
        os.remove(temp_file_path)

        return {"file_name": file.filename, "track_count": track_count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    

@app.post("/generate_yuv_histogram/")
async def generate_yuv_histogram(file: UploadFile = File(...)):
    if file.content_type != 'video/mp4':
        return {"detail": "Only MP4 files are supported."}
    
    # Generate YUV histogram video
    output_video_path = generate_yuv_histogram_video(file)
    
    # Return the generated video file
    return FileResponse(output_video_path, media_type='video/mp4', filename=os.path.basename(output_video_path))


@app.post("/transcode")
async def transcode_endpoint(
    file: UploadFile = File(...),
    format: str = Form(...)
):
    """
    Endpoint per transcodificar un vídeo a formats especificats.
    """
    valid_formats = ['vp8', 'vp9', 'h265', 'av1']

    if format not in valid_formats:
        raise HTTPException(status_code=400, detail="Format no suportat")

    # Desa el fitxer temporalment
    temp_input_file = f"./temp_{file.filename}"
    with open(temp_input_file, "wb") as temp_file:
        temp_file.write(await file.read())

    try:
        # Transcodifica el fitxer
        output_file_path = transcode_video(temp_input_file, format)
        return {"message": "Transcodificació completada", "output_file": output_file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la transcodificació: {str(e)}")
    finally:
        # Elimina el fitxer temporal
        if os.path.exists(temp_input_file):
            os.remove(temp_input_file)


ENCODING_LADDER = [
    {"resolution": "1080p", "bitrate": "5000k", "format": "h265"},
    {"resolution": "720p", "bitrate": "2800k", "format": "h265"},
    {"resolution": "480p", "bitrate": "1200k", "format": "h265"},
]

@app.post("/encoding-ladder")
async def encoding_ladder_endpoint(file: UploadFile = File(...)):
    # Desa el fitxer d'entrada temporalment
    temp_input_file = f"./temp_{file.filename}"
    with open(temp_input_file, "wb") as temp_file:
        temp_file.write(await file.read())

    output_files = []
    try:
        # Genera una versió per cada configuració de l'encoding ladder
        for step in ENCODING_LADDER:
            output_file = transcoder(input_path=temp_input_file, format=step["format"], resolution=step["resolution"], bitrate=step["bitrate"])
            output_files.append(output_file)

        return {
            "message": "Encoding ladder generat correctament",
            "output_files": output_files
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en l'encoding ladder: {str(error)}")

    finally:
        # Elimina el fitxer temporal
        if os.path.exists(temp_input_file):
            os.remove(temp_input_file)




