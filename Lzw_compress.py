import numpy as np
from PIL import Image
import math
import os
import struct 

def calculate_metrics(original_data, binary_file_path, original_bits_per_pixel=8):
    unique, counts = np.unique(original_data, return_counts=True)
    probs = counts / len(original_data)
    entropy = -sum(p * math.log2(p) for p in probs)
    
    compressed_file_size_bytes = os.path.getsize(binary_file_path)
    total_bits_compressed = compressed_file_size_bytes * 8
    
    avg_code_length = total_bits_compressed / len(original_data)
    original_size_bits = len(original_data) * original_bits_per_pixel
    compression_ratio = original_size_bits / total_bits_compressed
    
    return entropy, avg_code_length, compression_ratio, compressed_file_size_bytes

def lzw_compress(data):
    dict_size = 256
    dictionary = {bytes([i]): i for i in range(dict_size)}
    current_phrase = bytes([])
    compressed_data = []
    
    for pixel in data:
        new_phrase = current_phrase + bytes([pixel])
        if new_phrase in dictionary:
            current_phrase = new_phrase
        else:
            compressed_data.append(dictionary[current_phrase])
            dictionary[new_phrase] = dict_size
            dict_size += 1
            current_phrase = bytes([pixel])
            
    if current_phrase:
        compressed_data.append(dictionary[current_phrase])
    return compressed_data

def lzw_decompress(compressed_data):
    dict_size = 256
    dictionary = {i: bytes([i]) for i in range(dict_size)}
    if not compressed_data: return b""

    prev_code = compressed_data[0]
    result = [dictionary[prev_code]]
    
    for code in compressed_data[1:]:
        if code in dictionary:
            entry = dictionary[code]
        elif code == dict_size:
            entry = dictionary[prev_code] + bytes([dictionary[prev_code][0]])
        else:
            raise ValueError("Invalid LZW code encountered")
            
        result.append(entry)
        dictionary[dict_size] = dictionary[prev_code] + bytes([entry[0]])
        dict_size += 1
        prev_code = code
    return b"".join(result)

image_input = 'golden-bird.jpg'
binary_output = 'compressed_image.bin' 

if not os.path.exists(image_input):
    print(f"Error: {image_input} not found.")
else:
    img = Image.open(image_input).convert('L')
    img_array = np.array(img)
    flat_data = img_array.flatten()

    compressed_indices = lzw_compress(flat_data)


    with open(binary_output, 'wb') as f:
        for index in compressed_indices:
            f.write(struct.pack('>H', index)) 

    entropy, avg_len, ratio, comp_size_bytes = calculate_metrics(flat_data, binary_output)

    print("\n--- Compression Results ---")
    print(f"Entropy: {entropy:.4f} bits/pixel")
    print(f"Average Code Length (L_avg): {avg_len:.4f} bits/pixel")
    print(f"Compression Ratio (CR): {ratio:.4f}")
    print(f"Compressed File Size: {comp_size_bytes} bytes")

    loaded_indices = []
    with open(binary_output, 'rb') as f:
        while True:
            chunk = f.read(2) 
            if not chunk: break
            loaded_indices.append(struct.unpack('>H', chunk)[0])
    
    restored_bytes = lzw_decompress(loaded_indices)
    restored_img_array = np.frombuffer(restored_bytes, dtype=np.uint8).reshape(img_array.shape)

    is_identical = np.array_equal(img_array, restored_img_array)
    print(f"\nLossless Verification: {'SUCCESS' if is_identical else 'FAILED'}")
    Image.fromarray(restored_img_array).save('restored_image.png')