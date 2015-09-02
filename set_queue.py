import queue

class SetQueue(queue.Queue):
    # Initialize the queue representation
    def _init(self, maxsize):
        self.queue = set()

    # Put a new item in the queue
    def _put(self, item):
        if item not in self.queue:
            self.queue.add(item)

    # Get an item from the queue
    def _get(self):
        return self.queue.pop()
