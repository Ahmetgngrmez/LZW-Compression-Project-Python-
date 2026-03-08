import numpy as np
from PIL import Image
import math
import os

def calculate_metrics(original_pixels,compressed_data):
    #Calculates Entropy, Average Code Length and Compression Ratio
    unique,counts=np.unique(original_pixels,return_counts=True)
    probabilities=counts/len(original_pixels)
    entropy=-sum(p*math.log2(p) for p in probabilities if p>0)

    num_bits_per_code=math.ceil(math.log2(max(compressed_data)+1))
    avg_code_length=(len(compressed_data)*num_bits_per_code)/len(original_pixels)

    original_total_bits=len(original_pixels)*8
    compressed_total_bits=len(compressed_data)*num_bits_per_code
    compression_ratio=original_total_bits/compressed_total_bits

    return entropy,avg_code_length,compression_ratio,compressed_total_bits

def get_difference_image(img_array):
    #Level 3: Row-wise and Column-wise pixel differences
    height,width=img_array.shape
    diff_arr = np.zeros((height, width), dtype=np.int16)

    # İlk pikseli kopyala
    diff_arr[0, 0] = img_array[0, 0]

    # Satır içi farklar (2. pikselden itibaren)
    for i in range(height):
        for j in range(1, width):
            diff_arr[i, j] = int(img_array[i, j]) - int(img_array[i, j-1])
            
    # İlk sütundaki farklar (2. pikselden itibaren aşağı doğru)
    for i in range(1, height):
        diff_arr[i, 0] = int(img_array[i, 0]) - int(img_array[i-1, 0])
        
    return diff_arr

def restore_from_difference(diff_arr):
    #Level 3: Reconstruct original pixels from differences
    height,width=diff_arr.shape
    restored = np.zeros((height, width), dtype=np.int32)

    # İlk pikseli al
    restored[0, 0] = diff_arr[0, 0]

    # Önce ilk sütunu onar
    for i in range(1, height):
        restored[i, 0] = restored[i-1, 0] + diff_arr[i, 0]
        
    # Sonra kalan satırları onar
    for i in range(height):
        for j in range(1, width):
            restored[i, j] = restored[i, j-1] + diff_arr[i, j]
            
    return np.clip(restored,0,255).astype(np.uint8)

def lzw_compress(pixels):
    shifted_data = [x + 256 for x in pixels]
    dict_size=512
    dictionary={tuple([i]):i for i in range(dict_size)}
    w=[]
    compressed_data=[]

    for pixel in shifted_data:
        wc=w+[pixel]
        if tuple(wc) in dictionary:
            w=wc
        else:
            compressed_data.append(dictionary[tuple(w)])
            dictionary[tuple(wc)]=dict_size
            dict_size+=1
            w=[pixel]

    if w:
        compressed_data.append(dictionary[tuple(w)])
    return compressed_data

def lzw_decompress(compressed_data):
    dict_size=512
    dictionary={i:[i] for i in range(dict_size)}

    k=compressed_data[0]
    w=[k]
    result=[k]

    for k in compressed_data[1:]:
        if k in dictionary:
            entry=dictionary[k]
        elif k==dict_size:
            entry=w+[w[0]]
        else:
            raise ValueError("Incorrect compression code!")
        result.extend(entry)
        dictionary[dict_size]=w+[entry[0]]
        dict_size+=1
        w=entry
    return [x - 256 for x in result]

def main():
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_name='Kefken.jpeg'
    image_path = os.path.join(current_dir,input_file_name)

    if not os.path.exists(image_path):
        print(f"Error:{image_path} not found!")
        return
    
    base_name, extension = os.path.splitext(input_file_name)
    output_file_name = f"{base_name}_restored{extension}"
    # Read and convert image to grayscale
    img=Image.open(image_path).convert("L")
    width,height=img.size
    img_array = np.array(img)

    print(f"Image Size:{width}x{height}")
    print("Compression is starting...")

    diff_image = get_difference_image(img_array)
    diff_pixels = diff_image.flatten().tolist()

    compressed_data=lzw_compress(diff_pixels)

    entropy,avg_len,ratio,comp_size=calculate_metrics(diff_pixels,compressed_data)

    print("-"*30)
    print(f"Entropy:{entropy:.4f}")
    print(f"Average Code Length: {avg_len:.4f} bits/pixel")
    print(f"Compression Ratio: {ratio:.4f}")
    print(f"Compressed File Size (est): {comp_size / 8:.2f} bytes")
    print("-" * 30)

    compressed_file_path = os.path.join(current_dir, "compressed_data.lzw")
    
    # Save binary compressed file (Pickle yerine doğrudan binary yazma)
    with open(compressed_file_path, "wb") as f:
        for code in compressed_data:
            f.write(code.to_bytes(2, byteorder='big'))
    print(f"Compressed data saved: {compressed_file_path}")

    print("Decompression is starting...")

    # Read the stored data (Kaydedilen binary dosyayı diskten okuma)
    read_compressed_data = []
    with open(compressed_file_path, "rb") as f:
        while True:
            bytes_read = f.read(2)
            if not bytes_read:
                break
            read_compressed_data.append(int.from_bytes(bytes_read, byteorder='big'))

    # Decompress and Integrate (Okunan veri üzerinden geri açma)
    restored_pixels = lzw_decompress(read_compressed_data)
    diff_arr_2d = np.array(restored_pixels).reshape((height, width))
    final_pixels = restore_from_difference(diff_arr_2d)

    restored_img=Image.new("L",(width,height))
    restored_img.putdata(final_pixels.flatten().tolist())
    save_path = os.path.join(current_dir, output_file_name)
    restored_img.save(save_path)
    print(f"Restored image saved as: {output_file_name}")

    if list(img.getdata())==final_pixels.flatten().tolist():
        print("Succesful:Original and restored image is same.")
    else:
        print("Error:The images are different.")

if __name__=="__main__":
    main()