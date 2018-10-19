# -*- coding: utf-8 -*-
'''
Utility functions for data analysis and treatment.
Contains:
    split_data
    build_k_indices
    build_poly

'''

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set()
#*************************************************
# GENERAL FUNCTIONS
#-------------------------------------------------

#Data splitting
def split_data(x, y, ratio, seed=1):
    """
    split the dataset based on the split ratio. If ratio is 0.8
    you will have 80% of your data set dedicated to training
    and the rest dedicated to testing
    """
    # set seed
    np.random.seed(seed)

    set_size = len(y)
    n = int(np.floor(set_size*ratio))
    shuffled_i = np.random.permutation(set_size)
    train_i = shuffled_i[:n]
    test_i = shuffled_i[n:]
    x_train = x[train_i]
    x_test = x[test_i]
    y_train = y[train_i]
    y_test = y[test_i]

    return x_train, x_test, y_train, y_test

def build_k_indices(y, k_fold, seed):
    """build k indices for k-fold."""
    num_row = y.shape[0]
    interval = int(num_row / k_fold)
    np.random.seed(seed)
    indices = np.random.permutation(num_row)
    k_indices = [indices[k * interval: (k + 1) * interval]
                 for k in range(k_fold)]
    return np.array(k_indices)

def build_poly(x, degree):
    """polynomial basis functions for input data x, for j=0 up to j=degree.
    Return the augmented basis matrix tx."""

    n,p = x.shape
    tx = np.zeros((n,(degree*p)+1))
    tx[:,0] = 1
    for feature in range(p):
        for i in range(1,degree+1):
            tx[:,feature*degree+i]=(x[:,feature])**i
    return tx

def batch_iter(y, tx, batch_size, num_batches=1, shuffle=True):
    """
    Generate a minibatch iterator for a dataset.
    Takes as input two iterables (here the output desired values 'y' and the input data 'tx')
    Outputs an iterator which gives mini-batches of `batch_size` matching elements from `y` and `tx`.
    Data can be randomly shuffled to avoid ordering in the original data messing with the randomness of the minibatches.
    Example of use :
    for minibatch_y, minibatch_tx in batch_iter(y, tx, 32):
        <DO-SOMETHING>
    """
    data_size = len(y)

    if shuffle:
        shuffle_indices = np.random.permutation(np.arange(data_size))
        shuffled_y = y[shuffle_indices]
        shuffled_tx = tx[shuffle_indices]
    else:
        shuffled_y = y
        shuffled_tx = tx
    for batch_num in range(num_batches):
        start_index = batch_num * batch_size
        end_index = min((batch_num + 1) * batch_size, data_size)
        if start_index != end_index:
            yield shuffled_y[start_index:end_index], shuffled_tx[start_index:end_index]

#*************************************************
# PLOTS FUNCTIONS
#-------------------------------------------------

def scatter(x, which, other_f =False, against=None):
    '''Scatter plot of the features of x.
    Arguments:
        other_f: bool, if True give an argument in against
        against: an np.array of same size of x features against which you will have the scatterplot.'''

    for i in which:
        feature = x[:,i]
        if not other_f:
            if len(feature[feature==-999]) > 0: #If there is some misplaced value we do not include them in the scatterplot
                print("ATTENTION: missing values in {i}th feature removed!".format(i=i))
            feature = feature[feature>-999]
            against = range(len(feature))
        plt.scatter(feature, against)
        print("Scatter plot for {i}th feature :".format(i=i))
        plt.show()

def cross_validation_visualization(lambds, mse_tr, mse_te):
    """visualization the curves of mse_tr and mse_te."""
    plt.semilogx(lambds, mse_tr, marker=".", color='b', label='train error')
    plt.semilogx(lambds, mse_te, marker=".", color='r', label='test error')
    plt.xlabel("lambda")
    plt.ylabel("rmse")
    plt.title("cross validation")
    plt.legend(loc=2)
    plt.grid(True)
    plt.savefig("cross_validation")
