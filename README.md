# RedExtractor
RedExtractor is the go to choice for YouTube video Downloading, flexible Python framework for downloading videos and audio streams using [yt-dlp]. It supports multiple download strategies, including basic single-stream downloads, parallel downloads, MP3 extraction, and real-time progress tracking.

---

## Features

- **Multiple Download Strategies**  
  Choose the best download approach for your needs:  
  - Basic single-stream download  
  - Parallel download with segmented streams  
  - MP3 audio-only download  

- **Progress Tracking**  
  Real-time download progress updates via callbacks or event hooks.

- **Format Selection & Customization**  
  Easily select video/audio formats or quality preferences.

- **Concurrent Downloads**  
  Download multiple videos concurrently with thread or process-based parallelism.

- **Extensible & Modular**  
  Designed with strategy patterns for easy addition of new download methods.

- **User-friendly**
  Simple, decent API to use fluently and choose downloading strategies, designed to be the best.

- **Cross-platform Support**  
  Works on Windows, macOS, and Linux systems.


---

🛠 Technologies Used
Python 3.12.1

ytd-lp (for YouTube downloads)

FFmpeg (for processing media files)

PulseBus (for instantaneous progress tracking)

unittest (for testing)

---

## Installation

```bash
pip install RedExtractor

