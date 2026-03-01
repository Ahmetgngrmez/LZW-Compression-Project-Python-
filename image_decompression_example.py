from LZW import LZWCoding

# Decompress an image file
filename = 'image'   # filename without the extension
lzw = LZWCoding(filename, 'image')
output_path = lzw.decompress_image_file()

# Compare original and decompressed images
original_image = filename + '.png'
decompressed_image = filename + '_decompressed.png'
lzw.compare_images(original_image, decompressed_image)
