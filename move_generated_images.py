import shutil
import os

source_files = {
    "ocr_code.png": "C:/Users/nanoc/.gemini/antigravity/brain/304007e9-e426-4d59-ac1d-03773a87a82c/ocr_code_1765559879715.png",
    "ocr_data.png": "C:/Users/nanoc/.gemini/antigravity/brain/304007e9-e426-4d59-ac1d-03773a87a82c/ocr_data_1765559899515.png",
    "ocr_test.png": "C:/Users/nanoc/.gemini/antigravity/brain/304007e9-e426-4d59-ac1d-03773a87a82c/ocr_test_img_1765559917233.png",
    "ocr_bench.png": "C:/Users/nanoc/.gemini/antigravity/brain/304007e9-e426-4d59-ac1d-03773a87a82c/ocr_bench_1765559939521.png",
    "ocr_ai.png": "C:/Users/nanoc/.gemini/antigravity/brain/304007e9-e426-4d59-ac1d-03773a87a82c/ocr_ai_1765559958749.png",
    "count_apples.png": "C:/Users/nanoc/.gemini/antigravity/brain/304007e9-e426-4d59-ac1d-03773a87a82c/count_apples_1765559981225.png",
    "count_cats.png": "C:/Users/nanoc/.gemini/antigravity/brain/304007e9-e426-4d59-ac1d-03773a87a82c/count_cats_1765560003491.png",
    "count_books.png": "C:/Users/nanoc/.gemini/antigravity/brain/304007e9-e426-4d59-ac1d-03773a87a82c/count_books_1765560026025.png",
    "count_pens.png": "C:/Users/nanoc/.gemini/antigravity/brain/304007e9-e426-4d59-ac1d-03773a87a82c/count_pens_1765560049040.png",
    "count_car.png": "C:/Users/nanoc/.gemini/antigravity/brain/304007e9-e426-4d59-ac1d-03773a87a82c/count_car_1765560070133.png"
}

dest_dir = "bench/images"
os.makedirs(dest_dir, exist_ok=True)

for name, src in source_files.items():
    if os.path.exists(src):
        try:
            shutil.copy2(src, os.path.join(dest_dir, name))
            print(f"Copied {name}")
        except Exception as e:
            print(f"Error copying {name}: {e}")
    else:
        print(f"Source not found: {src}")
