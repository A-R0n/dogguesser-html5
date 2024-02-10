import sys
import time
from PIL import Image
import os

def guess_dog(file):
    gd = GuessDog(file)
    return gd.guess

class GuessDog:
    def __init__(self, file):
        self.epoch_time = str(time.time_ns())
        self.file = file
        self.p = self.epoch_time + "-" + self.file.filename
        self._save_file_locally()
        self._open_with_pil()
        self._main()
        ## make sure the file existed, which it does (local)
        # time.sleep(5)
        self._delete_local_copy()

    def _save_file_locally(self):
        print(self.p)
        self.file.save(self.p)

    def _open_with_pil(self):
        self.img = Image.open(self.p).convert('RGB')
        print(f'reading image with PIL {self.img}')

    def _main(self):
        ## this is where we do our timm stuff
        self.guess = "cool"

    def _delete_local_copy(self):
        os.remove(self.p)

if __name__ == '__main__':
    guess_dog(sys.argv[1])