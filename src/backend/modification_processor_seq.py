#IMPORTS:
import os
import time
import cv2
import modifiers as mod

#PROCESSING METHODS:

#Processes the video at input_directory/file_name and places the processed video at path
#output_directory/{file_name}_{string representation of modification}, and deletes the original 
#video to at path input_directory/file_name to save space
def process_file(file_name, input_directory, output_directory, modification) :

    input_path = os.path.join(input_directory, file_name)
    output_path = os.path.join(output_directory, f"{os.path.splitext(file_name)[0]}_{modification.__doc__}.mkv")
    print(f"      -- Begin processing {input_path} into {output_path} with modification {modification.__doc__}:")

    # Open the video file
    cap = cv2.VideoCapture(input_path)

    # Get video details
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(5)

    # Define the codec and create VideoWriter object
    #H264 is a lossless encoder so we don't loose video quality (makes IO take ≈ 25% longer, but the task
    #is compute bound so it doesn't matter)
    fourcc = cv2.VideoWriter_fourcc(*'H264') 
    first_output_frame = modification(cap.read()[1])
    height, width, _ = first_output_frame.shape
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    out.write(first_output_frame)

    start_time = time.time()
    # For each frame in the video, write the modified frame to the output video
    for frame_index in range(1, total_frames):
        _, frame = cap.read()
        modified_frame = modification(frame) #computationally expensive ML evaulation step 
        out.write(modified_frame) 
        if( frame_index % 50 == 0 ) : 
            running_fps = frame_index/(time.time() - start_time)
            eta = (total_frames - frame_index)/(running_fps*60)
            print(f"         * running fps: {running_fps:6.2f} | outputed frame {frame_index:<6}/{total_frames:<6}: completion {(100*frame_index/total_frames):5.2f}% | ETA: {eta:6.2f} min.")

    print(f"      -- Finished processing {input_path} into {output_path}.")
    out.release()
    cap.release()
    cv2.destroyAllWindows()

    #delete the now-processed file (commented out for convenience of testing)
    #os.remove(input_path) 

#Splits each video in input_directory into video segments that are 300 seconds long each using split_video() (300 is a magic
#number I found that worked well in tests so for now I'm just going with it, will do more thorough tests later),
#then runs process_file() on each of the video segments in inputs in parallel to ultimately process all the files in the directory
def process_directory(input_directory, output_directory, modification) :

    print(f"---- Begin processing directory '{input_directory}' into directory '{output_directory}' with modification {modification.__doc__} ----\n")
    
    start_time = time.time()
    
    video_files = [file_name for file_name in os.listdir(input_directory) 
                    if file_name.endswith((".mp4"))]
    video_files.sort() #Sort the videos so the ones earlier in the video will be processed first
    
    overhead_time = time.time() - start_time
    
    #process the videos sequentially
    start_time = time.time()
    for file_name in video_files : 
        process_file(file_name, input_directory, output_directory, modification)                  
    process_time = time.time() - start_time

    print(f"\n---- Finished processing directory '{input_directory}' into directory '{output_directory}' with modification {modification.__doc__} ----")
    print(f"        * overhead_time = {round(overhead_time, 3)} sec.")
    print(f"        * process_time  = {round(process_time/60, 3)} min.")

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
