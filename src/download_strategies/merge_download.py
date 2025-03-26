import asyncio

from .downloading_strategy import DownloadingStrategy
from utils.media_object_class import MediaObject
from utils.merge_download_helper import download_media_separately
from utils.logger import logger


class MergingDownload(DownloadingStrategy):

    def __init__(self) -> None:
        super().__init__()

    def download(self, media_object: MediaObject):
        
        # Async entry point
        async def download():
            result = await download_media_separately(
                media_object,
                video_format=media_object.format_id,
                audio_format="bestaudio[ext=m4a]"
            )
            logger.info(f" * {f"Successfully downloaded to {result}" if result else "Download failed"}")

        asyncio.run(download())
