from pydantic import BaseModel

class ConvertAudioRequest(BaseModel):
    input_path: str
    output_path: str
    output_format: str = "mp3"

class DownloadVideoRequest(BaseModel):
    url: str
    output_dir: str = "./downloads"