'''
functions to implement least squares using gradient descent, stochastic gradient descent or normal equation

All functions return w and loss , which is the last weight vector of the method and the corresponding loss
'''

import numpy as np

from costs import *
from data_utility import *
from proj1_helpers import *

#*****************************************
# GRADIENT DESCENT METHODS
#-----------------------------------------

def least_squares_GD(y, tx, initial_w, max_iters, gamma, all_step=False, printing=False, loss='mse', kind='cont'):
    """Gradient descent algorithm.
    Return: w, loss
    ******************
    all_step    If 'True' gives all the computed parameters and respective losses. False by default.
    printing    If 'True' print the loss and first 2 parameters estimate at each step. False by defalt.
    """
    # Define parameters to store w and loss
    ws = [initial_w]
    losses = []
    w = initial_w
    for n_iter in range(max_iters):
        # compute loss, gradient
        grad, loss = compute_gradient(y, tx, w, loss, kind)
        # gradient w by descent update
        w = w - gamma * grad
        # store w and loss
        ws.append(w)
        losses.append(loss)
        if printing:
            print("Gradient Descent({bi}/{ti}): loss={l}, w0={w0}, w1={w1}".format(
              bi=n_iter, ti=max_iters - 1, l=loss, w0=w[0], w1=w[1]))
    if all_step:
        return ws, losses
    else :
        return ws[-1], losses[-1]

def least_squares_SGD(y, tx, initial_w, batch_size, max_iters, gamma, all_step=False, printing=False, loss='mse', kind='cont'):
    """Stochastic gradient descent."""
    # Define parameters to store w and loss
    ws = [initial_w]
    losses = []
    w = initial_w

    for n_iter in range(max_iters):
        for y_batch, tx_batch in batch_iter(y, tx, batch_size=batch_size, num_batches=1):
            # compute a stochastic gradient and loss
            grad, _ = compute_gradient(y_batch, tx_batch, w, loss, kind)
            # update w through the stochastic gradient update
            w = w - gamma * grad
            # calculate loss
            loss = calculate_loss(y, tx, w, loss, kind)
            # store w and loss
            ws.append(w)
            losses.append(loss)
        if printing:
            print("Gradient Descent({bi}/{ti}): loss={l}, w0={w0}, w1={w1}".format(
              bi=n_iter, ti=max_iters - 1, l=loss, w0=w[0], w1=w[1]))
    if all_step:
        return ws, losses
    else :
        return ws[-1], losses[-1]

#************************************************
#LEAST SQUARES
#------------------------------------------------

def least_squares(y, tx, loss='mse', kind='cont'):
    """
    Calculate the least squares solution.
    Returns w and mse loss.
    """
    w = np.linalg.solve(tx.T.dot(tx),tx.T.dot(y))

    return w, calculate_loss(y, tx, w, loss, kind)

def least_squares_p(y, tx, parameters, loss='mse', kind='cont'): #this is used to generalize regressions
    return least_squares(y, tx, loss, kind)

#**************************************************
# RIDGE REGRESSION
#--------------------------------------------------

def ridge_regression(y, tx, lambda_, loss='mse', kind='cont'):
    """implement ridge regression.
    Returns w and loss loss"""
    a = tx.T.dot(tx) + 2*tx.shape[0]*lambda_*np.identity(tx.shape[1])
    w = np.linalg.solve(a,tx.T.dot(y))
    return w, calculate_loss(y, tx, w, loss, kind)


#*************************************************
# Logistic regression
#-------------------------------------------------


def sigmoid(z):
    return np.exp(z)/(1+np.exp(z))

def Logistic_regression(y, x, w0, gamma = 0.1, lambda_ = 0, max_iters = 500):
    '''
    compute the logistic regression on the data x,y, return the probability to be 1 in the classification problem (0,1)
    y_proba1 = Logistic_regression(...)


    Have to add intercept to the data ! t
    '''
    w = w0
    for i in range(max_iters):
        w_old = w
        grad,err = compute_gradient(y,x,w,loss = "logistic")
        w = w -gamma*grad
        if max(abs(w_old-w)):
            break

    return w

def pred_logitstic(x,w):

    return sigmoid(x.dot(w))



#**************************************************
# GENERAL REGRESSION FUNCTION
#--------------------------------------------------

def regression(y, tx, method, parameters=None, loss='mse', kind='cont'):
    '''General regression function.
    Specify response y, features matrix tx, desired regression method and a parameters list formatted as follows.

    METHOD              PARAMETERS
    least squares       None
    ridge               [lambda_]

    '''
    reg_switcher = {
        'least squares': least_squares,
        'ridge': ridge_regression
    }

    reg = reg_switcher.get(method, least_squares)
    return reg(y, tx, parameters, loss, kind)


#**************************************************
# CROSS VALIDATION
#--------------------------------------------------



def CV(y,x,k_fold,model, *args_model):
    '''
    return an estimate of the expected predicted error outside of the train set for the model, using k fold cross validation
    *args_model are the parameter needed for the model to train (for example lambda for ridge,..,)

    estimate = CV(y,x,k_fold,model, *args_model)


    prediction = model(x_test,y_train,x_train,*args_model): model is a function that return the prediction classification for a specific model
    '''

    k_indices = build_k_indices(y, k_fold, seed = 1)
    errors = []

    for k in range(k_fold):
        #repartition of the different folds to either train or test
        x_te = x[k_indices[k]]
        y_te = y[k_indices[k]]
        k_complement = np.ravel(np.vstack([k_indices[:k],k_indices[k+1:]]))
        x_tr = x[k_complement]
        y_tr = y[k_complement]

        y_pred = model(x_te,y_tr,x_tr,*args_model)
        y_pred = categories(y_pred)
        errors.append(np.mean(abs(y_te-y_pred)))

    estimate = np.mean(errors)

    return estimate



def single_cross_validation(y, x, k_indices, k, method='least_squares', hyper_parameters=None, loss='mse', kind='cont'):
    """
    return the loss of any regression.

    For informations on methods and parameters and errors see respectively regression() and compute_loss().
    ATTENTION: as of this implementation, the error for test set is considered as if the estimation is CATEGORICAL

    """

    # get k'th subgroup in test, others in train
    x_te = x[k_indices[k]]
    y_te = y[k_indices[k]]
    k_complement = np.ravel(np.vstack([k_indices[:k],k_indices[k+1:]]))
    x_tr = x[k_complement]
    y_tr = y[k_complement]


    # regression using the method given
    w, single_loss_tr = regression(y_tr, x_tr, method, hyper_parameters, loss, kind)

    # calculate the loss for test data
    single_loss_te = calculate_loss(y_te, x_te, w, loss, kind)
    return w, single_loss_tr, single_loss_te

def cross_validation(y, x, k_fold, method='least_squares', degree=0, parameters=None, seed=1, loss='mse', kind='cont', only_best=True):
    '''
        Run ridge regression cross validation for parameters lambda in lambda.
        You can choose the loss you get and the kind of target.

        ATTENTION: degree is gonna be incorporated in parameters in later implementation.
    '''
    if parameters is None:
        hyper_parameters = None
    else:
        hyper_parameters = parameters.get('hyper_parameters', None)
    # split data in k fold
    k_indices = build_k_indices(y, k_fold, seed)
    # define lists to store the loss of training data and test data
    loss_tr = []
    loss_te = []
    w = []

    if degree>0 :
        # form data with polynomial degree
        tx = build_poly(x, degree)
        degree = 0


    # cross validation
    for hyper_parameter in hyper_parameters:
        single_loss_tr = np.zeros(k_fold)
        single_loss_te = np.zeros(k_fold)
        w_l = np.zeros((tx.shape[1],k_fold))
        for k in range(k_fold):
            w_l[:,k], single_loss_tr[k], single_loss_te[k] = single_cross_validation(y, tx, k_indices, k, method, degree, hyper_parameter, loss=loss, kind=kind)
        loss_tr.append(np.mean(single_loss_tr))
        loss_te.append(np.mean(single_loss_te))
        w.append(np.mean(w_l, axis=1))

    cross_validation_visualization(hyper_parameters, loss_tr, loss_te)

    #Routine to gest just best hyper_parameter
    if only_best:
        best_i = np.argmax(loss_te)
        return w[best_i], loss_tr[best_i], loss_te[best_i], hyper_parameters[best_i]


    return w, loss_tr, loss_te
