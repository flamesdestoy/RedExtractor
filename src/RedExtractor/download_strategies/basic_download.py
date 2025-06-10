from .downloading_strategy import DownloadingStrategy
from utils.media_object_class import MediaObject
from utils.download_helper import download_media

class SimpleDownload(DownloadingStrategy):

    def __init__(self) -> None:
        super().__init__()
    
    def __str__(self) -> None:
        return "YTD Lp simple download strategy."
    
    def download(self, media_object: MediaObject, progress_callback=None):
        
        outtmpl = f"{media_object.output_path}/{media_object.output_name or media_object.title}.%(ext)s"
        file_ext = media_object.file_format
        
        # set the ytdlp settings/options
        self.download_settings.update({
            "progress_hooks": [progress_callback] if progress_callback else [],
            "format": media_object.format_id,
            "outtmpl": outtmpl,
            "merge_output_format": file_ext,
        })

        # Download the video using yt-dlp
        download_media(media_object.url, self.download_settings)

                
