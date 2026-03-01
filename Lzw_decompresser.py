import numpy as np
from PIL import Image
import struct
import os

def lzw_decompress(compressed_data):
    """
    LZW kodlarını alır ve orijinal piksel dizisine geri döndürür.
    Sözlük 'on-the-fly' (çalışırken) yeniden inşa edilir.
    """
    dict_size = 256

    dictionary = {i: bytes([i]) for i in range(dict_size)}
    
    if not compressed_data:
        return b""


    prev_code = compressed_data[0]
    result = [dictionary[prev_code]]
    
    for code in compressed_data[1:]:
        if code in dictionary:
            entry = dictionary[code]
        elif code == dict_size:

            entry = dictionary[prev_code] + bytes([dictionary[prev_code][0]])
        else:
            raise ValueError(f"Hatalı LZW kodu: {code}")
            
        result.append(entry)

        dictionary[dict_size] = dictionary[prev_code] + bytes([entry[0]])
        dict_size += 1
        prev_code = code
        
    return b"".join(result)


binary_file = 'compressed_image.bin'

WIDTH, HEIGHT = 1920, 1080 

if not os.path.exists(binary_file):
    print(f"Hata: '{binary_file}' dosyası bulunamadı! Önce compressor kodunu çalıştırın.")
else:
    print(f"'{binary_file}' okunuyor...")
    

    loaded_indices = []
    with open(binary_file, 'rb') as f:
        while True:
            chunk = f.read(2) 
            if not chunk:
                break
            index = struct.unpack('>H', chunk)[0]
            loaded_indices.append(index)
            
    print(f"Toplam {len(loaded_indices)} LZW kodu okundu. Decompress işlemi başlıyor...")


    restored_bytes = lzw_decompress(loaded_indices)
    

    try:

        restored_img_array = np.frombuffer(restored_bytes, dtype=np.uint8).reshape((HEIGHT, WIDTH))
        

        output_name = 'restored_final.png'
        Image.fromarray(restored_img_array).save(output_name)
        print(f"Başarılı! Resim '{output_name}' olarak geri yüklendi.")
        
    except Exception as e:
        print(f"Hata: Resim boyutları eşleşmedi. {e}")