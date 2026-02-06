from utils.locate_notepad_utils import locate_notepad_icon
from utils.api_handler import fetch_posts
from utils.automation import open_notepad, type_text_in_notepad, save_notepad_file, close_notepad
import time

if __name__ == "__main__":
    try:
        # جلب أول بوست فقط
        posts = fetch_posts(limit=10)
        if not posts:
            print("لم يتم جلب بيانات.")
            exit()
        
        for post in posts:
            print(f"جاري العمل على بوست ID: {post['id']}")

            # تحديد مكان الأيقونة وفتح Notepad
            x, y = locate_notepad_icon()
            open_notepad(x, y)

            # الكتابة
            content = f"Title: {post['title']}\n\n{post['body']}"
            type_text_in_notepad(content)

            # الحفظ واستبدال أي ملف موجود
            filename = f"post_{post['id']}.txt"
            save_notepad_file(filename)

            # الإغلاق النهائي
            close_notepad()
            
            print(f"تمت العملية بنجاح! الملف موجود في Desktop/tjm-project/{filename}")

    except Exception as e:
        print(f"حدث خطأ: {e}")
