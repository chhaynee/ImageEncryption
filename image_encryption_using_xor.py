import numpy as np
from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog
import time
import sys
import threading

def to_binary(arr):
    """Converts a NumPy array of integers to a string of binary where each integer has a length of 8 bits."""
    binary_string = ""
    for value in arr:
        binary_val = format(value, '08b')  # Convert to binary with leading zeros
        binary_string += binary_val
    return binary_string

def binary_to_array(binary_string):
    """Converts a binary string back to a numpy array of integers."""
    chunks = [binary_string[i:i+8] for i in range(0, len(binary_string), 8)]
    integers = [int(chunk, 2) for chunk in chunks]
    return np.array(integers, dtype=np.uint8)

def image_to_binary(user_image):
    img = Image.open(user_image)
    resize_img = img.resize((2048, 2048))
    rgb_img = resize_img.convert("RGB")
    rgb_array = np.array(rgb_img)
    conv_2arr_1arr = rgb_array.flatten()
    conv_1arr_binary = to_binary(conv_2arr_1arr)
    return conv_1arr_binary, rgb_array.shape

def xor_operation(str1, str2):
    binary_xor_result = ""
    for i in range(len(str1)):
        binary_xor_result += "0" if str1[i] == str2[i] else "1"
    return binary_xor_result

def save_image(binary_string, shape, output_path):
    """Convert binary string to image and save it."""
    arr = binary_to_array(binary_string)
    img_array = arr.reshape(shape)
    img = Image.fromarray(img_array, "RGB")
    img.save(output_path)
    return img

def loading_message(message, stop_event):
    """Display a loading message that runs until stop_event is set."""
    while not stop_event.is_set():
        for dots in range(1, 4):
            sys.stdout.write(f"\r{message}{'.' * dots}   ")
            sys.stdout.flush()
            time.sleep(0.5)
        sys.stdout.write("\r" + " " * (len(message) + 4) + "\r")  # Clear the line

def encrypt_image(pri_img, plain_img):
    """Encrypt image using XOR operation."""
    binary_pri_img, shape = image_to_binary(pri_img)
    binary_plain_img, _ = image_to_binary(plain_img)
    xor_result = xor_operation(binary_pri_img, binary_plain_img)
    return xor_result, shape, len(binary_pri_img)

def decrypt_image(encrypted_binary, key_image_path, shape, expected_length):
    """Decrypt image using provided key."""
    binary_key, key_shape = image_to_binary(key_image_path)
    
    if len(binary_key) != expected_length:
        raise ValueError("Invalid key: The provided key image has different dimensions")
    
    decrypted_binary = xor_operation(encrypted_binary, binary_key)
    decrypted_img = save_image(decrypted_binary, shape, "decrypted_image.png")
    return decrypted_img

def main():
    # Encryption phase
    pri_img = "Private_key.jpeg"
    plain_img = "Plain_image.jpeg"
    
    # Start loading message in a separate thread
    stop_event = threading.Event()
    loading_thread = threading.Thread(target=loading_message, args=("Encrypting image", stop_event))
    loading_thread.start()
    
    # Encrypt the image
    try:
        encrypted_binary, original_shape, key_length = encrypt_image(pri_img, plain_img)
    finally:
        stop_event.set()  # Stop loading message once encryption is complete
        loading_thread.join()  # Wait for loading thread to finish
    
    print("Encryption complete! Encrypted image saved as 'encrypted_image.png'")
    save_image(encrypted_binary, original_shape, "encrypted_image.png").show()
    
    # Decryption phase
    while True:
        print("\nPlease select the private key image to decrypt: ")
        key_path = filedialog.askopenfilename(title="Select Private Key Image")
        
        if not key_path:
            print("\nDecryption cancelled.")
            break

        # Start loading message in a separate thread for decryption
        stop_event.clear()
        loading_thread = threading.Thread(target=loading_message, args=("Decrypting image", stop_event))
        loading_thread.start()

        # Decrypt the image
        try:
            decrypted_img = decrypt_image(encrypted_binary, key_path, original_shape, key_length)
        except ValueError as e:
            print(f"Error during decryption: {e}")
            stop_event.set()
            loading_thread.join()
            continue
        finally:
            stop_event.set()  # Stop loading message once decryption is complete
            loading_thread.join()  # Wait for loading thread to finish

        print("Decryption successful! Image saved as 'decrypted_image.png'")
        decrypted_img.show()
        
        retry = input("\nWould you like to try another key? (y/n): ").lower()
        if retry != 'y':
            break

if __name__ == "__main__":
    main()
