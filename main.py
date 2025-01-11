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
import platform

bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

FILE_NAME = "voice_note"
FONT_PATH = os.path.abspath(os.path.join(bundle_dir, 'assets','Roboto-Bold.ttf'))
OUTPUT_AUDIO = "temp/audio.wav"
OUTPUT_VIDEO = f"out/{FILE_NAME}_{uuid.uuid4()}.mp4"
BACKGROUND_COLOR = (0, 0, 0)
PROFILE_IMAGE_NAME = "default_profile_image"
PROFILE_IMAGE_PATH = f"resources"
CUSTOM_TEXT = "Voice" 
DURATION = 20  # Maximum recording duration 20s
FPS = 30
VIDEO_SIZE = (0, 0) #default 0x0
MAX_HASHTAG_CHARACTERS = 20
HASHTAG_FONT_SIZE = 28 # DEFAULT FONT SIZE
AVATAR_SIZE=270

VIDEO_SIZE_LIST = {
    "default": (1920, 1080),
    "short": (1080, 1920),
}

VIDEO_COLOR_THEME_LIST = {
    "default": {
        "background_color": "#B9CEEB",
        "text_color": "#DEECFC"
    },
    "purple": {
        "background_color": "#BD83CE",
        "text_color": "#E5B0EA"
    },
    "DarkPurple": {
        "background_color": "#3B1E54",
        "text_color": "#9B7EBD"
    },
    "coffe": {
        "background_color": "#7C444F",
        "text_color": "#9F5255"
    }
}


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

def create_video(font, profile_path, audio_path, text, duration, font_size, avatar_height, theme):
    profile = ImageClip(profile_path).with_duration(duration).resized(height=avatar_height).with_position("center")
    video_font_color = ImageColor.getcolor(theme["text_color"], "RGB")
    text_clip = TextClip(
        font,
        f"#{text}",
        font_size=int(font_size),
        color=video_font_color
    )
    text_clip = text_clip.with_duration(duration).with_position((20, 50))

    audio = AudioFileClip(audio_path)

    video_bg_color = ImageColor.getcolor(theme["background_color"], "RGB")
    video = CompositeVideoClip([profile, text_clip], size=VIDEO_SIZE, bg_color=video_bg_color)
    video = video.with_audio(audio)

    video.write_videofile(OUTPUT_VIDEO, fps=FPS, codec="libx264")
    print(f"Video created: {OUTPUT_VIDEO}")

def hashtag():
    hashtag_text = input('Write a Hashtag (default is #Voice): ')
    text = None
    if len(hashtag_text) > MAX_HASHTAG_CHARACTERS:  # Limit the hashtag length to 7 characters
        print(f"Error: Max {MAX_HASHTAG_CHARACTERS} characters")
        return hashtag()  # Recursively ask for input if too long
    if hashtag_text != "":
        text = hashtag_text.replace("#","")
    else:
        text = "Voice"

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

def video_size(skipQuestion=False):
    change_size = "yes"

    if not skipQuestion:
        change_size = input("Do you what to change the video voice note size (use 'yes' or 'no'): ")
    
    if change_size != "":
        if change_size == "no":
            return VIDEO_SIZE_LIST["default"], "default"
        elif change_size == "yes":
            video_size_input = input("Chose the video size ['default' (1920x1080) or 'short' (1080x1920)]: ")
            if video_size_input in VIDEO_SIZE_LIST:
                return VIDEO_SIZE_LIST[video_size_input], video_size_input
            return video_size(True)
    return video_size(True)
    
def display_color(hexcolor, string):
    os.system("color")
    hexcolor = hexcolor.replace("#", "")
    r,g,b = bytes.fromhex(hexcolor)

    start = f"\x1b[38;2;{r};{g};{b}m"
    end = "\x1b[0m"


    return f"{start}{string}{end}"

def choce_color_theme(skipQuestion=False):
    change_theme = "yes"

    if not skipQuestion:
        change_theme = input("Do you what to change the color theme (video background & text color) (use 'yes' or 'no'): ")
    
    if change_theme != "":
        if change_theme == "no":
            return VIDEO_COLOR_THEME_LIST["default"]
        elif change_theme == "yes":
            video_theme_input = input("Chose the theme (use '-list' to see the theme list or use 'default'): ")
            if video_theme_input in VIDEO_COLOR_THEME_LIST:
                return VIDEO_COLOR_THEME_LIST[video_theme_input]
            elif video_theme_input == "default":
                return VIDEO_COLOR_THEME_LIST["default"]
            elif video_theme_input == "-list":
                def_bg_color = VIDEO_COLOR_THEME_LIST["default"]["background_color"]
                def_text_color = VIDEO_COLOR_THEME_LIST["default"]["text_color"]

                pur_bg_color = VIDEO_COLOR_THEME_LIST["purple"]["background_color"]
                pur_text_color = VIDEO_COLOR_THEME_LIST["purple"]["text_color"]

                Dpur_bg_color = VIDEO_COLOR_THEME_LIST["DarkPurple"]["background_color"]
                Dpur_text_color = VIDEO_COLOR_THEME_LIST["DarkPurple"]["text_color"]

                coffe_bg_color = VIDEO_COLOR_THEME_LIST["coffe"]["background_color"]
                coffe_text_color = VIDEO_COLOR_THEME_LIST["coffe"]["text_color"]

                print(f"[default]: background ({display_color(def_bg_color, def_bg_color)}) / text color ({display_color(def_text_color, def_text_color)})")
                print(f"[purple]: background ({display_color(pur_bg_color, pur_bg_color)}) / text color ({display_color(pur_text_color, pur_text_color)})")
                print(f"[DarkPurple]: background ({display_color(Dpur_bg_color, Dpur_bg_color)}) / text color ({display_color(Dpur_text_color, Dpur_text_color)})")
                print(f"[coffe]: background ({display_color(coffe_bg_color, coffe_bg_color)}) / text color ({display_color(coffe_text_color, coffe_text_color)})")



                
               
                return choce_color_theme(True)
            return choce_color_theme(True)
    return choce_color_theme(False)
    
def _init_files():
    temp_folder = os.path.join("temp")
    out_folder = os.path.join("out")
    res_folder = os.path.join("resources")

    if not os.path.exists(temp_folder):
        os.mkdir("temp")
    if not os.path.exists(out_folder):
        os.mkdir("out")
    if not os.path.exists(res_folder):
        os.mkdir("resources")
    
        default_avatar_rgb = Image.new('RGB', (400, 400), (228, 150, 150))

        default_avatar_arr = np.array(default_avatar_rgb)

        default_avatar_rgb = Image.fromarray(default_avatar_arr).save(f"resources/default_profile_image.jpg")


if __name__ == "__main__":
 
    try:
        _init_files()
    
        device_index = device_select()
        avatar = avatar_select()
        get_video_size, v_type = video_size()
        theme = choce_color_theme()

        CUSTOM_TEXT = hashtag()
        PROFILE_IMAGE_NAME = avatar
        VIDEO_SIZE = get_video_size

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

        if v_type == "short":
            HASHTAG_FONT_SIZE = 46
            AVATAR_SIZE = 350

        print("Info: you can stop the recording by pressing the 'r' key.")
        # Record the audio and get its actual duration
        audio_duration = record_audio(OUTPUT_AUDIO, DURATION, device_index)


        # Create video with the actual duration of the audio
        create_video(FONT_PATH, PROFILE_IMAGE_PATH, OUTPUT_AUDIO, CUSTOM_TEXT, audio_duration, HASHTAG_FONT_SIZE, AVATAR_SIZE, theme)

        # Delete temp when all is done

        os.unlink(OUTPUT_AUDIO)
        os.unlink(PROFILE_IMAGE_PATH)

    
    except Exception as e:
        traceback_template = '''Exception error:
  %(message)s\n

  %(plataform)s
 
  '''

        traceback_details = {
            'message' : e,
            'plataform': f"{platform.system()}-{platform.version()}",
        }    
        
        print(traceback_template % traceback_details)

        with open('traceback-error.txt', 'w') as f:
            f.write(traceback_template % traceback_details)
            f.close()

