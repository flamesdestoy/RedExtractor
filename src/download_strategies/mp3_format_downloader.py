from .downloading_strategy import DownloadingStrategy
from src.utils.media_object_class import MediaObject
from src.utils.download_helper import download_media

class MP3Download(DownloadingStrategy):

    def __init__(self) -> None:
        super().__init__()

        # setting up the downloading parameters
        self.strategy_settings = {
            "postprocessors": [{
                "key": "FFmpegExtractAudio",  # Extract audio
                "preferredcodec": "mp3",       # Convert to MP3
                "preferredquality": "192",     # Bitrate (192kbps)
            }],
            "quiet": True,  # Suppress non-error logs
        }
    
    def __str__(self) -> None:
        return "YTD Lp simple download strategy."
    
    def download(self, media_object: MediaObject):

        # Prioritize specified format/ Output template
        self.strategy_settings["format"] = f"{media_object.format_id}/bestaudio/best"
        self.strategy_settings["outtmpl"] = f"{media_object.output_path}/%(title)s.%(ext)s"
        
        # Download the mp3 file
        download_media(media_object.url, self.strategy_settings)
        