


import PIL.Image

# --- Parameters to control resolution ---
NEW_WIDTH = 240
# Character set from dark to light
ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

def main():
    path = input("Enter the path to the image file: \n")
    
    path = f"/usr/share/rpd-wallpaper/{path}"

    print(f"path: {path}")

    try:
        image = PIL.Image.open(path)
    except Exception as e:
        print(f"Unable to open image file: {e}")
        return

    # Ask user if they want to invert colors
    invert_choice = input("Do you want to invert the colors (dark to light)? (yes/no): \n").strip().lower()
    invert = invert_choice in ['yes', 'y']
    
    # Convert the image to grayscale
    image = image.convert('L')
    
    # Invert the image if requested
    if invert:
        image = PIL.Image.eval(image, lambda p: 255 - p)
        print("Image inverted successfully")
    
    # Resize the image
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * NEW_WIDTH * 0.55)
    resized_image = image.resize((NEW_WIDTH, new_height))
    
    # Generate the ASCII art string
    ascii_art = pixels_to_ascii(resized_image)
    
    # Save the result to a file
    try:
        with open("ascii_image.txt", "w") as f:
            f.write(ascii_art)
        print("ASCII art successfully saved to ascii_image.txt")
    except Exception as e:
        print(f"Unable to save file: {e}")

def pixels_to_ascii(image):
    """Converts a PIL image's pixels to an ASCII string."""
    pixels = image.getdata()
    # Map each pixel to an ASCII character
    characters = "".join([ASCII_CHARS[pixel // 25] for pixel in pixels])
    
    # Reshape the string of characters into lines
    pixel_count = len(characters)
    width, _ = image.size
    ascii_image = "\n".join([characters[i:(i + width)] for i in range(0, pixel_count, width)])
    
    return ascii_image

if __name__ == '__main__':
    main()


    
