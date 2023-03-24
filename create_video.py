import os
from moviepy.editor import *
import cv2
import numpy as np
import imageio
from scipy.interpolate import interp2d

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.video.VideoClip import ImageClip, TextClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx.resize import resize

# make these arguments
images_folder = '/home/lck/stable-diffusion-webui/outputs/txt2img-images/delicate and detailed ink drawing'
output_file = 'videos/rage/mooo.mp4'
audio_file = 'rage.mp4'
lines_file = 'rage.txt'
fps = 12  # Set the fps for the final video

def write_text_on_clip(clip, text, position, font_scale=1, font_thickness=2, font_color=(255, 255, 255)):
    for frame in clip.iter_frames():
        img = cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_color, font_thickness, cv2.LINE_AA)
        yield img

def crossfade_transition(clips, transition_duration):
    faded_clips = []
    for idx, clip in enumerate(clips[:-1]):
        clip_with_transition = clips[idx].crossfadein(transition_duration).crossfadeout(transition_duration)
        faded_clips.append(clip_with_transition.set_start(clips[idx].start))
    # Add the last clip without a transition
    faded_clips.append(clips[-1].set_start(clips[-1].start))
    return concatenate_videoclips(faded_clips)

def convert_timestamp_to_seconds(timestamp):
    parts = timestamp.split(':')
    if len(parts) == 1:
        return int(parts[0])
    elif len(parts) == 2:
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds

def extract_timestamps_and_poem_lines(lines_file):
    timestamps = []
    poem_lines = []
    
    with open(lines_file, 'r') as file:
        for line in file.readlines():
            line = line.strip()
            if '\t' in line:
                timestamp_end = line.find('\t')
            else:
                timestamp_end = line.find(' ')
            timestamp = line[:timestamp_end]
            timestamps.append(timestamp)
            
            poem_line = line[timestamp_end:].strip()
            poem_lines.append(poem_line)
    
    return timestamps, poem_lines


##
# create_video
# Creates a video from a list of image files and an audio file
# @param audio_file: The path to the audio file
# @param images_folder: The path to the folder containing the images
# @param output_file: The path to the output video file
##
def create_video(audio_file, output_file, images_folder):

    transition_duration = 1
    audio = AudioFileClip(audio_file)
    image_files = sorted([os.path.join(images_folder, f) for f in os.listdir(images_folder) if f.endswith('.jpg') or f.endswith('.png')])
    timestamps, poem_lines = extract_timestamps_and_poem_lines(lines_file)
    seconds_array = [convert_timestamp_to_seconds(ts) for ts in timestamps]
    clips = []

    for idx, image_file in enumerate(image_files):
        img = ImageClip(image_file)

        start_time = seconds_array[idx]
        end_time = seconds_array[idx + 1] if idx + 1 < len(seconds_array) else int(audio.duration)

        img = img.set_duration(end_time - start_time).set_start(start_time)

        clips.append(img)
        print(f"Clip {idx}: start_time = {start_time}, end_time = {end_time}, duration = {end_time - start_time}")

    video = crossfade_transition(clips, transition_duration)
    video = video.set_fps(fps).set_audio(audio)
    video.write_videofile(output_file, codec='libx264')

    print('Video created successfully!')


if __name__ == '__main__':
    create_video(audio_file, output_file, images_folder)
