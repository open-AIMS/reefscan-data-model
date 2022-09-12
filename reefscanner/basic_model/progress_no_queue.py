import logging


class ProgressNoQueue(object):
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.value = 0
        self.max = 0

    def reset(self):
        self.value = 0

    def set_progress_max(self, i):
        self.max = i

    def set_progress_value(self):
        self.value += 1
        logging.info(f"processing {self.value} of {self.max}")

    def set_progress_label(self, message):
        logging.info(message)

