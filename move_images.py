import shutil
import os

src_ocr = "C:/Users/nanoc/.gemini/antigravity/brain/ccb119d9-dd84-4e60-bc02-fe4024baf06b/ocr_test_image_1765546233719.png"
src_count = "C:/Users/nanoc/.gemini/antigravity/brain/ccb119d9-dd84-4e60-bc02-fe4024baf06b/count_test_image_1765546261988.png"

dst_dir = "bench/images"
os.makedirs(dst_dir, exist_ok=True)

try:
    shutil.copy(src_ocr, os.path.join(dst_dir, "ocr_test_gen.png"))
    print("Copied OCR image")
except Exception as e:
    print(f"Failed to copy OCR: {e}")

try:
    shutil.copy(src_count, os.path.join(dst_dir, "count_test_gen.png"))
    print("Copied Count image")
except Exception as e:
    print(f"Failed to copy Count: {e}")
