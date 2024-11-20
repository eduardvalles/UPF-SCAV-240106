from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from utils.image_processing import resize_image, runLengthEncoding
import numpy as np
from typing import List
import shutil
from PIL import Image
import io
from pydantic import BaseModel

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



