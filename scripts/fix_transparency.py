
from PIL import Image, ImageDraw
import os

target_dir = r'c:\Users\guziy\Documents\過年紅包\static\images\mingchang'

def remove_bg(img_path):
    try:
        img = Image.open(img_path).convert("RGBA")
        datas = img.getdata()
        
        # Check top-left pixel
        bg_color = img.getpixel((0, 0))
        
        # Heuristic: if top-left is transparent, assume it's processed (or check if user wants re-processing?)
        if bg_color[3] == 0:
            print(f"Skipping {os.path.basename(img_path)}: Already transparent.")
            return

        # If it's white-ish
        if bg_color[0] > 240 and bg_color[1] > 240 and bg_color[2] > 240:
            print(f"Processing {os.path.basename(img_path)}: Found white background.")
            
            # Flood fill from corners
            ImageDraw.floodfill(img, (0, 0), (255, 255, 255, 0), thresh=20)
            ImageDraw.floodfill(img, (img.width-1, 0), (255, 255, 255, 0), thresh=20)
            ImageDraw.floodfill(img, (0, img.height-1), (255, 255, 255, 0), thresh=20)
            ImageDraw.floodfill(img, (img.width-1, img.height-1), (255, 255, 255, 0), thresh=20)
            
            img.save(img_path)
            print("Saved.")
        else:
            print(f"Skipping {os.path.basename(img_path)}: Background not white {bg_color}.")

    except Exception as e:
        print(f"Error processing {img_path}: {e}")

for i in range(1, 11):
    filename = f'hw_horse{i}.png'
    path = os.path.join(target_dir, filename)
    if os.path.exists(path):
        remove_bg(path)
    else:
        print(f"File not found: {filename}")
