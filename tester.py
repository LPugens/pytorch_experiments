import torch
from torch import nn
import torchvision
from PIL import Image
from torchvision import transforms

from util import initialize_torch


def main():
    _, device = initialize_torch()

    model = torchvision.models.vgg19_bn(pretrained=False).to(device)
    model.classifier = nn.Sequential(
        nn.Linear(25088, 128),
        nn.Dropout(0.4),
        nn.Linear(128, 2),     
        nn.ReLU(),                
        nn.LogSoftmax(dim=1)
    )
    model.load_state_dict(torch.load("model.pt"))

    tranformations = transforms.Compose([
        transforms.RandomRotation(degrees=180),
        transforms.RandomVerticalFlip(),
        transforms.RandomHorizontalFlip(),
        transforms.Resize(size=128),
        # transforms.Grayscale(),
        transforms.ToTensor()
    ])

    img = Image.open('guampa_example2.jpg')
    img_tensor = tranformations(img)
    img_tensor = img_tensor.unsqueeze(0)
    classified_as = model(img_tensor).max(0)
    print(classified_as)

if __name__ == "__main__":
    main()
