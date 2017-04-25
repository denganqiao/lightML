#!usr/bin/env python
#-*- coding:utf-8 -*-
"""
@author: Jianfeng Zhang
@date: 2017-04-11
"""



import numpy as np
import theano
import theano.tensor as T
from methods import sigmoid, softmax, dropout, floatX,random_weights, zeros





class NNLayer(object):


    def get_params_names(self):
        return ['UNK' if p.name is None else p.name for p in self.param]

    def save_model(self):
        return

    def load_model(self):
        return

    def updates(self):
        return

    def reset_state(self):
        return




class LSTMLayer(NNLayer):

    def __init__(self, num_input, num_hidden, input_layers=None, name="", go_backwards=False):
        """
        LSTM Layer
        Takes as input sequence of inputs, returns sequence of outputs
        """

        self.name = name
        self.num_input = num_input
        self.num_hidden = num_hidden

        if len(input_layers) >= 2:
            # axis=1  an row xiang jia
            self.X = T.concatenate([input_layer.output() for input_layer in input_layers], axis=1)
        else:
            self.X = input_layers[0].output()

        self.h0 = theano.shared(floatX(np.zeros(num_hidden)))
        self.s0 = theano.shared(floatX(np.zeros(num_hidden)))

        self.go_backwards = go_backwards

        self.W_gx = random_weights((num_input, num_hidden), name=self.name+"W_gx")
        self.W_ix = random_weights((num_input, num_hidden), name=self.name+"W_ix")
        self.W_fx = random_weights((num_input, num_hidden), name=self.name+"W_fx")
        self.W_ox = random_weights((num_input, num_hidden), name=self.name+"W_ox")

        self.W_gh = random_weights((num_hidden, num_hidden), name=self.name+"W_gh")
        self.W_ih = random_weights((num_hidden, num_hidden), name=self.name+"W_ih")
        self.W_fh = random_weights((num_hidden, num_hidden), name=self.name+"W_fh")
        self.W_oh = random_weights((num_hidden, num_hidden), name=self.name+"W_oh")

        self.b_g = zeros(num_hidden, name=self.name+"b_g")
        self.b_i = zeros(num_hidden, name=self.name+"b_i")
        self.b_f = zeros(num_hidden, name=self.name+"b_f")
        self.b_o = zeros(num_hidden, name=self.name+"b_o")

        self.params = [self.W_gx, self.W_ix, self.W_ox, self.W_fx,
                       self.W_gh, self.W_ih, self.W_oh, self.W_fh,
                       self.b_g, self.b_i, self.b_f, self.b_o,
                       ]

        self.output()

    def get_params(self):
        return self.params

    def one_step(self, x, h_tm1, s_tm1):
        """
        Run the forward pass for a single timestep of a LSTM
        h_tm1: initial h
        s_tm1: initial s  (cell state)
        """

        g = T.tanh(T.dot(x, self.W_gx) + T.dot(h_tm1, self.W_gh) + self.b_g)
        i = T.nnet.sigmoid(T.dot(x, self.W_ix) + T.dot(h_tm1, self.W_ih) + self.b_i)
        f = T.nnet.sigmoid(T.dot(x, self.W_fx) + T.dot(h_tm1, self.W_fh) + self.b_f)
        o = T.nnet.sigmoid(T.dot(x, self.W_ox) + T.dot(h_tm1, self.W_oh) + self.b_o)

        s = i * g + s_tm1 * f
        h = T.tanh(s) * o

        return h, s


    def output(self, train=True):

        outputs_info = [self.h0, self.s0]

        ([outputs, states], updates) = theano.scan(
            fn=self.one_step,   #function
            sequences=self.X,
            # n_steps=600,
            outputs_info = outputs_info,
            go_backwards=self.go_backwards
        )

        return outputs


    def reset_state(self):
        self.h0 = theano.shared(floatX(np.zeros(self.num_hidden)))
        self.s0 = theano.shared(floatX(np.zeros(self.num_hidden)))



class GRULayer(NNLayer):
    def __init__(self, num_input, num_cells, input_layers=None, name="", go_backwards=False):
        """
        GRU Layer
        Takes as input sequence of inputs, returns sequence of outputs
        """

        self.name = name
        self.num_input = num_input
        self.num_cells = num_cells

        if len(input_layers) >= 2:
            self.X = T.concatenate([input_layer.output() for input_layer in input_layers], axis=1)
        else:
            self.X = input_layers[0].output()

        self.s0 = zeros(num_cells)
        self.go_backwards = go_backwards

        self.U_z = random_weights((num_input, num_cells), name=self.name + "U_z")
        self.W_z = random_weights((num_cells, num_cells), name=self.name + "W_z")
        self.U_r = random_weights((num_input, num_cells), name=self.name + "U_r")
        self.W_r = random_weights((num_cells, num_cells), name=self.name + "W_r")
        self.U_h = random_weights((num_input, num_cells), name=self.name + "U_h")
        self.W_h = random_weights((num_cells, num_cells), name=self.name + "W_h")
        self.b_z = zeros(num_cells, name=self.name + "b_z")
        self.b_r = zeros(num_cells, name=self.name + "b_r")
        self.b_h = zeros(num_cells, name=self.name + "b_h")

        self.params = [self.U_z, self.W_z, self.U_r,
                       self.W_r, self.U_h, self.W_h,
                       self.b_z, self.b_r, self.b_h
                       ]

        self.output()

    def get_params(self):
        return self.params


    def one_step(self, x, s_tm1):
        """
        """
        z = T.nnet.sigmoid(T.dot(x, self.U_z) + T.dot(s_tm1, self.W_z) + self.b_z)
        r = T.nnet.sigmoid(T.dot(x, self.U_r) + T.dot(s_tm1, self.W_r) + self.b_r)
        h = T.tanh(T.dot(x, self.U_h) + T.dot(s_tm1 * r, self.W_h) + self.b_h)
        s = (1 - z) * s_tm1 + z * h

        return [s]

    def output(self, train=True):

        outputs_info = [self.s0]

        (outputs, updates) = theano.scan(
            fn=self.one_step,
            sequences=self.X,
            outputs_info=outputs_info,
            go_backwards=self.go_backwards
        )

        return outputs

    def reset_state(self):
        self.s0 = zeros(self.num_cells)


class MGULayer(NNLayer):

    def __init__(self, num_input, num_hidden, input_layers=None, name="", go_backwards=False):
        """
        MGU Layer from 周志华paper
        Takes as input sequence of inputs, returns sequence of outputs
        """
        self.name = name
        self.num_input = num_input
        self.num_hidden = num_hidden

        if len(input_layers) >= 2:
            # axis=1  an row xiang jia
            self.X = T.concatenate([input_layer.output() for input_layer in input_layers], axis=1)
        else:
            self.X = input_layers[0].output()

        self.h0 = theano.shared(floatX(np.zeros(num_hidden)))
        self.s0 = theano.shared(floatX(np.zeros(num_hidden)))

        self.go_backwards = go_backwards


        self.W_fx = random_weights((num_input, num_hidden), name=self.name + "W_fx")
        self.W_fh = random_weights((num_hidden, num_hidden), name=self.name + "W_fh")
        self.U_h = random_weights((num_input, num_hidden), name=self.name + "U_h")
        self.W_h = random_weights((num_hidden, num_hidden), name=self.name + "W_h")

        self.b_f = zeros(num_hidden, name=self.name + "b_f")
        self.b_h = zeros(num_hidden, name=self.name + "b_h")

        self.params = [self.W_fx, self.W_fh, self.b_f]
        self.output()


    def get_params(self):
        return self.params


    def one_step(self, x, s_tm1):
        """
        Run the forward pass for a single timestep of a LSTM
        h_tm1: initial h
        s_tm1: initial s  (cell state)
        """


        f = T.nnet.sigmoid(T.dot(x, self.W_fx) + T.dot(s_tm1, self.W_fh) + self.b_f)
        h = T.tanh(T.dot(x, self.U_h) + T.dot(s_tm1 * f, self.W_h) + self.b_h)
        s = (1 - f) * s_tm1 + f * h

        return [s]


    def output(self, train=True):

        outputs_info = [self.s0]

        (outputs, updates) = theano.scan(
            fn=self.one_step,
            sequences=self.X,
            outputs_info=outputs_info,
            go_backwards=self.go_backwards
        )

        return outputs

    def reset_state(self):
        self.s0 = zeros(self.num_hidden)




class FullyConnectedLayer(NNLayer):
    """
    """
    def __init__(self, num_input, num_output, input_layers, name=""):

        if len(input_layers) >= 2:
            self.X = T.concatenate([input_layer.output() for input_layer in input_layers], axis=1)
        else:
            self.X = input_layers[0].output()
        self.W_yh = random_weights((num_input, num_output),name="W_yh_FC")
        self.b_y = zeros(num_output, name="b_y_FC")
        self.params = [self.W_yh, self.b_y]

    def output(self):
        # return T.nnet.sigmoid(T.dot(self.X, self.W_yh) + self.b_y)
        return T.dot(self.X, self.W_yh) + self.b_y

    def get_params(self):
        return self.params


