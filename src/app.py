import time

import config
from .api import PostsClient
from .automation.icon_locator import locate_notepad_icon
from .automation.window_manager import open_notepad, close_notepad
from .automation.text_input import type_text_in_notepad
from .automation.file_saver import save_notepad_file


def run() -> None:
    posts = PostsClient().get_posts(limit=config.MAX_POSTS)
    if not posts:
        print("No data fetched — nothing to do.")
        return

    print(f"\n{'='*70}")
    print(f"Starting automation — {len(posts)} posts to process")
    print(f"{'='*70}\n")

    successful = 0
    for i, post in enumerate(posts, 1):
        print(f"\n{'─'*70}")
        print(f"Post {i}/{len(posts)}  (ID: {post['id']})")
        print(f"{'─'*70}")

        try:
            # Fresh screenshot + grounding every iteration.
            # The icon may have been moved between posts — detect dynamically.
            print("  Locating Notepad icon...")
            x, y = locate_notepad_icon(save_visualization=config.ENABLE_VISUALIZATION)

            open_notepad(x, y)
            time.sleep(1)

            content = f"Title: {post['title']}\n\n{post['body']}"
            type_text_in_notepad(content)
            time.sleep(1)

            saved_path = save_notepad_file(f"post_{post['id']}.txt")
            print(f"  Saved → {saved_path}")
            time.sleep(1)

            close_notepad()
            successful += 1
            time.sleep(2)

        except Exception as e:
            print(f"\n  Error on post {post['id']}: {e}")
            try:
                close_notepad()
            except Exception:
                pass
            time.sleep(1)

    print(f"\n{'='*70}")
    print(f"Done — {successful}/{len(posts)} posts saved to {config.SAVE_DIR}")
    print(f"{'='*70}\n")
