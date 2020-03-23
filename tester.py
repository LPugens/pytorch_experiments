import torch
import torchvision
from PIL import Image
from torchvision import transforms

from net import Net
from util import initialize_torch


def main():
    _, device = initialize_torch()

    model = Net().to(device)
    model.load_state_dict(torch.load("model.pt"))

    tranformations = transforms.Compose([
        transforms.RandomRotation(degrees=180),
        transforms.RandomVerticalFlip(),
        transforms.RandomHorizontalFlip(),
        transforms.Resize(size=128),
        transforms.Grayscale(),
        transforms.ToTensor()
    ])

    img = Image.open('WIN_20200323_12_34_23_Pro.jpg')
    img_tensor = tranformations(img)
    print(img_tensor.shape)
    img_tensor.unsqueeze(-1)
    print(img_tensor.shape)
    print(model(img_tensor))

if __name__ == "__main__":
    main()
