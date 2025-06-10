
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Callable
from queue import Queue, Empty
import threading
import time
import json

from download_strategies.downloading_strategy import DownloadingStrategy
from utils.media_object_class import MediaObject
from utils.progress_tracking import DownloadProgressTracker, message_queue
from utils.logger import logger

class DownloadManager:
    def __init__(self, 
                 download_strategy: Optional[DownloadingStrategy] = None, 
                 consumer_callable: Callable = None,
                 max_workers: int = 1) -> None:
        self.download_strategy = download_strategy
        self.max_workers = max_workers
        self.download_queue = Queue()
        self.progress_tracker = DownloadProgressTracker(consumer_callable)

    def set_downloading_strategy(self, download_strategy: DownloadingStrategy) -> None:
        self.download_strategy = download_strategy
        logger.info(f"Download strategy set to: {download_strategy.__class__.__name__}")
    
    def set_max_threads(self, max_workers: int) -> None:
        self.max_workers = max_workers

    def enqueue_object(self, object: MediaObject) -> None:
        self.download_queue.put(object)

    def _process_queue(self):
        while not self.download_queue.empty():
            try:
                media_object = self.download_queue.get_nowait()
                self._execute_download(media_object)
                self.download_queue.task_done()
            except Empty:
                break
    
    def _execute_download(self, object: MediaObject) -> None:
        if not self.download_strategy:
            raise TypeError("Set the download strategy first!")
        
        start_time = time.time()
        self.download_strategy.download(object, self.progress_tracker.progress_hook)
        end_time = time.time()
        logger.info(f"\nTotal downloading Time for {object.url}: {end_time - start_time}")

    def start_download(self):
        # Use ThreadPoolExecutor to process 2 videos at a time
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self._process_queue) for _ in range(self.max_workers)]
            for future in futures:
                future.result()

        message_queue.shutdown()  # Close the queue after download finishes

    def get_download_status(self) -> Dict:
        return self.progress_tracker.get_status()
