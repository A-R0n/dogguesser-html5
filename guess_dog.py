import sys
import time
from PIL import Image, ImageFile
import timm
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform
import torch
from io import BytesIO

ImageFile.LOAD_TRUNCATED_IMAGES = True


imagenet_classes_file = "imagenet_classes.txt"
imagenet_classes_download = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"

def guess_dog(file):
    gd = GuessDog(file)
    return gd.top_guess

class GuessDog:
    def __init__(self, file):
        self.top_guess = 'N/A'
        self.model = timm.create_model("inception_v3", pretrained=True)
        self.model.eval()
        self.config = resolve_data_config({}, model=self.model)
        self.transform = create_transform(**self.config)
        self.epoch_time = str(time.time_ns())
        self.file = file
        self._main()

    def _get_output(self):
        with torch.no_grad():
            return self.model(self.tensor)
        
    def _structure_imagenet_classes(self):
        with open(imagenet_classes_file, "r") as f:
            return [s.strip() for s in f.readlines()] 
        
    def _get_most_probable(self, n):
        return torch.topk(self.probabilities, n)
    
    def _display_results(self):
        for i in range(self.topn_prob.size(0)):
            try:
                idx_category = self.topn_catid[i]
            except IndexError:
                continue
            if idx_category >= 151 and idx_category <= 275:
                try:
                    category_name = self.categories[idx_category]
                    prob = str(round(float(self.topn_prob[i].item()*100), 1)) + "%"
                    print(f'category_name: {category_name}, prob: {prob}')
                    self.top_guess = str(self.categories[idx_category]).title()
                    # return
                except IndexError:
                    continue
            else:
                continue


    def _main(self):
        print(f'opening with pil...')
        try:
            image_stream = BytesIO(self.file)
            img = Image.open(image_stream)
            img_converted = img.convert('RGB')
            self.tensor = self.transform(img_converted).unsqueeze(0)

        except ValueError:
            print(f'value error I/O operation')
            self.top_guess = 'N/A'
            return 'N/A'
        
        self.output = self._get_output()
        self.probabilities = torch.nn.functional.softmax(self.output[0], dim=0)
        self.categories = self._structure_imagenet_classes()
        self.topn_prob, self.topn_catid = self._get_most_probable(3)
        self._display_results()


if __name__ == '__main__':
    guess_dog(sys.argv[1])