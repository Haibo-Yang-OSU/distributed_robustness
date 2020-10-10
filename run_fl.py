"""
federated learning FedAvg with both client side and server side optimizer
"""

import os
import sys
from datetime import datetime

from absl import flags
import logging

import torch

from utils import read_write_data
from trainer import FedAvg




def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path

def read_options():
    """
    read all the experiment parameter
    :return: None
    """
    flags.DEFINE_string('client_optimizer', 'sgd', 'name of the client optimizer.')
    flags.DEFINE_float('client_lr', 0.1, 'learning rate.')
    # flags.DEFINE_enum('client_lr_schedule', 'stepLR', ['constant', 'stepLR'],
    #                   'learning rate schedule of client.')
    # flags.DEFINE_integer('client_decay_epochs', 25, 'Number of epochs before decaying the learning rate.')
    # flags.DEFINE_float('client_lr_decay', 0.5, 'How much to decay the learning rate by at each stage.')

    flags.DEFINE_integer('client_batch_size', 64, 'Size of batches for training and eval.')

    flags.DEFINE_string('server_optimizer', 'sgd', 'name of the optimizer.')
    flags.DEFINE_float('server_lr', 1.0, 'learning rate.')
    # flags.DEFINE_enum('server_lr_schedule', 'constant', ['constant', 'exp_decay', 'inv_lin_decay', 'inv_sqrt_decay'],
                      # 'learning rate schedule of server.')
    # flags.DEFINE_integer('server_decay_epochs', 25, 'Number of epochs before decaying the learning rate.')
    # flags.DEFINE_float('server_lr_decay', 0.1, 'How much to decay the learning rate by at each stage.')

    flags.DEFINE_integer('clients_per_round', 100, 'Number of clients for each communication round.')
    flags.DEFINE_integer('num_epochs', 1, 'Number of epochs to local train.')
    flags.DEFINE_integer('num_round', 2, 'Number of communication round.')

    # compression options
    flags.DEFINE_enum('compressor', 'uniform_drop', ['none', 'signSGD', 'random_drop', 'topK', 'uniform_drop'], 'Which model to use for classification.')
    flags.DEFINE_float('compress_factor', 0.1, 'gradients compression factor')
    flags.DEFINE_bool('error_feedback', True, 'use error feedback or not')

    # modle options
    flags.DEFINE_enum('model', 'cnn', ['2nn', 'cnn', 'lstm', 'resnet18', 'vgg11'], 'Which model to use for classification.')

    # dataset and non iid details
    flags.DEFINE_string(
        'dataset', 'mnist',
        'Dataset name. Root name of the output directory: mnist, fmnist, cifar_10')
    flags.DEFINE_string(
        'dataset_name', 'all_data_1_digits_1_niid',
        'name of the data file for different partition for non-iid data')

    flags.DEFINE_integer('device', 0, 'CUDA device.')
    flags.DEFINE_bool('gpu', True, 'GPU or not, default to use GPU')

    # attack/defense options
    flags.DEFINE_enum('attack', 'byzantine', ['none', 'byzantine', 'backdoor'], 'Which attack')
    flags.DEFINE_float('attack_percentage', 0.2, 'attacker number %')
    flags.DEFINE_enum('defense', 'krum', ['none', 'krum'], 'Which defense')


    FLAGS = flags.FLAGS
    FLAGS(sys.argv)
    if not torch.cuda.is_available():
        FLAGS.gpu = False

def set_logging(log_name):
    now = datetime.now()
    current_time = now.strftime("%m_%d_%H_%M_%S")
    logger = logging.getLogger('main')
    logger.setLevel(level=logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    mkdir('log')
    file_handler = logging.FileHandler('log/' + log_name + current_time)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def main():
    read_options()

    FLAGS = flags.FLAGS


    logger = set_logging(str(FLAGS.model))

    dataset_options = 'model_{}_dataset_{}_iids_{}'.format(
        FLAGS.model, FLAGS.dataset, FLAGS.dataset_name
    )
    optimization_options = 'client_lr_{}_server_lr_{}_clients_per_round_{}_local_epochs_{}_num_round_{}'.format(
        FLAGS.client_lr, FLAGS.server_lr, FLAGS.clients_per_round, FLAGS.num_epochs, FLAGS.num_round
    )
    compression_options = 'compressor_{}_compressRate_{}_feedback_{}'.format(
        FLAGS.compressor, FLAGS.compress_factor, FLAGS.error_feedback
    )
    attack_options = 'attack_{}_percentage_{}_defense_{}'.format(
        FLAGS.attack, FLAGS.attack_percentage, FLAGS.defense
    )
    logger.info(dataset_options)
    logger.info(optimization_options)
    logger.info(compression_options)
    logger.info(attack_options)
    # data_inf is a tuple (client_id, grops, training_data, test_data
    data_inf = read_write_data.read_data()

    logger.info('Read data completed')

    fedavg_server = FedAvg.Server(data_inf)
    fedavg_server.train()


if __name__ == '__main__':
    main()










