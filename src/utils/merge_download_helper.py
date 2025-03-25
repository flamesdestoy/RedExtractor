import asyncio
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
import yt_dlp

from src.utils.download_helper import download_media


async def download_media_separately(
    url: str,
    output_dir: str = "downloads",
    video_format: str = "bestvideo",
    audio_format: str = "bestaudio",
    max_workers: int = 4,
    title_length: int = 50
) -> Optional[str]:
    """
    Downloads video and audio streams in parallel, merges them via FFmpeg piping.
    
    Args:
        url: Video URL
        output_dir: Output directory (default: "downloads")
        video_format: Video stream selector (default: "bestvideo")
        audio_format: Audio stream selector (default: "bestaudio")
        max_workers: Thread pool size (default: 4)
        title_length: Max characters for filename (default: 50)
    
    Returns:
        Path to merged file or None if failed
    """
    
    # Get video metadata first
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = sanitize_filename(info['title'])[:title_length]
        output_template = f"{output_dir}/{title}.%(ext)s"

    # Prepare parallel downloads
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Download both streams simultaneously
        video_future = loop.run_in_executor(
            executor, 
            partial_download,
            url, 
            video_format,
            f"{output_template % {'ext': 'mp4'}}"
        )
        audio_future = loop.run_in_executor(
            executor,
            partial_download,
            url,
            audio_format,
            f"{output_template % {'ext': 'm4a'}}"
        )

        video_path, audio_path = await asyncio.gather(video_future, audio_future)

    # Merge streams with FFmpeg piping (no temp files)
    output_path = f"{output_dir}/{title}.mp4"
    merge_success = merge_with_ffmpeg_pipe(video_path, audio_path, output_path)
    
    # Cleanup partial files
    for path in (video_path, audio_path):
        if path and os.path.exists(path):
            os.unlink(path)

    return output_path if merge_success else None


def partial_download(url: str, format_spec: str, output_path: str) -> Optional[str]:
    """Download single stream (video or audio)"""
    ydl_opts = {
        'format': format_spec,
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }

    download_media(url, ydl_opts)
        

def merge_with_ffmpeg_pipe(
    video_path: str,
    audio_path: str,
    output_path: str
) -> bool:
    """Merge streams using FFmpeg pipes for zero-copy efficiency"""
    try:
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # Overwrite without asking
            '-i', 'pipe:0',  # Video from stdin
            '-i', 'pipe:1',  # Audio from stdin
            '-c:v', 'copy',  # Stream copy (no re-encode)
            '-c:a', 'copy',  # Stream copy (no re-encode)
            '-movflags', 'faststart',  # Enable streaming
            output_path
        ]
        
        with subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE) as proc:
            # Pipe video and audio simultaneously
            with open(video_path, 'rb') as vfile, open(audio_path, 'rb') as afile:
                proc.communicate(input=vfile.read() + afile.read())
        return True
    except Exception as e:
        print(f"Merge failed: {e}")
        return False


def sanitize_filename(filename: str) -> str:
    """Remove invalid filename characters"""
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', filename).strip()

