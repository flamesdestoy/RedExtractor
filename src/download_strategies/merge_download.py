import asyncio

from .downloading_strategy import DownloadingStrategy
from src.utils.media_object_class import MediaObject
from src.utils.merge_download_helper import download_media_separately
from src.utils.logger import logger


class MergingDownload(DownloadingStrategy):

    def __init__(self) -> None:
        super().__init__()

    def download(self, media_object: MediaObject):
        
        # Async entry point
        async def download():
            result = await download_media_separately(
                media_object.url,
                media_object.output_path,
                video_format=media_object.format_id,
                audio_format="bestaudio[ext=m4a]"
            )
            logger.info(f"Download {'succeeded' if result else 'failed'}")

        asyncio.run(download())
