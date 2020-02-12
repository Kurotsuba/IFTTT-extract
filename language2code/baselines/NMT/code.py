#!/usr/bin/python3.6
import random

import torch
import torch.nn as nn
from torch.autograd import Variable
from torch import optim
import torch.nn.functional as F
import torch.utils.data as DataSet
import numpy as np
import matplotlib.pyplot as plt

import pickle

# global vars
SOS_TOKEN=0
EOS_TOKEN=1
MAX_LEN=0
USE_CUDA=1
INPUT_LANG=0
OUTPUT_LANG=0

def read_data(data_pickle):
    data_dict = {}
    with open(data_pickle, 'rb') as f:
        data_dict = pickle.load(f)
    # read data as {description:[description, TC, T, AC, A] ... }
    
    des_data = list(data_dict.keys())
    recipe_data = [each[1:] for each in data_dict.values()]
    recipe_data = [' '.join(each) for each in recipe_data]

    return (des_data, recipe_data)

# a language class, description and recipe act as two different language
class Lang:
    def __init__(self, name):
        self.name = name
        self.word2index = {}
        self.word2count = {}
        self.index2word = {0: "SOS", 1: "EOS"}
        self.n_words = 2

    def add_sentence(self, sentence):
        for word in sentence.split(' '):
            self.add_word(word)

    def add_word(self, word):
        if word not in self.word2index:
            self.word2index[word] = self.n_words
            self.word2count[word] = 1
            self.index2word[self.n_words] = word
            self.n_words += 1
        else:
            self.word2count[word] += 1

# utils
def word_index_from_sentence(lang, sentence):
    return [lang.word2index[word] for word in sentence.split(' ')]

def index_from_sentence(lang, sentence):
    indexes = word_index_from_sentence(lang, sentence)
    indexes.append(EOS_TOKEN)
    for i in range(MAX_LEN - len(indexes)):
        indexes.append(EOS_TOKEN)
    return indexes

def index_from_pair(pair):
    input_var = index_from_sentence(INPUT_LANG, pair[0])
    output_var = index_from_sentence(OUTPUT_LANG, pair[1])
    return (input_var, output_var)

def index_to_sentence(lang, index_list):
    result = [lang.index2word[i] for i in index_list if i != EOS_TOKEN]
    result = ' '.join(result)
    return result

def rightness(predictions, labels):
    pred = torch.max(predictions.data, 1)[1] 
    rights = pred.eq(labels.data).sum() 
    return rights, len(labels)

class EncoderRNN(nn.Module):
    def __init__(self, input_size, hidden_size, n_layers=1):
        super(EncoderRNN, self).__init__()
        self.n_layers = n_layers
        self.hidden_size = hidden_size
        self.embedding = nn.Embedding(input_size, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size, batch_first=True, num_layers=self.n_layers, bidirectional=True)

    def forward(self, input, hidden):
        embedded = self.embedding(input)
        output = embedded
        output, hidden = self.gru(output, hidden)
        return output, hidden

    def init_hidden(self, batch_size):
        result = Variable(torch.zeros(self.n_layers*2, batch_size, self.hidden_size))
        if USE_CUDA:
            return result.cuda()
        else:
            return result

class DecoderRNN(nn.Module):
    def __init__(self, hidden_size, output_size, n_layers=1):
        super(DecoderRNN, self).__init__()
        self.n_layers = n_layers
        self.hidden_size = hidden_size
        self.embedding = nn.Embedding(output_size, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size, batch_first=True, num_layers=self.n_layers, bidirectional=True)
        self.dropout = nn.Dropout(0.1)
        self.out = nn.Linear(hidden_size*2, output_size)
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, input, hidden):
        output = self.embedding(input)
        output = F.relu(output)
        output, hidden = self.gru(output, hidden)
        output = self.dropout(output)
        output = self.softmax(self.out(output[:, -1, :]))

        return output, hidden

    def init_hidden(self):
        result = Variable(torch.zeros(self.n_layers*2, batch_size, self.hidden_size))
        if USE_CUDA:
            return result.cuda()
        else:
            return result

def train_model():
    global plot_losses
    global print_loss_total
    global print_loss_avg
    print_loss_total = 0

    for data in train_loader:
        input_variable = Variable(data[0]).cuda() if USE_CUDA else Variable(data[0])
        target_variable = Variable(data[1]).cuda() if USE_CUDA else Variable(data[1])

        encoder_hidden = encoder.init_hidden(data[0].size()[0])
        encoder_optimizer.zero_grad()
        decoder_optimizer.zero_grad()

        loss = 0

        encoder_outputs, encoder_hidden = encoder(input_variable, encoder_hidden)
        
        decoder_input = Variable(torch.LongTensor([[SOS_TOKEN]] * target_variable.size()[0]))
        decoder_input = decoder_input.cuda() if USE_CUDA else decoder_input

        decoder_hidden = encoder_hidden

        use_teacher_forcing = True if random.random() < teacher_forcing_ratio else False
        base = torch.zeros(target_variable.size()[0])
        if use_teacher_forcing:
            for di in range(MAX_LEN):
                decoder_output, decoder_hidden = decoder(decoder_input, decoder_hidden)
                loss += criterion(decoder_output, target_variable[:, di])
                decoder_input = target_variable[:, di].unsqueeze(1)

        else:
            for di in range(MAX_LEN):
                decoder_output, decoder_hidden = decoder(decoder_input, decoder_hidden)

                topv, topi = decoder_output.data.topk(1, dim = 1)
                ni = topi[:, 0]

                decoder_input = Variable(ni.unsqueeze(1))
                decoder_input = decoder_input.cuda() if USE_CUDA else decoder_input

                loss += criterion(decoder_output, target_variable[:, di])


        loss.backward()
        loss = loss.cpu() if USE_CUDA else loss
        encoder_optimizer.step()
        decoder_optimizer.step()
        print_loss_total += loss.data.numpy()

    print_loss_avg = print_loss_total / len(train_loader)

def evaluation_model():
    global dev_loss
    global rights
    dev_loss = 0
    rights = []

    for data in dev_loader:
        input_variable = Variable(data[0]).cuda() if USE_CUDA else Variable(data[0])
        target_variable = Variable(data[1]).cuda() if USE_CUDA else Variable(data[1])

        encoder_hidden = encoder.init_hidden(data[0].size()[0])

        loss = 0
        encoder_outputs, encoder_hidden = encoder(input_variable, encoder_hidden)

        decoder_input = Variable(torch.LongTensor([[SOS_TOKEN]] * target_variable.size()[0]))
        decoder_input = decoder_input.cuda() if USE_CUDA else decoder_input

        decoder_hidden = encoder_hidden

        for di in range(MAX_LEN):
            decoder_output, decoder_hidden = decoder(decoder_input, decoder_hidden)

            topv, topi = decoder_output.data.topk(1, dim = 1)
            ni = topi[:, 0]
            decoder_input = Variable(ni.unsqueeze(1))
            decoder_input = decoder_input.cuda() if USE_CUDA else decoder_input

            right = rightness(decoder_output, target_variable[:, di])
            rights.append(right)

            loss += criterion(decoder_output, target_variable[:, di])
        loss = loss.cpu() if USE_CUDA else loss
        dev_loss += loss.data.numpy()
 
MAX_LEN = 30
INPUT_LANG = Lang('description')
OUTPUT_LANG = Lang('recipe')

# prepare data
data = read_data('data.pickle')
pairs = [(a, b) for a, b in zip(data[0], data[1])]
pairs = [each for each in pairs if len(each[0]) < MAX_LEN]
for pair in pairs:
    INPUT_LANG.add_sentence(pair[0])
    OUTPUT_LANG.add_sentence(pair[1])

random_idx = np.random.permutation(range(len(pairs)))
pairs = [pairs[i] for i in random_idx]
pairs = [index_from_pair(pair) for pair in pairs]

print(len(pairs))
dev_size = len(pairs) // 10
pp = pairs
pairs = pairs[: -dev_size]
dev_pairs = pp[-dev_size : -dev_size // 2]
test_pairs = pp[-dev_size // 2 :]

batch_size = 8
print('train: ', len(pairs))
print('dev: ', len(dev_pairs))
print('test: ', len(test_pairs))

pairs_X = [pair[0] for pair in pairs]
pairs_Y = [pair[1] for pair in pairs]
dev_X = [pair[0] for pair in dev_pairs]
dev_Y = [pair[1] for pair in dev_pairs]
test_X = [pair[0] for pair in test_pairs]
test_Y = [pair[1] for pair in test_pairs]

train_dataset = DataSet.TensorDataset(torch.LongTensor(pairs_X), torch.LongTensor(pairs_Y))
train_loader = DataSet.DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=8)
dev_dataset = DataSet.TensorDataset(torch.LongTensor(dev_X), torch.LongTensor(dev_Y))
dev_loader = DataSet.DataLoader(dev_dataset, batch_size=batch_size, shuffle=True, num_workers=8)
test_dataset = DataSet.TensorDataset(torch.LongTensor(test_X), torch.LongTensor(test_Y))
test_loader = DataSet.DataLoader(test_dataset, batch_size=batch_size, shuffle=True, num_workers=8)

# implement encoder and decoder
hidden_size = 32
max_length = MAX_LEN
n_layers = 1

encoder = EncoderRNN(INPUT_LANG.n_words, hidden_size, n_layers=n_layers)
decoder = DecoderRNN(hidden_size, OUTPUT_LANG.n_words, n_layers=n_layers)

if USE_CUDA:
    encoder = encoder.cuda()
    decoder = decoder.cuda()

learning_rate = 0.0001

encoder_optimizer = optim.Adam(encoder.parameters(), lr=learning_rate)
decoder_optimizer = optim.Adam(decoder.parameters(), lr=learning_rate)

criterion = nn.NLLLoss()
teacher_forcing_ratio = 0.2

plot_losses = []
print_loss_total = 0
print_loss_avg = 0
dev_loss = 0
rights = []
plot_losses = []

num_epoch = 200
for epoch in range(num_epoch):
    train_model()

    evaluation_model()

    right_ratio = 1.0 * np.sum([i[0] for i in rights]) / np.sum([i[1] for i in rights])
    print('progress：%d%% train_loss：%.4f，dev_loss：%.4f，acc：%.2f%%' % (epoch * 1.0 / num_epoch * 100, 
                                                    print_loss_avg,
                                                    dev_loss / len(dev_loader),
                                                    100.0 * right_ratio))
    plot_losses.append([print_loss_avg, dev_loss / len(dev_loader), right_ratio])

# draw plot if possible
#a = [i[0] for i in plot_losses]
#b = [i[1] for i in plot_losses]
#c = [i[2] * 100 for i in plot_losses]
#plt.plot(a, '-', label = 'Training Loss')
#plt.plot(b, ':', label = 'Validation Loss')
#plt.plot(c, '.', label = 'Accuracy')
#plt.xlabel('Epoch')
#plt.ylabel('Loss & Accuracy')
#plt.legend()
