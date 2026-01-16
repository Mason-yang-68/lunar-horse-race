import os
from rembg import remove
from PIL import Image
import io

IMAGE_DIR = os.path.join(os.getcwd(), 'static', 'images')

def process_images():
    if not os.path.exists(IMAGE_DIR):
        print(f"Directory not found: {IMAGE_DIR}")
        return

    files = [f for f in os.listdir(IMAGE_DIR) if f.startswith('horse') and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"Found {len(files)} horse images.")

    for filename in files:
        input_path = os.path.join(IMAGE_DIR, filename)
        output_path = input_path # Overwrite
        
        print(f"Processing {filename}...")
        
        try:
            with open(input_path, 'rb') as i:
                input_data = i.read()
                
            output_data = remove(input_data)
            
            # Verify and optimize
            img = Image.open(io.BytesIO(output_data))
            img.save(output_path, 'PNG')
            print(f"Successfully processed {filename}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == '__main__':
    process_images()
