import argparse
import os
import imghdr
from PIL import Image

def resize_image(image_path, max_size, output_format, quality, realesrgan_path):
    image = Image.open(image_path)

    # Check if the image has already been processed
    if (image.width == max_size or image.height == max_size) and image.format == "JPEG" and os.path.splitext(image_path)[1].lower() == ".jpg" and image.mode == "RGB":
        print(f"Skipping {image_path}: already processed")
        return

    if image.width < max_size and image.height < max_size:
        print(f"Upscaling {image_path}...")
        upscaled_image_path = os.path.splitext(image_path)[0] + '.png'

        # Upscale with realesrgan
        escaped_image_path = image_path.replace('"', '\\"')
        escaped_upscaled_image_path = upscaled_image_path.replace('"', '\\"')
        upscale_result = os.system(f"{realesrgan_path} -i \"{escaped_image_path}\" -o \"{escaped_upscaled_image_path}\" > /dev/null 2>&1")

        # Check if upscaled file exists
        if not os.path.isfile(upscaled_image_path):
            print(f"Failed to upscale {image_path} to {upscaled_image_path}")
            exit(1)

        # Remove the original file
        os.remove(image_path)

        # Reopen the image
        image_path = upscaled_image_path
        image = Image.open(image_path)

    image = image.convert("RGB")

    # Calculate aspect ratio and new image size
    aspect_ratio = image.width / image.height
    if aspect_ratio >= 1:
        new_width = min(max_size, image.width)
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = min(max_size, image.height)
        new_width = int(new_height * aspect_ratio)

    # Resize the image
    resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)

    # Save the image in the new format with new quality, overwriting the original file
    output_path = os.path.splitext(image_path)[0] + '.jpg'
    resized_image.save(output_path, format=output_format, quality=quality)
    print(f"Processed {image_path}")

    # Remove the original file if output_path is different from image_path
    if output_path != image_path:
        os.remove(image_path)


def process_directory(directory, max_size, output_format, quality, realesrgan_path):
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)

            # Check if the file is an image
            if imghdr.what(file_path):
                try:
                    resize_image(file_path, max_size, output_format, quality, realesrgan_path)
                except Exception as e:
                    print(f"Failed to process {file_path}: {e}")
            else:
                print(f"Skipping non-image file {file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resize images in a directory.")
    parser.add_argument("input_directory", help="The input directory with images.")

    args = parser.parse_args()

    input_directory = args.input_directory
    max_pixels = 1024
    format_to_convert = "JPEG"
    image_quality = 90
    realesrgan_path = "/home/jordan/Downloads/realesrgan-ncnn-vulkan-20220424-ubuntu/realesrgan-ncnn-vulkan"

    process_directory(input_directory, max_pixels, format_to_convert, image_quality, realesrgan_path)

    print("Done!")