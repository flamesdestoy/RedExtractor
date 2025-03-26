import asyncio
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Tuple
import yt_dlp
import uuid

from download_helper import download_media
from logger import logger


def sanitize_filename(filename: str) -> str:
    """Remove invalid filename characters while preserving Unicode"""
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', filename).strip()

async def download_media_separately(
    url: str,
    output_dir: str = "downloads",
    video_format: str = "bestvideo[height<=1080][ext=mp4]",
    audio_format: str = "bestaudio[ext=m4a]",
    max_workers: int = 2
) -> Optional[str]:
    """
    Downloads and merges media with session-based temp files.
    
    Returns:
        Path to merged file if successful, None otherwise
    """
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Get video metadata
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = sanitize_filename(info['title'])
            session_id = uuid.uuid4().hex[:8]  # 8-character unique ID
            
        # Prepare paths
        final_path = os.path.join(output_dir, f"{title}.mp4")
        video_temp = os.path.join(output_dir, f"video_{session_id}.mp4")
        audio_temp = os.path.join(output_dir, f"audio_{session_id}.m4a")
        
        # Download both streams in parallel
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            download_tasks = [
                loop.run_in_executor(
                    executor,
                    lambda: download_stream(url, video_format, video_temp)
                ),
                loop.run_in_executor(
                    executor,
                    lambda: download_stream(url, audio_format, audio_temp)
                )
            ]
            
            results = await asyncio.gather(*download_tasks)
            
            # Check if both downloads succeeded
            if None in results:
                logger.error("One or both downloads failed")
                return None

        # Merge streams
        if not merge_streams(video_temp, audio_temp, final_path):
            return None
            
        # Cleanup
        for path in (video_temp, audio_temp):
            try:
                if path and os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                logger.warning(f"Couldn't delete temp file {path}: {e}")
        
        return final_path
        
    except Exception as e:
        logger.error(f"Download process failed: {str(e)}")
        return None

def download_stream(url: str, format_spec: str, output_path: str) -> Optional[str]:
    """Downloads a single stream with validation"""
    try:
        ydl_opts = {
            'format': format_spec,
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Verify download completed successfully
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        return None
    except Exception as e:
        logger.error(f"Download failed for {format_spec}: {str(e)}")
        return None

def merge_streams(video_path: str, audio_path: str, output_path: str) -> bool:
    """Merges video and audio streams safely"""
    try:
        # Verify both files exist
        if not all(os.path.exists(p) for p in (video_path, audio_path)):
            missing = [p for p in (video_path, audio_path) if not os.path.exists(p)]
            logger.error(f"Missing files for merging: {missing}")
            return False

        # FFmpeg command (no re-encoding)
        cmd = [
            'ffmpeg',
            '-y',                    # Overwrite output
            '-i', video_path,        # Video input
            '-i', audio_path,        # Audio input
            '-c:v', 'copy',         # Copy video stream
            '-c:a', 'copy',         # Copy audio stream
            '-movflags', 'faststart',  # Enable streaming
            output_path
        ]
        
        # Run FFmpeg
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Verify output
        if not os.path.exists(output_path):
            logger.error("FFmpeg completed but no output file created")
            return False
            
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg merge failed: {e.stderr.strip()}")
        return False
    except Exception as e:
        logger.error(f"Unexpected merge error: {str(e)}")
        return False
    