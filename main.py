from utils.locate_notepad_utils import locate_notepad_icon
from utils.api_handler import fetch_posts
from utils.automation import open_notepad, type_text_in_notepad, save_notepad_file, close_notepad
import time

if __name__ == "__main__":
    posts = fetch_posts(limit=10)
    if not posts:
        print("لم يتم جلب بيانات.")
        exit()
    
    print(f"Starting automation for {len(posts)} posts...")
    
    for i, post in enumerate(posts):
        try:
            print(f"\n--- Processing Post {i+1}/{len(posts)} (ID: {post['id']}) ---")
            
            time.sleep(2)

            x, y = locate_notepad_icon()
            open_notepad(x, y)

            content = f"Title: {post['title']}\n\n{post['body']}"
            type_text_in_notepad(content)

            filename = f"post_{post['id']}.txt"
            save_notepad_file(filename)

            close_notepad()
            
            print(f"Completed Post {post['id']} successfully.")
            time.sleep(1) 
            
        except Exception as e:
            print("Skipping to next post...")
            try:
                close_notepad()
            except:
                pass
            continue
