# Panopto Video Downloader

A Python script to download videos from Panopto folders using Playwright for browser automation.

## Prerequisites

- Python 3.x 
- Playwright
- (you may want to consult an LLM on how to install this)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/zach-ath/panoptodownload.git
   cd panoptodownload
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install playwright
   playwright install
   ```

## Usage

1. Update the `FOLDER_URL` in `panopto.py` to point to your desired Panopto folder.

2. Run the script:
   ```bash
   python panopto.py
   ```

3. Follow the on-screen instructions:
   - Log in with your university credentials in the browser window that opens.
   - Scroll down to load all videos in the folder.
   - Press ENTER in the terminal to start downloading.
   - **This is currently setup for UoA - but you can get an LLM to change this out**

The script will automatically download all visible videos in the folder to the current directory.

## Notes

- This script requires manual login and scrolling to ensure all videos are loaded.
- Downloads are saved with their original filenames.
- There's a 3-second delay between downloads to avoid rate limiting.

## Disclaimer
It will fail if you don't have enough storage space.
Use this script responsibly and in accordance with your institution's terms of service and copyright policies.
