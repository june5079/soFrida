import logging
import queue
from logging.handlers import QueueHandler, QueueListener
import json
# Queue Logger
class sfLogger:
    def __init__(self, logger_name):
        self.format =  logging.Formatter("%(message)s")
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        self.queue_handler.setFormatter(self.format)
        self.logger = logging.getLogger(logger_name)
        self.logger.addHandler(self.queue_handler)
        self.logger.setLevel(logging.DEBUG)
        self.listener = QueueListener(self.log_queue, self.queue_handler)
        self.isStop = False

    def start(self):
        print("logger.start()")
        self.listener.start()
        self.isStop = False

    def loggenerator(self):
        print("logger.loggenerator()")
        while self.isStop == False:
            yield self.log_queue.get().getMessage()

    def stop(self):
        print("logger.stop()")
        print("before stop length "+str(self.log_queue.qsize()))
        self.listener.stop()
        self.isStop = True
        while self.log_queue.empty() == False:
            print("throw "+str(self.log_queue.get().getMessage()))
        print("after stop length "+str(self.log_queue.qsize()))
        
# if file logging needed:
class sfFileLogger:
    def __init__(self, filename):
        self.filename = filename
        self.filelogger = logging.getLogger("soLogger")
        self.filelogger.setLevel(logging.INFO)        
        self.formatter = logging.Formatter('%(levelname)s - %(message)s')
        self.file_handler = logging.FileHandler(self.filename + ".log")
        self.file_handler.setFormatter(self.formatter)
        self.filelogger.addHandler(self.file_handler)

