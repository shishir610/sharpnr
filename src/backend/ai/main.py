# example usage: python main.py
# vapoursynth does not have audio support and processing multiple files is not really possible
# hacky script to make batch processing with audio and subtitle support
# make sure tmp_dir is also set in inference.py
# maybe should pass arguments instead of a text file instead
# main.py
import glob
import os
import shutil

# Define your directories
input_dir = "/workspace/tensorrt/input/"
tmp_dir = "tmp/"
output_dir = "/workspace/tensorrt/output/"

# Refactor the code to make it callable
def process_videos():
    files = glob.glob(input_dir + "**/*.mp4", recursive=True)
    files.sort()
     
    for f in files:
        # creating folders if they dont exist
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
            os.mkdir(tmp_dir)

        # paths
        out_render_path = os.path.join(
            output_dir, os.path.splitext(os.path.basename(f))[0] + "_rendered.mkv"
        )
        mux_path = os.path.join(
            output_dir, os.path.splitext(os.path.basename(f))[0] + "_mux.mkv"
        )

        # x264 crf10 preset slow [31fps]
        os.system(
            f"vspipe -c y4m inference_batch.py --arg source='{f}' - | ffmpeg -y -i '{f}' -thread_queue_size 100 -i pipe: -map 1 -map 0 -map -0:v -max_interleave_delta 0 -scodec copy -crf 10 -preset slow '{mux_path}'"
        )

if __name__ == '__main__':
    process_videos()