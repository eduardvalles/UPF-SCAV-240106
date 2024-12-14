import ffmpeg
import os
import subprocess

def transcode_video(input_file: str, output_format: str):
    # base name of the input file
    name = os.path.splitext(os.path.basename(input_file))[0]
    
    codecs = {"vp8": "libvpx", "vp9": "libvpx-vp9", "h265": "libx265", "av1": "libaom-av1"}
    
    if output_format not in codecs:
        raise ValueError(f"Format no suportat: {output_format}")
    
    # output file path
    output_file = f"{name}_{output_format}.mp4"
    
    # Transcodificació
    try:
        (ffmpeg.input(input_file).output(output_file, vcodec=codecs[output_format], **get_codec_options(output_format)).run())
        print(f"Transcodificació completada: {output_file}")
    except ffmpeg.Error as error:
        print(f"Error en la transcodificació: {e.stderr.decode('utf-8')}")
        raise error
    
    return output_file



def get_codec_options(format: str):
    if format == "vp8" or format == "vp9":
        return {"b:v": "1M", "crf": 30}
    elif format == "h265":
        return {"preset": "medium", "crf": 28}
    elif format == "av1":
        return {"cpu-used": 4, "crf": 30}
    else:
        return {}
    

def transcoder(input_path, format, resolution=None, bitrate=None):
    """
    Transcodifica un fitxer de vídeo a un format específic amb resolució i bitrate opcional.
    """
    output_path = f"{os.path.splitext(input_path)[0]}_{resolution}_{format}.mp4"

    # Comanda ffmpeg
    ffmpeg_command = [
        "ffmpeg",
        "-i", input_path,
        "-c:v", format,
    ]
    
    # Afegim resolució si està especificada
    if resolution:
        ffmpeg_command.extend(["-vf", f"scale=-1:{resolution}"])
    
    # Afegim bitrate si està especificat
    if bitrate:
        ffmpeg_command.extend(["-b:v", bitrate])
    
    ffmpeg_command.append(output_path)

    # Executem ffmpeg
    process = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode != 0:
        raise Exception(f"Error en la transcodificació: {process.stderr.decode()}")

    return output_path

    