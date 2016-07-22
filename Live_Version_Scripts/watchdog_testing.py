#!/usr/bin/python 
import time
import Live_Database_Fill
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
class MyHandler(FileSystemEventHandler):
	def process(self, event):
		"""
		event.event_type 
			'modified' | 'created' | 'moved' | 'deleted'
		event.is_directory
			True | False
		event.src_path
			path/to/observed/file
		"""
		# the file will be processed there
		print event.src_path, event.event_type  # print now only for degug
	def create_process(self, event):
		folder='\\'.join(event.src_path.split('\\')[0:-1])
		print(folder)
		Live_Database_Fill.start(folder)
		
	def on_modified(self, event):
		self.create_process(event)
	def on_created(self, event):
		self.create_process(event)
	def on_deleted(self, event):
		self.process(event)
	def on_moved(self, event):
		self.process(event)

if __name__ == "__main__":
	starting_dir = raw_input("Please Enter Directory to Monitor:")
	event_handler = MyHandler()
	observer = Observer()
	observer.schedule(event_handler, path=starting_dir, recursive=True)
	observer.start()

	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		observer.stop()
	observer.join()
