import os
import sys
from PIL import Image

def remove_white_background(image_path, output_path=None, tolerance=40):
    """
    Remove white background from an image.
    Values close to white (255, 255, 255) within tolerance will be made transparent.
    """
    if output_path is None:
        output_path = image_path
        
    try:
        img = Image.open(image_path).convert('RGBA')
        pixels = img.load()
        width, height = img.size
        
        changed = 0
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                
                # Check if pixel is white-ish
                if r > 255 - tolerance and g > 255 - tolerance and b > 255 - tolerance:
                    pixels[x, y] = (0, 0, 0, 0)
                    changed += 1
        
        if changed > 0:
            img.save(output_path, 'PNG')
            print(f"[OK] {os.path.basename(image_path)}: Removed {changed} pixels")
        else:
            print(f"[SKIP] {os.path.basename(image_path)}: No white background found")
            
        return True
    except Exception as e:
        print(f"[ERROR] {os.path.basename(image_path)}: {e}")
        return False

def process_directory(directory_path, recursive=True):
    """
    Process all png images in a directory.
    """
    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return

    print(f"Scanning: {directory_path}")
    
    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            if filename.lower().endswith('.png') and ('horse' in filename.lower()):
                file_path = os.path.join(root, filename)
                remove_white_background(file_path)
        
        if not recursive:
            break

if __name__ == '__main__':
    # Default paths
    base_images_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'images')
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if os.path.isfile(target):
            remove_white_background(target)
        elif os.path.isdir(target):
            process_directory(target)
        else:
            print(f"Invalid path: {target}")
    else:
        # Default behavior: scan static/images
        print("Running default scan on static/images...")
        process_directory(base_images_path)
