class Queue():
    def __init__(self):
        self.queue = []

    def enqueue(self, x):
        self.queue.append(x)

    def dequeue(self):
        try:
            tmp = self.queue[0]
            self.queue.remove(tmp)
            return tmp
        except IndexError:
            return None

    def is_empty(self):
        return len(self.queue) == 0

    def clear(self):
        self.queue = []

    def show(self):
        return self.queue