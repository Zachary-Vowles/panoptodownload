import re
import time
import os
from playwright.sync_api import sync_playwright

FOLDER_URL = "https://auckland.au.panopto.com/Panopto/Pages/Sessions/List.aspx?embedded=0&isFromTeams=false#view=0&maxResults=250&endDate=%2202%2F01%2F2025%22"
BASE_URL = "https://auckland.au.panopto.com"

def sanitize_filename(filename: str, max_length: int = 150) -> str:
    """
    Cleans illegal OS characters, normalizes whitespace, and truncates filename.
    """
    # Remove invalid filename characters (\ / : * ? " < > |)
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Replace multiple spaces/newlines with a single space
    sanitized = re.sub(r'\s+', " ", sanitized).strip()
    
    # Truncate to max_length while preserving room for the extension
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip()
        
    return sanitized

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        print("Navigating to Panopto...")
        page.goto(FOLDER_URL)

        print("\n*** MANUAL STEPS REQUIRED ***")
        print("1. Please log in with your university credentials in the browser window.")
        print("2. Once logged in and on the folder page, SCROLL DOWN to the very bottom.")
        print("3. Ensure ALL videos you want to download are visible on the screen.")
        input("Press ENTER here in the terminal when you are ready to continue...")

        page.wait_for_load_state("networkidle")
        page.locator('a[href*="Viewer.aspx?id="]').first.wait_for(state="attached", timeout=10000)

        # Extract structured data (Video ID, Title, and Folder Name) directly from row elements
        items_data = page.evaluate('''() => {
            const results = [];
            // Target rows in Panopto list view
            const rows = document.querySelectorAll('tr[id]');
            
            rows.forEach(row => {
                const videoLink = row.querySelector('a[href*="Viewer.aspx?id="]');
                const folderLink = row.querySelector('td.list-folder div a.folder-link');
                
                if (videoLink) {
                    const href = videoLink.href;
                    const match = href.match(/id=([a-f0-9\\-]+)/i);
                    if (match) {
                        results.push({
                            id: match[1],
                            title: videoLink.innerText.trim(),
                            folder: folderLink ? folderLink.innerText.trim() : ""
                        });
                    }
                }
            });
            return results;
        }''')

        # Fallback: Check if there's a global page/folder header if row-level folder is empty
        global_folder_name = page.evaluate('''() => {
            const header = document.querySelector('#folderName, .folder-name, #deliveryHeader');
            return header ? header.innerText.trim() : "";
        }''')

        # Remove duplicate video IDs
        unique_videos = {}
        for item in items_data:
            if item['id'] not in unique_videos:
                unique_videos[item['id']] = item

        video_list = list(unique_videos.values())
        print(f"\nFound {len(video_list)} unique videos to download.")

        # Loop through and download
        for index, item in enumerate(video_list, start=1):
            vid_id = item['id']
            video_title = item['title'] or "Untitled"
            folder_name = item['folder'] or global_folder_name or "Course"

            download_url = f"{BASE_URL}/Panopto/Podcast/Download/{vid_id}.mp4?mediaTargetType=videoPodcast"
            print(f"[{index}/{len(video_list)}] Processing ID: {vid_id}...")

            try:
                with page.expect_download(timeout=60000) as download_info:
                    page.evaluate(f"window.location.href = '{download_url}'")

                download = download_info.value
                original_filename = download.suggested_filename
                
                # Get extension (default .mp4)
                ext = os.path.splitext(original_filename)[1] or ".mp4"

                # Construct new filename: [Folder Name] - [Video Title].mp4
                raw_new_filename = f"[{folder_name}] {video_title}"
                
                # Sanitize and strictly clamp to max length (e.g., 140 chars + extension)
                clean_base_name = sanitize_filename(raw_new_filename, max_length=140)
                final_filename = f"{clean_base_name}{ext}"

                print(f"   -> Saving as: {final_filename}")
                download.save_as(final_filename)
                print(f"   -> Successfully saved!")

                time.sleep(3)

            except Exception as e:
                print(f"   -> Failed to download {vid_id}: {e}")

        print("\nAll downloads completed!")
        browser.close()

if __name__ == "__main__":
    main()
