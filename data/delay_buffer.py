from collections import deque


class CircularQueue:
    """
    A circular queue that stores a fixed number of items.

    Unlike a traditional ring buffer, reading from the queue does not
    remove the item from the queue. This allows the queue to be used
    to buffer incoming live game data in such a way that the first update is
    "instant", and the subsequent updates are delayed until the buffer is full.
    """

    def __init__(self, size):
        self.size = size
        self.queue = deque(maxlen=size)

    def push(self, data):
        self.queue.append(data)

    def peek(self):
        top = self.queue.popleft()
        self.queue.appendleft(top)
        return top

    def __len__(self):
        return len(self.queue)
