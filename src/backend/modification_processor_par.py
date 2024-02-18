#IMPORTS:
import os
import time
from joblib import Parallel, delayed
import cv2
import subprocess
import modifiers as mod
#ffmpeg must also be installed to execute the subprocess command in split_video()

#PROCESSING METHODS:

#Splits the video with path file_directory/file_name into mutliple videos that are duration 
#seconds long at paths file_directory/{index in video}_seg_{file_name}, and deletes the original 
#video to at path file_directory/file_name to save space
def split_video(file_name, file_directory, duration):
    if duration == -1 : return
    file_path = os.path.join(file_directory, file_name)
    subprocess.run([
        'ffmpeg',
        '-i', file_path,
        '-c', 'copy',
        '-f', 'segment',
        '-segment_time', str(duration),
        '-reset_timestamps', '1',
        os.path.join(file_directory, f'%03d_seg_{file_name}')
    ])
    #delete the now-processed file (commented out for convenience of testing)
    #os.remove(input_path) 

#Processes the video at input_directory/file_name and places the processed video at path
#output_directory/{file_name}_{string representation of modification}, and deletes the original 
#video to at path input_directory/file_name to save space
def process_file(file_name, input_directory, output_directory, modification) :

    input_path = os.path.join(input_directory, file_name)
    output_path = os.path.join(output_directory, f"{os.path.splitext(file_name)[0]}_{modification.__doc__}.mkv")
    print(f"      -- Begin processing {input_path} into {output_path}:")

    # Open the video file
    cap = cv2.VideoCapture(input_path)

    # Get video details
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = cap.get(5)

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    # For each frame in the video, write the modified frame to the output video
    while True:
        ret, frame = cap.read()
        if not ret : break
        out.write(modification(frame))
    
    out.release()
    cap.release()
    cv2.destroyAllWindows()

    #delete the now-processed segment file
    os.remove(input_path)

    print("     - ", file_name, "processed, outputted, and deleted.\n")

#Splits each video in input_directory into video segments that are 300 seconds long each using split_video() (300 is a magic
#number I found that worked well in tests so for now I'm just going with it, will do more thorough tests later),
#then runs process_file() on each of the video segments in inputs in parallel to ultimately process all the files in the directory
def process_directory(input_directory, output_directory, modification) :

    print(f"---- Begin processing directory '{input_directory}' into directory '{output_directory}' with modification {modification.__doc__} ----\n")
    
    start_time = time.time()

    #split each file in the input directory into segments so those segments 
    #can be processed in parallel
    video_files = [file_name for file_name in os.listdir(input_directory) 
                    if file_name.endswith((".mp4")) or file_name.endswith((".avi"))]
    for file_name in video_files :
        split_video(file_name, input_directory, 30)

    video_files = [file_name for file_name in os.listdir(input_directory) 
                    if file_name.endswith((".mp4")) or file_name.endswith((".avi"))]
    overhead_time = time.time() - start_time
    
    #process the videos in paralllel
    start_time = time.time()
    Parallel(n_jobs=-1)(delayed(process_file)(file_name, input_directory, output_directory, modification)
                        for file_name in video_files)
    process_time = time.time() - start_time

    print(f"\n---- Finished processing directory '{input_directory}' into directory '{output_directory}' with modification {modification.__doc__} ----")
    print(f"        * overhead_time = {round(overhead_time, 3)} sec.")
    print(f"        * process_time  = {round(process_time, 3)} sec.")

#This method will be called by watcher.py whenever a new mp4 if placed into 'inputs', such that all the files in
#inputs will be processed and outputed
def run() :
    process_directory(input_directory='inputs', 
                      output_directory='outputs', 
                      modification=mod.grayscale)

#This is a shortcut way to run process_directory() during testing, that in deployment will be deleted 
if __name__ == "__main__" :
    print()
    run()
    print()
