from enum import Enum, auto
from time import time
from typing import Callable
from pulsebus import (
    MessageTemplate,
    MessageBuilder,
    MessageQueue,
    MessagePool
)

class DownloadingState(Enum):
    """
    Enum to define the different states of video downloading.
    """
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    PAUSED = auto()

# Initialize the message template, message pool, message queue
progress_msg_template = (
    MessageBuilder()
        .add_field("url", "")
        .add_field("file_name", "")
        .add_field("progress", 0.0)
        .add_field("downloaded_bytes", 0)
        .add_field("file_size", 0)
        .add_field("download_speed", "")
        .add_field("ETA", 0)
        .add_field("status", DownloadingState.IN_PROGRESS)
        .add_field("timestamp", time())
        .build()
)

pool = MessagePool(template=progress_msg_template, max_size=10)
message_queue = MessageQueue()

class DownloadProgressTracker:
    def __init__(self, consumer_callable: Callable):
        self.consumer_logic_callable = consumer_callable
        self.status = {}
        message_queue.subscribe(self._handle_message)

    def progress_hook(self, d):
        """Update progress details."""
        # Producer, acquires a message store data in it pushes the message to the queue
        if d["status"] not in ("downloading", "finished"):
            return
        
        url = d.get("info_dict", {}).get("webpage_url") or d.get("url", "unknown")
        file_name = d.get("filename", "unknown")
        downloaded_bytes = d.get("downloaded_bytes", 0)
        total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
        progress = f"{( downloaded_bytes / total_bytes) * 100:.2f}%" if total_bytes else "N/A"
        raw_speed = d.get("speed")
        speed = f"{raw_speed / 1024:.2f} KB/s" if raw_speed else "N/A"
        eta = f"{d.get("eta", 0)}s" if d.get("eta") else "N/A"
        status = DownloadingState.IN_PROGRESS if d["status"] == "downloading" else DownloadingState.COMPLETED
        
        message = pool.acquire()  # Get a message from the fixed size pool

        # Set the cloned template"s values
        message.set_property("url", url)
        message.set_property("file_name", file_name)
        message.set_property("progress", progress)
        message.set_property("downloaded_bytes", downloaded_bytes)
        message.set_property("file_size", total_bytes)
        message.set_property("download_speed", speed)
        message.set_property("ETA", eta)
        message.set_property("status", status)
        message.set_property("timestamp", time())

        message_queue.publish(message)  # Push message to the queue

    def complete(self, url: str, elapsed_time: float):
        """Mark a download as completed."""
        if url in self.status:
            self.status[url]["status"] = DownloadingState.COMPLETED
            self.status[url]["elapsed_time"] = f"{round(elapsed_time, 2)}s"

    def _handle_message(self, msg: MessageTemplate):
        """Return the current download status."""
        # A Consumer which gets notified and pulls the message from the queue Displays it 
        # Have the message released to the pool back again
        media_status = msg.to_dict()        
        self.consumer_logic_callable(media_status)
        self.status[msg.get_property("url")] = media_status
        pool.release(msg)

    def get_status(self):
        return self.status

