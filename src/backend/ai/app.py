from flask import Flask, request, jsonify, url_for, send_from_directory
from pytube import YouTube
import os
from celery import Celery
from main import process_videos

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
input = "/input"
output = "/output"

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Define your REST endpoint
@app.route('/process-video', methods=['POST'])
def process_video():
    video_url = request.json.get('video_url')
    download_video(video_url)
    process_downloaded_video()
    processed_video_url = generate_video_url()
    return jsonify({ "processed_video_url" : processed_video_url }) 

def download_video(video_url):
    if not os.path.exists(input):
        os.makedirs(input)
    yt = YouTube(video_url)
    video_stream = yt.streams.get_highest_resolution()
    video_stream.download(output_path=input)
    print(f"Video '{yt.title}' downloaded successfully to {input}")

def process_downloaded_video():
    process_videos()

def serve_video(filename):
    return send_from_directory(output, filename)

def generate_video_url(filename):
    if not filename:
        return jsonify({'error': 'Missing filename'}), 400
    video_url = url_for('serve_video', filename=filename, _external=True)
    return video_url

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)