import logging
import queue

logger = logging.getLogger(__name__)
class ProgressQueue(object):

    def __init__(self):
        logger.info("init progress queue")
        self.q = queue.Queue()

    def set_progress_max(self, i):
        logger.info("progress queue max " + str(i) )
        self.q.put(("max", i))

    def set_progress_value(self):
        logger.info("progress queue value ")
        self.q.put(("value", None))

    def set_progress_label(self, message):
        logger.info("progress queue label " + message )
        self.q.put(("label", message))

