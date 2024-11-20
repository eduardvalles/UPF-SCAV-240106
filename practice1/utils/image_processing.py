import numpy as np 
import io
import ffmpeg
from PIL import Image
import pywt
from scipy.fftpack import dct, idct

# Conversion Functions
def RGB_to_YUV(rgb):
    m = np.array([[0.29900, -0.16874, 0.50000], 
                  [0.58700, -0.33126, -0.41869], 
                  [0.11400, 0.50000, -0.08131]])
    yuv = np.dot(rgb, m)
    yuv[:, :, 1:] += 128.0
    return yuv

def YUV_to_RGB(yuv):
    m = np.array([[1.0, 1.0, 1.0], 
                  [-0.000007154783816076815, -0.3441331386566162, 1.7720025777816772], 
                  [1.4019975662231445, -0.7141380310058594, 0.00001542569043522235]])
    rgb = np.dot(yuv, m)
    rgb[:, :, 0] -= 179.45477266423404
    rgb[:, :, 1] += 135.45870971679688
    rgb[:, :, 2] -= 226.8183044444304
    return rgb

# Resize Image Function
def resize_image(input_image, width, height):
    img_byte_array = io.BytesIO()
    input_image.save(img_byte_array, format="PNG")
    img_byte_array.seek(0)  # Volver al principio del buffer

    resized_image = "/tmp/resized_image.png"  
    ffmpeg.input('pipe:0').output(resized_image, vf=f'scale={width}:{height}').run(input=img_byte_array.read(), overwrite_output=True)

    return resized_image 

# Serpentine Pattern Function
def serpentine(img):
    rows, cols = img.shape
    idx = 0
    arr = []
    output = np.zeros([rows, cols], int)

    arr.append(img[0, 0])

    for col in range(1, cols):
        i, j = 0, col
        while i < rows and j >= 0:
            arr.append(img[i, j])
            i += 1
            j -= 1

    for row in range(1, rows):
        i, j = row, 0
        while j < cols and i >= 0:
            arr.append(img[i, j])
            i -= 1
            j += 1

    # Matrix
    for row in range(rows):
        for col in range(cols):
            output[row, col] = arr[idx]
            idx += 1

    return output

# Run-Length Encoding
def runLengthEncoding(data):
    if not data:
        return []  # Handle edge case for empty input
    
    encoded = [data[0]]
    for i in range(len(data)):
        if i == 0 or data[i] != data[i - 1]:
            encoded.append(data[i])
    return encoded

# DCT Processor Class
class DCTProcessor:
    def __init__(self, type=2, norm='ortho'):
        self.type = type
        self.norm = norm

    def encode(self, data):
        if data.ndim == 1:
            return dct(data, type=self.type, norm=self.norm)
        elif data.ndim == 2:
            return dct(dct(data.T, type=self.type, norm=self.norm).T, type=self.type, norm=self.norm)
        else:
            raise ValueError("Data must be 1D or 2D.")

    def decode(self, transformed_data):
        if transformed_data.ndim == 1:
            return idct(transformed_data, type=self.type, norm=self.norm)
        elif transformed_data.ndim == 2:
            return idct(idct(transformed_data.T, type=self.type, norm=self.norm).T, type=self.type, norm=self.norm)
        else:
            raise ValueError("Data must be 1D or 2D.")

    def process(self, data):
        encoded_data = self.encode(data)
        decoded_data = self.decode(encoded_data)
        return data, encoded_data, decoded_data

# DWT Processor Class
class DWTProcessor:
    def __init__(self, wavelet='haar', level=1):
        self.wavelet = wavelet
        self.level = level

    def encode(self, data):
        if data.ndim == 1:
            coeffs = pywt.wavedec(data, wavelet=self.wavelet, level=self.level)
            return coeffs
        elif data.ndim == 2:
            coeffs = pywt.dwt2(data, wavelet=self.wavelet)
            return coeffs
        else:
            raise ValueError("Data must be 1D or 2D.")

    def decode(self, transformed_data):
        if isinstance(transformed_data, list):
            data = pywt.waverec(transformed_data, wavelet=self.wavelet)
            return data
        elif isinstance(transformed_data, tuple):
            data = pywt.idwt2(transformed_data, wavelet=self.wavelet)
            return data
        else:
            raise ValueError("Invalid transformed data format.")

    def process(self, data):
        encoded_data = self.encode(data)
        decoded_data = self.decode(encoded_data)
        return data, encoded_data, decoded_data
