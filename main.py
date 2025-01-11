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
import typer
import inquirer

bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

FILE_NAME = "voice_note"
FONT_PATH = os.path.abspath(os.path.join(bundle_dir, 'assets','Roboto-Bold.ttf'))
OUTPUT_AUDIO = "temp/audio.wav"
OUTPUT_VIDEO = f"out/{FILE_NAME}_{uuid.uuid4()}.mp4"
PROFILE_IMAGE_PATH = f"resources"
DURATION = 20  # Maximum recording duration 20s
FPS = 30
MAX_HASHTAG_CHARACTERS = 20
HASHTAG_FONT_SIZE = 28 # DEFAULT FONT SIZE
 

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

def create_video(font, profile_path, audio_path, text, duration, font_size, avatar_height, theme, video_size):
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
    video = CompositeVideoClip([profile, text_clip], size=video_size, bg_color=video_bg_color)
    video = video.with_audio(audio)

    video.write_videofile(OUTPUT_VIDEO, fps=FPS, codec="libx264")
    print(f"Video created: {OUTPUT_VIDEO}")


def display_color(hexcolor, string):
    os.system("color")
    hexcolor = hexcolor.replace("#", "")
    r,g,b = bytes.fromhex(hexcolor)

    start = f"\x1b[38;2;{r};{g};{b}m"
    end = "\x1b[0m"


    return f"{start}{string}{end}"

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

        default_avatar_rgb = Image.fromarray(default_avatar_arr).save(f"resources/default.jpg")


def avatar_sug(_text, state):
    onlyfiles = [f.replace(".jpg", "") for f in os.listdir(PROFILE_IMAGE_PATH) if os.path.isfile(os.path.join(PROFILE_IMAGE_PATH, f)) and f.lower().endswith(".jpg")]
    return onlyfiles[state % len(onlyfiles)]

def App():
    _init_files()

    questions = [
        inquirer.List("video_size", message="Choce the video size", choices=["default", "short"], default="default"),
        inquirer.List("color_theme", message="Choce the color theme", choices=["default", "purple", "DarkPurple", "coffe"], default="default"),
        inquirer.Text("avatar", message="Enter the name of the avatar you want to use (image must be inside resources folder)", default="default", autocomplete=avatar_sug),
        inquirer.Text("hashtag", message="Write a Hashtag", default="Voice")
    ]

    answers = inquirer.prompt(questions)

    avatar = answers["avatar"]
    video_size = answers["video_size"]
    color_theme = answers["color_theme"]
    hashtag = answers["hashtag"]
    
 
    img = Image.open(f"{PROFILE_IMAGE_PATH}/{avatar}.jpg")
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

    prf = Image.fromarray(final_img_arr).save(f"temp/{avatar}.png")

    im_path = f"temp/{avatar}.png"
    
    hashtag_font_size = 34
    avatar_size = 270
    if video_size == "short":
        hashtag_font_size = 46
        avatar_size = 350

    print("Info: you can stop the recording by pressing the 'r' key.")
    # Record the audio and get its actual duration
    audio_duration = record_audio(OUTPUT_AUDIO, DURATION, None)


    # Create video with the actual duration of the audio
    create_video(FONT_PATH, im_path, OUTPUT_AUDIO, hashtag, audio_duration, hashtag_font_size, avatar_size, VIDEO_COLOR_THEME_LIST[color_theme], VIDEO_SIZE_LIST[video_size])

    # Delete temp when all is done

    os.unlink(OUTPUT_AUDIO)
    os.unlink(im_path)


if __name__ == "__main__":
 
    try:
        typer.run(App)    
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

