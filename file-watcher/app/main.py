import asyncio
import logging
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.processor import FileProcessor
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FileWatcherHandler(FileSystemEventHandler):
    """Handle file system events for new files"""

    def __init__(self, processor: FileProcessor):
        self.processor = processor
        self.last_processed = {}

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        # Debounce: wait for file to be fully written
        time.sleep(1)

        logger.info(f"New file detected: {file_path}")
        asyncio.run(self.processor.process(file_path))


def main():
    """Main entry point for file watcher"""
    processor = FileProcessor()
    event_handler = FileWatcherHandler(processor)
    observer = Observer()
    observer.schedule(event_handler, settings.WATCH_PATH, recursive=False)
    observer.start()

    logger.info(f"Watching {settings.WATCH_PATH} for new files...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
