#VNG © 2024 by Neyunse (https://bsky.app/profile/neyunse.verified.unsetsoft.com) is licensed under Creative Commons Attribution-NoDerivatives 4.0 International. 
#To view a copy of this license, visit https://creativecommons.org/licenses/by-nd/4.0/

import sys
import os
import numpy as np
from moviepy import *
from PIL import Image, ImageDraw, ImageColor
import sounddevice as sd
import soundfile as sf
import uuid
import keyboard   
import time


FILE_NAME = "voice_note"
FONT_PATH = "resources/Roboto-Bold.ttf"
OUTPUT_AUDIO = "temp/audio.wav"
OUTPUT_VIDEO = f"out/{FILE_NAME}_{uuid.uuid4()}.mp4"
BACKGROUND_COLOR = (0, 0, 0)
PROFILE_IMAGE_NAME = "default_profile_image"
PROFILE_IMAGE_PATH = f"resources"
CUSTOM_TEXT = "#Voice" 
DURATION = 20  # Maximum recording duration 20s
FPS = 60
FONT_COLOR = "#fff"
TEXT_X = 1800

def list_microphones():
    print("Available audio devices:")
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if device["max_input_channels"] > 0:  # Only list input devices
            print(f"{idx}: {device['name']}")

 

def record_audio(filename, max_duration, device=None):
    print("Recording audio... Press 'r' to stop.")

    fs = 44100  # Sample rate
    channels = 2  # Stereo
    dtype = 'float32'  # Audio format
    block_duration = 1  # Duration of each block to record (in seconds)

    # Initialize empty list to store audio
    audio_data = []

    # Define a callback function to record in chunks
    def callback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        audio_data.append(indata.copy())

    # Open an input stream for recording
    with sd.InputStream(samplerate=fs, channels=channels, dtype=dtype, callback=callback, device=device):
        start_time = time.time()

        while True:
            # Check if the user pressed 'r' to stop recording
            if keyboard.is_pressed('r'):
                print("Recording stopped.")
                break

            # Check if we've reached the max duration
            elapsed_time = time.time() - start_time
            if elapsed_time >= max_duration:
                print(f"Maximum duration reached: {elapsed_time:.2f} seconds.")
                break

            time.sleep(0.1)  # Sleep for a short time to check the key press

    # Concatenate all recorded blocks
    audio_data = np.concatenate(audio_data, axis=0)

    # Save the recorded audio to a file
    sf.write(filename, audio_data, fs)

    # Calculate actual duration
    actual_duration = len(audio_data) / fs
    print(f"Audio stored in {filename}. Actual duration: {actual_duration:.2f} seconds.")

    return actual_duration

def create_video(font, background_color, profile_path, audio_path, text, duration):
    
    profile = ImageClip(profile_path).with_duration(duration).resized(height=240).with_position("center")

    text_clip = TextClip(
        font,
        text,
        font_size=23,
        color=FONT_COLOR
    )
    text_clip = text_clip.with_duration(duration).with_position((TEXT_X, 1080 - 50))

    audio = AudioFileClip(audio_path)


    video = CompositeVideoClip([profile, text_clip], size=(1920, 1080), bg_color=background_color)
    video = video.with_audio(audio)

    video.write_videofile(OUTPUT_VIDEO, fps=FPS, codec="libx264")
    print(f"Video created: {OUTPUT_VIDEO}")

    # remove temp files
    os.unlink(os.path.join("temp", f"{PROFILE_IMAGE_NAME}.png"))
    os.unlink(os.path.join("temp", "audio.wav"))
 



def hashtag():
    hashtag_text = input('Write a Hashtag (default is #Voice): ')
    text = None
    if len(hashtag_text) > 8:  # Limit the hashtag length to 7 characters
        print("Error: Max 8 characters")
        return hashtag()  # Recursively ask for input if too long
    if hashtag_text != "":
        text = hashtag_text
    else:
        text = "#Voice"

    return text

def device_select():
   
    device_select_index = input("Enter the index of the microphone you want to use (if you don't know use '-list' or 'default' to use the default microphone): ")

    if device_select_index != "":
        if device_select_index == "-list":
            list_microphones()
            return device_select()
        if device_select_index == "default":
            return None
        
        return int(device_select_index)
    return device_select()

def avatar_select():
   
    avatar_select_image_name = input("Enter the name of the avatar you want to use which is inside the resources folder (without the extension and be .jpg or use 'default'): ")

    if avatar_select_image_name != "":
        if avatar_select_image_name == "default":
            return PROFILE_IMAGE_NAME
        return avatar_select_image_name
    return avatar_select()

if __name__ == "__main__":
 

    # Ask the user to select a microphone
    device_index = device_select()

    bg_color = input('Color theme (voice note background color in hex default is #000): ')
    CUSTOM_TEXT = hashtag()

    if bg_color != "":
        BACKGROUND_COLOR = ImageColor.getcolor(bg_color.replace(" ", "").replace("\t", ""), "RGB")
    
    avatar = avatar_select()

    PROFILE_IMAGE_NAME = avatar

    img = Image.open(f"{PROFILE_IMAGE_PATH}/{PROFILE_IMAGE_NAME}.jpg")
    height, width = img.size
    new_width = 680
    new_height = 680

    img = img.resize((new_width, new_height), Image.LANCZOS)

    h, w = img.size

    lum_img = Image.new('L', [h, w], 0)

    draw = ImageDraw.Draw(lum_img)
    draw.pieslice([(0, 0), (h, w)], 0, 360, fill=255, outline="white")
    img_arr = np.array(img)
    lum_img_arr = np.array(lum_img)

    final_img_arr = np.dstack((img_arr, lum_img_arr))

    prf = Image.fromarray(final_img_arr).save(f"temp/{PROFILE_IMAGE_NAME}.png")
 
    PROFILE_IMAGE_PATH = f"temp/{PROFILE_IMAGE_NAME}.png"

    print("Info: you can stop the recording by pressing the 'r' key.")
    # Record the audio and get its actual duration
    audio_duration = record_audio(OUTPUT_AUDIO, DURATION, device_index)

    # Create video with the actual duration of the audio
    create_video(FONT_PATH, BACKGROUND_COLOR, PROFILE_IMAGE_PATH, OUTPUT_AUDIO, CUSTOM_TEXT, audio_duration)
