# example usage: python main.py
# vapoursynth does not have audio support and processing multiple files is not really possible
# hacky script to make batch processing with audio and subtitle support
# make sure tmp_dir is also set in inference.py
# maybe should pass arguments instead of a text file instead
import glob
import os
import shutil

input_dir = "/workspace/tensorrt/input/"
tmp_dir = "tmp/"
output_dir = "/workspace/tensorrt/output/"

# creating folders if they dont exist
if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)
if not os.path.exists(output_dir):
    os.mkdir(output_dir)
if os.path.exists(tmp_dir):
    shutil.rmtree(tmp_dir)
    os.mkdir(tmp_dir)

def upscale_directory(input_path) :

    files = glob.glob(input_path + "/**/*.mkv", recursive=True)
    files.sort()

    for f in files :

        # paths
        out_render_path = os.path.join(
            output_dir, os.path.splitext(os.path.basename(f))[0] + "_rendered.mkv"
        )
        mux_path = os.path.join(
            output_dir, os.path.splitext(os.path.basename(f))[0] + "_mux.mkv"
        )

        ### faster ###
        # x264 crf10 default preset [43fps]
        # os.system(
        #   f"vspipe -c y4m inference_batch.py --arg source='{f}' - | ffmpeg -y -i '{f}' -thread_queue_size 100 -i pipe: -map 1 -map 0 -map -0:v -max_interleave_delta 0 -scodec copy -crf 10 '{mux_path}'"
        # )

        # x264 crf10 preset slow [31fps]
        os.system(
            f"vspipe -c y4m ai.inference_batch.py --arg source='{f}' - | ffmpeg -y -i '{f}' -thread_queue_size 100 -i pipe: -map 1 -map 0 -map -0:v -max_interleave_delta 0 -scodec copy -crf 10 -preset slow '{mux_path}'"
        )

#This method will be called by watcher.py whenever a new mp4 if placed into 'inputs', such that all the files in
#inputs will be processed and outputed
def run() :
    upscale_directory(input_directory='inputs')

#This is a shortcut way to run process_directory() during testing, that in deployment will be deleted 
if __name__ == "__main__" :
    print()
    run()
    print()