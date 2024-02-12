import sys
import time
from PIL import Image
import os
import timm
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform
import torch
# import urllib

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
        self._open_with_pil()
        self._main()

    def _open_with_pil(self):
        self.img = Image.open(self.file).convert('RGB')
        # print(f'reading image with PIL {self.img}')

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
            # print(f'topn_catid {self.topn_catid}')
            # print(f'topn_catid at index {self.topn_catid[i]}')
            try:
                idx_category = self.topn_catid[i]
                # print(f'idx category {idx_category}')
            except IndexError:
                continue
            if idx_category >= 151 and idx_category <= 275:
                # print(f'we found a dog')
                try:
                    category_name = self.categories[idx_category]
                    prob = str(round(float(self.topn_prob[i].item()*100), 1)) + "%"
                    print(f'category_name: {category_name}, prob: {prob}')
                except IndexError:
                    continue
            else:
                break
        idx_category = self.topn_catid[0]
        # print(f'idx category {idx_category}')
        if idx_category >= 151 and idx_category <= 275:
            self.top_guess = str(self.categories[self.topn_catid[0]]).title()

    def _main(self):
        self.tensor = self.transform(self.img).unsqueeze(0)
        self.output = self._get_output()
        self.probabilities = torch.nn.functional.softmax(self.output[0], dim=0)
        self.categories = self._structure_imagenet_classes()
        self.topn_prob, self.topn_catid = self._get_most_probable(3)
        self._display_results()

if __name__ == '__main__':
    guess_dog(sys.argv[1])