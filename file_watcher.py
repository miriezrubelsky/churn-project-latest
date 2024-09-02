import os
import time
import subprocess
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from prometheus_client import start_http_server
import threading


metrics_server_started = threading.Event()


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FileWatcherHandler(FileSystemEventHandler):
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.csv'):
            logger.info(f"New file detected: {event.src_path}")
            self.process_file(event.src_path)

    def process_file(self, file_path):
        # Define the output file path
        file_name = os.path.basename(file_path)
        output_file = os.path.join(self.output_dir, file_name)

        # Run the pipeline script
        command = [
            'python', 'prediction_batch_pipeline.py',
            '--input', file_path,
            '--output', output_file,
            '--runner', 'DirectRunner'
        ]
        try:
            logger.info(f"Processing file: {file_path}")
            subprocess.run(command, check=True)
            logger.info(f"Processed file: {file_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to process file {file_path}: {e}")


def start_metrics_server(port=8000):
    try:
        logger.info(f"Starting Prometheus metrics server on port {port}")
        start_http_server(port, addr='0.0.0.0')
        metrics_server_started.set()
        logger.info("Metrics server started successfully.")
    except OSError as e:
        logger.error(f"Error starting metrics server: {e}")

def start_file_watcher(input_dir, output_dir):
    event_handler = FileWatcherHandler(input_dir, output_dir)
    
    observer = Observer()
    observer.schedule(event_handler, path=input_dir, recursive=False)
    observer.start()
    logger.info(f"Watching directory: {input_dir}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":

    if not metrics_server_started.is_set():
        metrics_thread = threading.Thread(target=start_metrics_server, args=(8000,))
        metrics_thread.daemon = True  # Ensures the thread exits when the main program exits
        metrics_thread.start()
    # Input and output directories
    input_directory = '/code/input-files'
    output_directory = '/code/output-files'

    start_file_watcher(input_directory, output_directory)
