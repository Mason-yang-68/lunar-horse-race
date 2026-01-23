"""
Remove white background from images.
Values close to white (255, 255, 255) will be made transparent.
"""
from PIL import Image
import os

def remove_white_background(image_path, output_path, tolerance=30):
    """
    Remove white background.
    """
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
        
        img.save(output_path, 'PNG')
        print(f"Processed: {os.path.basename(output_path)} - removed {changed} pixels")
        return True
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return False

def process_new_horses():
    """Process the 6 new horse images."""
    # Source is the artifacts folder, destination is the project folder
    # But first I need to copy them to project folder or process them in place
    # The user manual copy step will happen later, I should process them where they are or copy-process.
    
    # I will assume I need to copy them from artifact dir to project dir 
    # But wait, I don't know the exact artifact path in this script easily without passing it.
    # I will run this script on the project folder after copying the files there.
    pass

if __name__ == '__main__':
    # Process regular horses
    base_folder = r'c:\Users\guziy\Documents\過年紅包\static\images'
    print(f"Processing base folder: {base_folder}")
    for filename in os.listdir(base_folder):
        if filename.startswith('horse') and filename.endswith('.png'):
            filepath = os.path.join(base_folder, filename)
            remove_white_background(filepath, filepath, tolerance=40)

    # Process mingchang horses
    mc_folder = os.path.join(base_folder, 'mingchang')
    print(f"Processing Ming Chang folder: {mc_folder}")
    if os.path.exists(mc_folder):
        for filename in os.listdir(mc_folder):
            if filename.startswith('hw_horse') and filename.endswith('.png'):
                filepath = os.path.join(mc_folder, filename)
                remove_white_background(filepath, filepath, tolerance=40)
    
    print("Background removal complete.")
