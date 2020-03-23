import torch
import torchvision
from util import initialize_torch
from net import Net

def main():
    _, device = initialize_torch()

    model = Net().to(device)
    model.load_state_dict(torch.load("mnist_cnn.pt"))

    data_path = './data/'
    train_dataset = torchvision.datasets.DatasetFolder(
        root=data_path,
        transform=torchvision.transforms.ToTensor()
    )
    train_loader = DataLoader(
        train_dataset,
        batch_size=16,
        num_workers=1,
        shuffle=True
    )

    for batch_idx, (data, target) in enumerate(train_loader):
    model()


if __name__ == "__main__":
    main()