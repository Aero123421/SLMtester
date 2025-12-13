import base64
import os

# A simple red square 5x5
red_dot_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="

target_dir = "bench/images"
os.makedirs(target_dir, exist_ok=True)
with open(os.path.join(target_dir, "ocr_test.png"), "wb") as f:
    f.write(base64.b64decode(red_dot_b64))

print(f"Created {target_dir}/ocr_test.png")
