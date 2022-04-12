"""
2-input XOR example -- this is most likely the simplest possible example.
"""
from __future__ import print_function

import pickle
import os
import neat

import torch
from torch import nn
from torch import optim
import torchvision
import torchvision.transforms as transforms

import numpy as np

from NeCNN import visualize
from NeCNN.Method1.genome import NECnnGenome_M1
from NeCNN.Pytorch.pytorch_converter import create_CNN
from NeCNN.Pytorch.pytorch_helper import classification_error, train_pytorch

folder = "results"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Training on device {device}")
mnist_mean = 0.1307
mnist_sd = 0.3081
num_workers = 8
train_batch_size = 128
classification_batch_size = 2048
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((mnist_mean,), (mnist_sd,))])

# Create the data loaders for the train and test sets
trainset = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=train_batch_size, shuffle=True, num_workers=num_workers)
trainloader_2 = torch.utils.data.DataLoader(trainset, batch_size=classification_batch_size, shuffle=True,
                                            num_workers=num_workers)

testset = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=classification_batch_size, shuffle=False)


def eval_genome(genome, config):
    net = create_CNN(genome, config.genome_config)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(), lr=0.02, momentum=0.5)
    train_pytorch(net, optimizer, criterion, trainloader, device=device, printing_offset=-1)
    images, labels = next(iter(trainloader_2))
    images = images.to(device)
    labels = labels.to(device)
    net.to(device)
    outputs = net(images)
    loss = criterion(outputs, labels)
    fitness = 1 / (1 + loss.item())
    print(
        f"Genome: {genome.key} Loss: {loss.item()} Fitness: {fitness}")
    genome.set_fitness(fitness)


def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        eval_genome(genome, config)


def run(config_file):
    # Load configuration.
    config = neat.Config(NECnnGenome_M1, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)
    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    checkpoints = neat.Checkpointer(generation_interval=10, time_interval_seconds=300,
                                    filename_prefix=f"{folder}/neat-checkpoint-")
    p.add_reporter(checkpoints)

    # Run for up to 100 generations.
    winner = p.run(eval_genomes, 1)

    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

    # Show output of the most fit genome against training data.
    winner_net = create_CNN(winner, config.genome_config)

    print(f'\nClassification Error: {classification_error(winner_net, testloader, device=device)}')  #

    with open(f'{folder}/stats.pickle', 'wb') as f:
        pickle.dump(stats, f)
    with open(f'{folder}/winner.pickle', 'wb') as f:
        pickle.dump(winner, f)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward-cnn1-test')
    run(config_path)