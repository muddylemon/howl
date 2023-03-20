import os
from moviepy.editor import *
import numpy as np
import imageio
from scipy.interpolate import interp2d

mp3_file = 'howl.mp3'
images_folder = 'sets/ballpoint/'
output_file = 'videos/howl_ballpoint.mp4'
fps = 24  # Set the fps for the final video
timestamps_file_path = 'timestamps.txt'

def interpolate_frames(img1, img2, num_frames):
    im1 = imageio.imread(img1)
    im2 = imageio.imread(img2)

    x = np.linspace(0, 1, im1.shape[1])
    y = np.linspace(0, 1, im1.shape[0])

    f1_r = interp2d(x, y, im1[:, :, 0].astype(np.float64), kind='linear')
    f1_g = interp2d(x, y, im1[:, :, 1].astype(np.float64), kind='linear')
    f1_b = interp2d(x, y, im1[:, :, 2].astype(np.float64), kind='linear')

    f2_r = interp2d(x, y, im2[:, :, 0].astype(np.float64), kind='linear')
    f2_g = interp2d(x, y, im2[:, :, 1].astype(np.float64), kind='linear')
    f2_b = interp2d(x, y, im2[:, :, 2].astype(np.float64), kind='linear')

    interpolated_frames = []
    for t in np.linspace(0, 1, num_frames + 2)[1:-1]:
        im_interpolated = np.zeros_like(im1)
        im_interpolated[:, :, 0] = f1_r(x, y) * (1 - t) + f2_r(x, y) * t
        im_interpolated[:, :, 1] = f1_g(x, y) * (1 - t) + f2_g(x, y) * t
        im_interpolated[:, :, 2] = f1_b(x, y) * (1 - t) + f2_b(x, y) * t
        interpolated_frames.append(im_interpolated.astype(np.uint8))

    return interpolated_frames

def crossfade_transition(clips, transition_duration):
    faded_clips = []
    for idx, clip in enumerate(clips[:-1]):
        clip_with_transition = clips[idx].crossfadein(transition_duration).crossfadeout(transition_duration)
        faded_clips.append(clip_with_transition.set_start(clips[idx].start))
    # Add the last clip without a transition
    faded_clips.append(clips[-1].set_start(clips[-1].start))
    return concatenate_videoclips(faded_clips)

def interpolation_transition(image_files, transition_duration, fps):
    interpolated_clips = [ImageClip(image_files[0])]

    for idx in range(1, len(image_files)):
        img1_file = image_files[idx - 1]
        img2_file = image_files[idx]

        # Calculate the number of interpolation frames
        num_frames = int(fps * transition_duration)

        # Interpolate frames
        interpolated_frames = interpolate_frames(img1_file, img2_file, num_frames)

        # Create ImageClips from the interpolated frames
        frame_clips = [ImageClip(frame).set_duration(1 / fps) for frame in interpolated_frames]

        # Add the frame clips to the list
        for frame_clip in frame_clips:
            interpolated_clips.append(frame_clip.set_start(interpolated_clips[-1].end))

        # Add the next main clip
        interpolated_clips.append(ImageClip(img2_file).set_start(interpolated_clips[-1].end))

    return concatenate_videoclips(interpolated_clips)

def apply_transition(transition_type, clips, transition_duration, fps):
    if transition_type == 'crossfade':
        return crossfade_transition(clips, transition_duration)
    # elif transition_type == 'interpolation':
        # return interpolation_transition(image_files, transition_duration, fps)
    else:
        raise ValueError("Invalid transition type. Choose either 'crossfade' or 'interpolation'.")



def create_video(mp3_file, images_folder, output_file, transition_type='crossfade', transition_duration=1):
    # Read the MP3 file
    audio = AudioFileClip(mp3_file)

    # Get the list of image files
    image_files = sorted([os.path.join(images_folder, f) for f in os.listdir(images_folder) if f.endswith('.jpg') or f.endswith('.png')])

    def extract_timestamps(file_path):
        timestamps = []
        
        with open(file_path, 'r') as file:
            for line in file.readlines():
                line = line.strip()
                if '\t' in line:
                    timestamp_end = line.find('\t')
                else:
                    timestamp_end = line.find(' ')
                timestamp = line[:timestamp_end]
                timestamps.append(timestamp)
        
        return timestamps

    timestamps = extract_timestamps(timestamps_file_path)
    print(timestamps)


    # # Set your timestamps for each line in the poem
    # timestamps = [
    #     '0:00', '0:05', '0:14', '0:24', '0:34', '0:42', '0:53', '1:02', '1:09', '1:16', '1:25', '1:31', '1:40', '1:43', '1:46', '1:48', '1:51',
    #     '1:57', '2:03', '2:09', '2:14', '2:18', '2:30', '2:38', '2:47', '2:56', '3:05', '3:12', '3:20', '3:27', '3:35', '3:45', '3:52',
    #     '3:59', '4:07', '4:13', '4:18', '4:29', '4:40', '4:46', '4:52', '4:57', '5:03', '5:07', '5:12', '5:19', '5:25', '5:31', '5:42',
    #     '5:52', '5:54', '5:57', '6:00', '6:08', '6:15', '6:27', '6:31', '6:35', '6:39', '6:43', '6:49', '6:53', '7:00', '7:09', '7:12',
    #     '7:18', '7:23', '7:24', '7:33', '7:39', '7:45', '7:51', '7:57', '8:00', '8:03', '8:11', '8:19', '8:26', '8:31', '8:36', '8:39',
    #     '8:42', '8:47', '8:50', '8:54', '9:00', '9:04', '9:08', '9:17', '9:18', '9:26', '9:40', '9:50', '9:57', '10:13', '10:22', '10:32',
    #     '10:47', '10:54', '11:10', '11:19', '11:26', '11:34', '11:51', '12:00', '12:09', '12:14', '12:22', '12:38', '12:48', '12:58',
    #     '13:15', '13:24', '13:42', '13:53', '14:04', '14:18', '14:22', '14:28', '14:32', '14:36', '14:39', '14:42', '14:46', '14:47',
    #     '14:48', '14:50', '14:52', '14:54', '14:56', '14:58', '15:04', '15:10', '15:14', '15:20', '15:24', '15:26', '15:35', '15:40',
    #     '15:44', '15:47', '15:50', '16:00', '16:10', '16:13', '16:17', '16:21', '16:25', '16:30', '16:36', '16:47', '16:56', '17:03', 
    #     '17:06', '17:08', '17:15', '17:20', '17:39', '17:45', '17:50','17:53', '17:58', '18:02', '18:09', '18:14', '18:18', '18:25', 
    #     '18:29', '18:35', '18:45', '18:53', '19:02', '19:10', '19:16', '19:25', '19:38', '19:53', '20:00'
    # ]


    def convert_to_seconds(timestamp):
        parts = timestamp.split(':')
        if len(parts) == 1:
            return int(parts[0])
        elif len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds

    seconds_array = [convert_to_seconds(ts) for ts in timestamps]
    print(seconds_array)

    clips = []
    for idx, image_file in enumerate(image_files):
        img = ImageClip(image_file)

        start_time = seconds_array[idx]
        end_time = seconds_array[idx + 1] if idx + 1 < len(seconds_array) else int(audio.duration)

        img = img.set_duration(end_time - start_time).set_start(start_time)
        clips.append(img)
        print(f"Clip {idx}: start_time = {start_time}, end_time = {end_time}, duration = {end_time - start_time}")

    transition_duration = 3  # Set the duration of the transition in seconds

    video = apply_transition(transition_type, clips, transition_duration, fps)
    video = video.set_fps(fps).set_audio(audio)
    video.write_videofile(output_file, codec='libx264')
    print('Video created successfully!')


if __name__ == '__main__':
    create_video(mp3_file, images_folder, output_file, transition_type='crossfade')

    # output_file = 'howl_pen_interpolation.mp4'
    # create_video(mp3_file, images_folder, output_file, transition_type='interpolation')