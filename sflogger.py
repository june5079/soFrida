import logging
import queue
from logging.handlers import QueueHandler, QueueListener

class sfLogger:
    def __init__(self):
        self.format =  logging.Formatter("%(message)s")
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        self.queue_handler.setFormatter(self.format)
        self.logger = logging.getLogger("testlogger")
        self.logger.addHandler(self.queue_handler)
        self.logger.setLevel(logging.INFO)
        self.isStop = False

    def start(self):
        print("logger.start()")
        self.listener = QueueListener(self.log_queue, self.queue_handler)
        self.listener.start()
        self.isStop = False

    def logprint(self):
        print (self.log_queue.get().getMessage())

    def loggenerator(self):
        print("logger.loggenerator()")
        while self.isStop == False:
            yield "data: "+self.log_queue.get().getMessage()+"\n\n"

    def stop(self):
        print("logger.stop()")
        self.isStop = True
        self.log_queue.empty()
        
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