"""
2-input XOR example -- this is most likely the simplest possible example.
"""
from __future__ import print_function

import os
import pickle

import neat
import shutil

import multiprocessing as mp

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

folder = "results_test"


def run(config_file):
    # Load configuration.
    config = neat.Config(NECnnGenome_M1, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)
    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    with open(f"{folder}/stats.pickle", 'rb') as file:
        stats = pickle.load(file)

    with open(f"{folder}/winner.pickle", 'rb') as file:
        winner = pickle.load(file)

    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

    # Show output of the most fit genome against training data.
    winner_net = create_CNN(winner, config.genome_config)

    visualize.draw_net(config.genome_config.classification_genome_config, winner.classification,
                       filename=f"{folder}/net", view=False)
    visualize.plot_stats(stats, ylog=False, filename=f"{folder}/avg_fitness.svg", view=False)
    visualize.plot_species(stats, filename=f"{folder}/speciation.svg", view=False)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, f'{folder}/config')
    run(config_path)