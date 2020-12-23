'''
Processor containing general functions
'''
from random import random

def random_number(data_dict):
    '''
    Generates a random number
    args:
        data_dict (dict): Dictinoary with the configs

    return:
        (int): Random number
    '''
    return int(random() * 1000)
