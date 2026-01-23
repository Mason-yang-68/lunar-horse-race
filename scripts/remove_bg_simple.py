from PIL import Image
import os

IMAGE_DIR = os.path.join(os.getcwd(), 'static', 'images')
THRESHOLD = 230  # Brightness threshold (0-255)

def process_images_simple():
    if not os.path.exists(IMAGE_DIR):
        print(f"Directory not found: {IMAGE_DIR}")
        return

    files = [f for f in os.listdir(IMAGE_DIR) if f.startswith('horse') and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"Found {len(files)} horse images. Removing light background...")

    for filename in files:
        input_path = os.path.join(IMAGE_DIR, filename)
        
        try:
            img = Image.open(input_path).convert("RGBA")
            datas = img.getdata()
            
            new_data = []
            for item in datas:
                # If pixel is very light (white/gray), make it transparent
                if item[0] > THRESHOLD and item[1] > THRESHOLD and item[2] > THRESHOLD:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            
            img.putdata(new_data)
            
            # Save as PNG
            output_filename = os.path.splitext(filename)[0] + ".png"
            output_path = os.path.join(IMAGE_DIR, output_filename)
            img.save(output_path, "PNG")
            print(f"Processed {filename}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == '__main__':
    process_images_simple()
