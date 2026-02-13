from utils.locate_notepad_utils import locate_notepad_icon
from utils.api_handler import fetch_posts
from utils.automation import open_notepad, type_text_in_notepad, save_notepad_file, close_notepad
import time
import os

# Configuration
ENABLE_GROUNDING_VISUALIZATION = False  # Set to True to save annotated screenshots
MAX_POSTS = 10  # Number of posts to process

if __name__ == "__main__":
    posts = fetch_posts(limit=MAX_POSTS)
    if not posts:
        print("No data fetched.")
        exit()
    
    # Ensure output directory exists for visualizations
    if ENABLE_GROUNDING_VISUALIZATION:
        os.makedirs("output", exist_ok=True)
        print(f"\n📸 Grounding visualization ENABLED - Screenshots will be saved to output/")
    
    print(f"\n{'='*70}")
    print(f"Starting automation for {len(posts)} posts...")
    print(f"{'='*70}\n")
    
    # Process all 10 posts
    posts_to_process = posts[:MAX_POSTS]
    successful = 0
    
    for i, post in enumerate(posts_to_process):
        try:
            print(f"\n{'─'*70}")
            print(f"📝 Processing Post {i+1}/{len(posts_to_process)} (ID: {post['id']})")
            print(f"{'─'*70}")
            
            time.sleep(2)

            # Take fresh screenshot & locate Notepad icon using visual grounding
            print(f"\n🔍 Taking fresh screenshot & locating Notepad icon...")
            x, y = locate_notepad_icon(
                max_attempts=3,
                debug=True,
                save_visualization=ENABLE_GROUNDING_VISUALIZATION
            )
            print(f"✓ Icon found at ({x}, {y})")
          
            # Open Notepad by double-clicking the grounded icon
            print(f"\n🚀 Launching Notepad...")
            notepad_window = open_notepad(x, y)
            time.sleep(1)  # Extra wait for stability

            # Type post content: Title + Body
            print(f"\n⌨️  Typing post content...")
            content = f"Title: {post['title']}\n\n{post['body']}"
            type_text_in_notepad(content)
            time.sleep(1)  # Wait for typing to complete

            # Save file as post_{id}.txt inside C:\Users\hp\Desktop\tjm-project
            print(f"\n💾 Saving file...")
            filename = f"post_{post['id']}.txt"
            saved_path = save_notepad_file(filename)
            print(f"✓ Saved: {saved_path}")
            time.sleep(1)

            # Close Notepad
            print(f"\n❌ Closing Notepad...")
            close_notepad()
            
            successful += 1
            print(f"\n{'='*50}")
            print(f"✓ Completed Post {post['id']} successfully!")
            print(f"{'='*50}")
            time.sleep(2)  # Wait before next post 
            
        except Exception as e:
            print(f"\n❌ Error processing post {post['id']}: {e}")
            print("Skipping to next post...")
            try:
                close_notepad()
            except:
                pass
            time.sleep(1)
            continue

    print(f"\n{'='*70}")
    print(f"✓ Automation Complete! Successfully processed {successful}/{len(posts_to_process)} posts.")
    print(f"  Files saved to: C:\\Users\\hp\\Desktop\\tjm-project")
    print(f"{'='*70}\n")

