from LZW import LZWCoding

# Compress an image file
filename = 'image'   # filename without the extension (assumes image.png exists)
lzw = LZWCoding(filename, 'image')
output_path = lzw.compress_image_file()
