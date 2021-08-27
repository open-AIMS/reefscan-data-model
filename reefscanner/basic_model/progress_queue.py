import queue


class ProgressQueue(object):

    def __init__(self):
        self.q = queue.Queue()

    def set_progress_max(self, i):
        self.q.put(("max", i))

    def set_progress_value(self):
        self.q.put(("value", None))

    def set_progress_label(self, message):
        self.q.put(("label", message))

