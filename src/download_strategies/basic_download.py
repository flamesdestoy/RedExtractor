from .downloading_strategy import DownloadingStrategy
from utils.media_object_class import MediaObject
from utils.download_helper import download_media

class SimpleDownload(DownloadingStrategy):

    def __init__(self) -> None:
        super().__init__()

        # setting up the downloading parameters
        self.strategy_settings = {
            "format": "bestvideo+bestaudio/best",  # Download best video and audio
            "no_color": True,
            "noplaylist": True,  # Disable playlist extraction if not needed
            "skip_download": False,  # Ensure that downloading is not skipped
            "no_warnings": True,  # Suppress warnings to speed up execution
            "no_call_home": True,  # Disable sending usage statistics
            "source_address": None,  # Optionally bind to a specific IP address
        }
    
    def __str__(self) -> None:
        return "YTD Lp simple download strategy."
    
    def download(self, media_object: MediaObject, throttle_rate="700M"):

        url = media_object.url
        output_path = media_object.output_path

        # Define the parameter for yt-dlp
        
        # Save with title and extension
        self.strategy_settings["outtmpl"] = f"{output_path}/%(title)s.%(ext)s"
        
        # Set throttling rate (1 megabit per second)
        self.strategy_settings["throttled_rate"] = throttle_rate
        
        # Download the video using yt-dlp
        download_media(url, self.strategy_settings)

                
