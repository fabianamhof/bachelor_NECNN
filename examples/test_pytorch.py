import time

import torch
from torch import nn
from torch import optim
import torchvision
import torchvision.transforms as transforms

from NeCNN.Pytorch.net import Net
from NeCNN.Pytorch.pytorch_helper import classification_error, train_pytorch
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])

# Create the data loaders for the train and test sets
trainset = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=10, shuffle=True, num_workers=2)

testset = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=1000, shuffle=False, num_workers=2)

net = Net()
net.load_state_dict(torch.load("./results/model_good.pth"))
for param in net.features.parameters():
    param.requires_grad = False

classifier = [
    nn.Linear(320, 30),
    nn.ReLU(),
    nn.Linear(30, 10),
    nn.ReLU()
]

net.classifier = nn.Sequential(*classifier)

criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(net.parameters(), lr=0.01, momentum=0.5)
train_pytorch(net, optimizer, criterion, trainloader)
print(f"Classification: {classification_error(net, trainloader, 100)}")

torch.save(net.state_dict(), 'results/model.pth')