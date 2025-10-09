class PixelRange:
    def __init__(self, pixelbuf, start, end):
        self._pixelbuf = pixelbuf
        self.start = start
        self.end = end

    def fill(self, color):
        for i in range(self.start, self.end):
            self._pixelbuf[i] = color

    def show(self):
        self._pixelbuf.show()

    def __len__(self):
        return self.end - self.start

    def __getitem__(self, key):
        return self._pixelbuf[self.start + key]
    
    def __setitem__(self, key, color):
        self._pixelbuf[self.start + key] = color
