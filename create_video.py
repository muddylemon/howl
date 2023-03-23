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


mp3_file = 'rage.mp4'
file_path = 'rage.txt'
fps = 12  # Set the fps for the final video
transition_duration = 1  # Set the duration of the transition in seconds
images_folder = '/home/lck/stable-diffusion-webui/outputs/txt2img-images/first imagery inspired by the line'
output_file = 'videos/rage/flatdark.mp4'

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


def slide_transition(clips, transition_duration, direction='left'):
    slide_clips = [clips[0]]
    
    for i in range(len(clips) - 1):
        clip1 = clips[i]
        clip2 = clips[i+1]
        w, h = clips[0].size

        if direction == 'left':
            clip1 = clip1.set_position(lambda t: (int(-t * w / transition_duration), 0))
            clip2 = clip2.set_position(lambda t: (int(w - (t * w / transition_duration)), 0))
        elif direction == 'right':
            clip1 = clip1.set_position(lambda t: (int(t * w / transition_duration), 0))
            clip2 = clip2.set_position(lambda t: (int((t * w / transition_duration) - w), 0))
        elif direction == 'up':
            clip1 = clip1.set_position(lambda t: (0, int(-t * h / transition_duration)))
            clip2 = clip2.set_position(lambda t: (0, int(h - (t * h / transition_duration))))
        elif direction == 'down':
            clip1 = clip1.set_position(lambda t: (0, int(t * h / transition_duration)))
            clip2 = clip2.set_position(lambda t: (0, int((t * h / transition_duration) - h)))

        composite_clip = CompositeVideoClip([clip1, clip2.set_start(clip1.duration - transition_duration)]).set_duration(clip1.duration + transition_duration)
        slide_clips.append(composite_clip)

    return concatenate_videoclips([slide_clips[0]] + [clip.subclip(transition_duration) for clip in slide_clips[1:]])




def apply_transition(transition_type, clips, transition_duration):
    if transition_type == 'crossfade':
        return crossfade_transition(clips, transition_duration)
    elif transition_type == 'slide':
        return slide_transition(clips, transition_duration)
    else:
        raise ValueError("Invalid transition type")

def convert_to_seconds(timestamp):
    parts = timestamp.split(':')
    if len(parts) == 1:
        return int(parts[0])
    elif len(parts) == 2:
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds

def extract_timestamps_and_poem_lines(file_path):
    timestamps = []
    poem_lines = []
    
    with open(file_path, 'r') as file:
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
# @param mp3_file: The path to the MP3 file
# @param images_folder: The path to the folder containing the images
# @param output_file: The path to the output video file
# @param transition_type: The type of transition to use. Choose either 'crossfade' or 'interpolation'
# @param transition_duration: The duration of the transition in seconds
##
def create_video(mp3_file, images_folder, output_file, transition_type='crossfade', transition_duration=1):

    audio = AudioFileClip(mp3_file)
    image_files = sorted([os.path.join(images_folder, f) for f in os.listdir(images_folder) if f.endswith('.jpg') or f.endswith('.png')])
    timestamps, poem_lines = extract_timestamps_and_poem_lines(file_path)
    seconds_array = [convert_to_seconds(ts) for ts in timestamps]
    clips = []

    for idx, image_file in enumerate(image_files):
        img = ImageClip(image_file)

        start_time = seconds_array[idx]
        end_time = seconds_array[idx + 1] if idx + 1 < len(seconds_array) else int(audio.duration)

        img = img.set_duration(end_time - start_time).set_start(start_time)

        # if idx < len(poem_lines):
        #     text = TextClip(poem_lines[idx], fontsize=24, color='white', bg_color='black', size=img.size, print_cmd=False)
        #     img = CompositeVideoClip([img, text])

        clips.append(img)
        print(f"Clip {idx}: start_time = {start_time}, end_time = {end_time}, duration = {end_time - start_time}")


    video = apply_transition(transition_type, clips, transition_duration)
    video = video.set_fps(fps).set_audio(audio)
    video.write_videofile(output_file, codec='libx264')

    print('Video created successfully!')


if __name__ == '__main__':
    create_video(mp3_file, images_folder, output_file, transition_type='crossfade')
