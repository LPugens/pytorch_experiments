import argparse
import math
import pickle

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
from PIL import Image
from torch.optim.lr_scheduler import StepLR
from torchvision import datasets, transforms

from net import Net
from util import initialize_torch, create_dir_if_not_exists


def train_epoch(args, model, device, train_loader, optimizer, epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)

        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % 10 == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item()))


def test(args, model, device, test_loader):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            # sum up batch loss
            test_loss += F.nll_loss(output, target, reduction='sum').item()
            # get the index of the max log-probability
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)

    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))

    return correct/len(test_loader.dataset)


def image_load(inp):
    result = Image.open(inp)
    return result


def main():
    # Training settings
    args = parse_args()

    dir_name = 'output'
    create_dir_if_not_exists(dir_name)

    use_cuda, device = initialize_torch(args)

    tranformations = transforms.Compose([
        transforms.RandomRotation(degrees=180),
        transforms.RandomVerticalFlip(),
        transforms.RandomHorizontalFlip(),
        transforms.Resize(size=128),
        transforms.ToTensor(),
        transforms.Normalize((0,), (1,)),
    ])

    dataset = datasets.DatasetFolder(root=args.dataset_path, loader=image_load, transform=tranformations, extensions=('jpg',))

    train_proportion = 0.9
    train_length = math.floor(len(dataset)*train_proportion)
    test_length = math.ceil(len(dataset) - train_length)
    train_dataset, test_dataset = torch.utils.data.random_split(dataset, (train_length, test_length))

    kwargs = {'num_workers': 2, 'pin_memory': True} if use_cuda else {'num_workers': 2}
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, **kwargs)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=args.test_batch_size, shuffle=True, **kwargs)

    model = generate_model(device, dataset)

    optimizer = optim.Adadelta(model.parameters(), lr=args.lr)

    scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma)
    accuracy = 0
    last_accuracies = [0]*5
    for epoch in range(1, args.epochs + 1):
        train_epoch(args, model, device, train_loader, optimizer, epoch)
        torch.save(model.state_dict(), "output/model.pt")
        accuracy = test(args, model, device, test_loader)
        del last_accuracies[0]
        last_accuracies += [accuracy]
        if average(last_accuracies) > args.stop_accuracy:
            break
        scheduler.step()

def generate_model(device, dataset):
    model = torchvision.models.vgg19_bn(pretrained=True).to(device)
    model.classifier = nn.Sequential(
        nn.Linear(25088, 128),
        nn.BatchNorm1d(128),
        nn.Dropout(0.4),
        nn.Linear(128, len(dataset.classes)),
        nn.BatchNorm1d(len(dataset.classes)),
        nn.ReLU(),
        nn.LogSoftmax(dim=1)
    )
    return model


def average(last_accuracies):
    return sum(last_accuracies)/len(last_accuracies)


def parse_args():
    # Training settings
    parser = argparse.ArgumentParser(description='PyTorch MNIST Example')
    parser.add_argument('--batch-size', type=int, default=8, metavar='N',
                        help='input batch size for training')
    parser.add_argument('--test-batch-size', type=int, default=8, metavar='N',
                        help='input batch size for testing (default: 1000)')
    parser.add_argument('--epochs', type=int, default=100, metavar='N',
                        help='number of epochs to train')
    parser.add_argument('--lr', type=float, default=0.1, metavar='LR',
                        help='learning rate (default: 1.0)')
    parser.add_argument('--gamma', type=float, default=0.7, metavar='M',
                        help='Learning rate step gamma (default: 0.7)')
    parser.add_argument('--seed', type=int, default=1, metavar='S',
                        help='random seed (default: 1)')
    parser.add_argument('--dataset-path', type=str, default='datasets/everything',
                        help='The dataset path containing images from each class in each folder')
    parser.add_argument('--stop-accuracy', type=float, default=0.99,
                        help='The stop criteria accuracy.')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
