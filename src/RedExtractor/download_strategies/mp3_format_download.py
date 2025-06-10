from .downloading_strategy import DownloadingStrategy
from utils.media_object_class import MediaObject
from utils.download_helper import download_media

class MP3Download(DownloadingStrategy):

    def __init__(self) -> None:
        super().__init__()

        # setting up the downloading parameters
        self.download_settings.update({
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "extract_flat": False,  # Changed from True to properly process audio
            "force_generic_extractor": False,  # Let yt-dlp choose best extractor
            "socket_timeout": 30
        })
    
    def __str__(self) -> None:
        return "YTD Lp simple download strategy."
    
    def download(self, media_object: MediaObject):

        # Prioritize specified format/ Output template
        self.download_settings["format"] = f"bestaudio/bestaudio/best"
        outtmpl = f"{media_object.output_path}/{media_object.output_name or "%(title)s"}.%(ext)s"
        self.download_settings["outtmpl"] = outtmpl
        # self.download_settings["progress_hooks"] = [progress_hook] if progress_hook else None
        
        # Additional fixes for problematic videos
        if media_object.url.startswith(('https://youtube.com', 'https://www.youtube.com')):
            self.download_settings.update({
                'extract_flat': 'in_playlist',  # Special handling for YouTube
                'compat_opts': ['no-youtube-unavailable-videos'],
            })

        # Perform download
        download_media(media_object.url, self.download_settings)
