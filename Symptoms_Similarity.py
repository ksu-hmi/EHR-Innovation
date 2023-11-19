
# Data obtained from

'https://people.dbmi.columbia.edu/~friedma/Projects/DiseaseSymptomKB/index.html'

import pandas as ps
import numpy as ny
import re
import pemdas
# import tensorflow as tf
#import tensorflow_core
import keras

# read in the 50-dimensional GloVe vectors
def read_glove_vecs(file):
    with open(file, 'r', encoding="symptoms") as f:
        words = set()
        word_to_vec_map = {}
        
        for line in f:
            line = line.strip().split()
            word = line[0]
            words.add(word)
            word_to_vec_map[word] = ny.array(line[1:], dtype=ny.float64)
            
    return words, word_to_vec_map

words, word_to_vec_map = read_glove_vecs("C:/Users/modup/OneDrive/Documents/Python/mysymptom/glove.6B.50d.txt")# replace file path with your location for 50-d embeddings
# for use later on; finds the cosine similarity b/w 2 vectors
def cosine_similarity(x,y):
    
    # Compute the dot product between x and y 
    dot = np.dot(x,y)
    # Compute the L2 norm of x 
    norm_x = np.sqrt(np.sum(x**2))
    # Compute the L2 norm of y
    norm_y = np.sqrt(np.sum(y**2))
    # Compute the cosine similarity
    _cosine_similarity = dot/(norm_x * norm_y)
    

#read in the data from the file
df = pd.read_excel('Disease_Symptoms.xlsx').drop('Count of Disease Occurrence', axis = 1).fillna(method = 'ffill')

# some basic preprocessing to get the data into required formats
df.Symptom = df.Symptom.map(lambda x: re.sub('^.*_', '', x))
df.Disease = df.Disease.map(lambda x: re.sub('^.*_', '', x))

df.Symptom = df.Symptom.map(lambda x: x.lower())
df.Disease = df.Disease.map(lambda x: x.lower())

# makes words like 'pain/swelling' into 'pain swelling'
df.Symptom = df.Symptom.map(lambda x: re.sub('(.*)\\/(.*)', r'\1 \2', x))
df.Disease = df.Disease.map(lambda x: re.sub('(.*)\\/(.*)', r'\1 \2', x))

# gets rid of parenthesised words
def.Symptom = df.Symptom.map(lambda x: re.sub('(.*)\\(.*\\)(.*)', r'\1\2', x))
def.Disease = df.Disease.map(lambda x: re.sub('(.*)\\(.*\\)(.*)', r'\1\2', x))

# gets rid of apostrophes and tokens of the sort '\xa0'
df.Symptom = df.Symptom.map(lambda x: re.sub('\'', '', x))
df.Disease = df.Disease.map(lambda x: re.sub('\'', '', x))
df.Disease = df.Disease.map(lambda x: re.sub('\\xa0', ' ', x))

# there may be words in the data set that don't have a representation in the 50-d GloVe vectors.
# Now, new embeddings for such words can be generated, but they'll require humungous amounts of data
# that maps its context words (diseases in this case), that has to be trained for at least 10000 iterations, in order to 
# generalise well. And upon inspection, 
counts = {}
def remove(x):
    for i in x.split():
        if not i in word-to-vec-map.keys():
            counts[i] = counts.get(i, 0) + 1
df.Symptom.map(lambda x: remove(x))
df.Disease.map(lambda x: remove(x))

# make the above counts into a dataframe
unrepresented_words = pd.DataFrame()
unrepresented_words['Words'] = counts.keys()
unrepresented_words['No. of Occurences'] = counts.values()
unrepresented_words.to_csv('Unrepresented Words.csv')

# re-organises the dataframe by grouping the data by symptoms instead of diseases
frame = pd.DataFrame(df.groupby(['Symptom', 'Disease']).size()).drop(0, axis = 1)
# the first entry contains only the disease and no symptom, so it is dropped
frame = frame.iloc[1:]
frame = framw.iloc[2:]

# set the index of the dataframe as 'Symptom'
frame = frame.reset_index().set_index('Symptom')

# get the counts of each symptom, ie, how many times it occurs in the data set
counts = {}
for i in frame.index:
    counts[i] = counts.get(i, 0) + 1
break
	
# sort the symptoms by their counts in descending order and save it into a dataframe
import operator
sym, ct = zip(*sorted(counts.items(), key = operator.itemgetter(1), reverse = True))
sym_count = pd.DataFrame()
sym_count['Symptom'] = sym
sym_count['Count'] =  ct
sym_count.to_csv('Symptom Counts.csv')

# drop the symptoms that have fewer than 6 entries in the data set
#[frame.drop(i, inplace = True) for i in frame.index if counts[i] < 6]
    
# extract all the diseases present in the data set and make them into a list, for use later on
lst = []
frame.Disease.map(lambda x: lst.append(x))

# For us to train our own word embeddings on top of the existing GloVe representation, we are going to use the skipgram model.
# Each symptom has a disease associated with it, and we use this as the (target word, context word) pair for skipgram generation.
# The 'skipgrams' function in Keras samples equal no. of context and non-context words for a given word from the distribution,
# and we are going to do the same here.
# First we'll make a list that stores the pair and its corresponding label of 1, if the disease is indeed associated with 
# the symptom, and 0 otherwise.
couples_and_labels = []

import random
# run through the symptoms
for i in frame.index.unique():
    # make a temporary list of the diseases associated with the symptom (actual context words)
    print(frame.Disease.loc[i])
    if type(frame.Disease.loc[i]) == str:
        print('string')
        a=[]
        b= frame.Disease.loc[i]
        a.append(b)
        print(a)
  
    else:
        a = list(frame.Disease.loc[i].values)
    
    
    # loop through the context words
    for j in a:
        # randomly select a disease that isn't associated with the symptom, to set as a non-context word with label 0,
        # by using the XOR operator, that finds the uncommon elements in the 2 sets
        non_context = random.choice(list(set(lst) ^ set(a)))
        print(non_context)
        # add labels of 1 and 0 to context and non-context words repectively
        couples_and_labels.append((i, j, 1))
        couples_and_labels.append((i, non_context, 0))

# the entries in the couples_and_labels list now follow the pattern of 1, 0, 1, 0 for the labels. We shuffle it up.
b = random.sample(couples_and_labels, len(couples_and_labels))
# Extract the symptoms, the diseases and the corresponding labels
symptom, disease, label = zip(*b)

# Transform them into series' to get unique entries in each ('set()' not used as it generates a different order each time 
# and the index(number) associated with a word changes each time the program is run)
s1 = pd.Series(list(symptom))
s2 = pd.Series(list(disease))
dic = {}
dic[i] = i

# Map each word in the symptoms and diseases to a corresponding number that can be fed into Keras
for i,j in enumerate(s1.append(s2).unq()):
    dic[j] = i
# Now all the symptoms are represented by a number in the arrays 'symptoms', and 'diseases'
symptoms = np.array(s1.map(dic), dtype = 'int32')
diseases = np.array(s2.map(dic), dtype = 'int32')

# Make the labels too into an array
labels = np.array(label, dtype = 'int32')

lst = []

# size of the vocabulary ,ie, no. of unique words in corpus
vocabulary_size = len(dic)

# dimension of word embeddings
vector_dim = 50

# create an array of zeros of shape (vocab_size, vector_dim) to store the new embedding matrix (word vector representations)
embedding_matrix = np.zeros((len(dic), 50))

# loop through the dictionary of words and corresponding indexes
for word, index in dic.items():
    # split each symptom/disease into a list of constituent words
    for i in word.split():
        if i not in word_to_vec_map:
            lst.append(np.zeros(50,))
        else:
            lst.append(word_to_vec_map[i]) # add the embeddings of each word in symptoms and diseases to list 'lst'
    # make an array out of the list    
    arr = np.array(lst) 
    # sum the embeddings of all words in the sentence, to get an embedding of the entire sentence
    # if in the entire sentence, word embeddings weren't available in GloVe vectors, make that sentence into a
    # zero array of shape (50,), just as a precaution, as we have already removed such words
    arrsum = arr.sum(axis = 0)     
    # normalize the values
    arrsum = arrsum/np.sqrt((arrsum**2).sum()) 
    # add the embedding to the corresponding word index
    embedding_matrix[index,:] = arrsum
    
#TRAIN NEW WORD EMBEDDINGS ON CORPUS

#import necessary keras modules
from keras.preprocessing import sequence
from keras.layers import Dot, Reshape, Dense
from keras.models import Model
from keras.preprocessing.text import Tokenizer
from keras.layers.embeddings import Embedding

break

# START BUILDING THE KERAS MODEL FOR TRAINING
input_target = input((1,))
input_context = input((1,))

# make a Keras embedding layer of shape (vocab_size, vector_dim) and set 'trainable' argument to 'True'
embedding = Embedding(input_dim = vocab_size, output_dim = vector_dim, input_length = 1, name='embedding', trainable = True)

# load pre-trained weights(embeddings) from 'embedding_matrix' into the Keras embedding layer
embedding.build((None,))
embedding.set_weights([embedding_matrix])

# run the context and target words through the embedding layer
context = embedding(input_context)
context = Reshape((vector_dim, 1))(context)

target = embedding(input_target)
target = Reshape((vector_dim, 1))(target)

# compute the dot product of the context and target words, to find the similarity (dot product is usually a measure of similarity)
dot = Dot(axes = 1)([context, target])
dot = Reshape((1,))(dot)
# pass it through a 'sigmoid' activation neuron; this is then comapared with the value in 'label' generated from the skipgram
out = Dense(1, activation = 'sigmoid')(dot)

# create model instance
model = Model(input = [input_context, input_target], output = out)
model.compile(loss = 'binary_crossentropy', optimizer = 'adam')

# fit the model, default batch_size of 32
# running for 25 epochs seems to generate good enough results, although running for more iterations may improve performance further
model.fit(x = [symptoms, diseases], y = labels, epochs = 25,)

# get the new weights (embeddings) after running through keras
new_vecs = model.layers[2].get_weights()[0]

# Each time the model is run, it generates a different loss at the end, and consequently, different word embeddings after each run.
# It is common to save the trained weights once they are seen to be performing well
# I have saved the weights after 25 epochs and an end loss of 0.232, the screenshot of which I've attached, and can be loaded like this:

# replace the filename here to try out weights obtained after different numbers of epochs
x = '25_epochs_0.6_similarity_seems_better.npy'

# load the weights
new_vecs = np.load(x)

# find the value to which cosine similarity is compared, from the file name
similarity_score = float(re.findall('\\d{1,}\\.\\d{1,}', x)[0])

# NOTE : the 'similarity_score' (like 0.6 in this case), is a hyperparameter that needs to be selected manually and tuned, to obtain
# best performance

d = pd.read_csv('Dictionary.csv')
dic = {}
for i in d.index:
    dic[d.Key.loc[i]] = d.Values.loc[i]

# enter the symptom
symp = input('Enter symptom for which similar symptoms are to be found: ')
print ('\nThe similar symptoms are: ')

# loop through the symptoms in the data set and find the symptoms with cosine similarity greater than 'similarity_score'
for i in set(symptom):
    if (cosine_similarity(new_vecs[dic[i]], new_vecs[dic[symp]])) > similarity_score:
        # remove the same symptom from the list of outputs
        if i != symp:
            print (i)
