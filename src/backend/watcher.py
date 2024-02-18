import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

#As long as main is running, the code in this file will run the processor whenever an mp4 is placed into the input directory
input_directory_path = 'C:/Users/High Definition/SharprAI/src/backend/ai/input'
# C:/Users/High Definition/SharprAI/src/backend/ai/input
# /workspace/tensorrt/input/

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_extension = os.path.splitext(event.src_path)[1]
            if file_extension.lower() == '.mp4' or file_extension.lower() == '.mkv':
                print("     -- watcher.py triggered: beginning processing", os.path.basename(event.src_path))
                
                os.chdir('C:/Users/High Definition/SharprAI/src/backend/ai')
                print("---------------cded----------------")
                
                print("---------------starting docker container----------------")

                # Start a Docker container and open an interactive shell
                process = subprocess.Popen(["docker-compose", "run", "--rm", "-T", "vsgan_tensorrt", "/bin/bash"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                # Send the python command to the container's shell
                command = 'python /workspace/tensorrt/main.py\n'
                output, errors = process.communicate(command.strip())

                # Print the output and errors if any
                print(output)
                if errors:
                    print(errors)

                print("     -- watcher.py terminated: finished processing", os.path.basename(event.src_path), "\n")
                
if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, input_directory_path, recursive=False)
    print(" ------------ \n Watcher started: Monitoring directory", input_directory_path, " \n ------------ \n ")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
