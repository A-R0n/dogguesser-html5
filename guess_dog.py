import sys
import time
from PIL import Image
import os

def guess_dog(file):
    gd = GuessDog(file)
    return gd.guess

class GuessDog:
    def __init__(self, file):
        type_file = type(file)
        print(f'type of file {type_file}')
        self.epoch_time = str(time.time_ns())
        self.file = file
        type_self_file = type(self.file)
        print(f'type of self.file {type_self_file}')
        self._open_with_pil()
        self._main()

    def _open_with_pil(self):
        self.img = Image.open(self.file).convert('RGB')
        print(f'reading image with PIL {self.img}')

    def _main(self):
        ## this is where we do our timm stuff
        self.guess = "cool"

if __name__ == '__main__':
    guess_dog(sys.argv[1])