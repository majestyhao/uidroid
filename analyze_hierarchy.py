#!/usr/bin/env python2
# coding: utf-8

__author__ = 'hao'
# use LDA to do topic modelings on xml
# LDA: relies on stat models to discover the topics that occur in a collection of unlabeled text
# a topic consists of a cluster of words that freq occur together
import numpy as np
import lda
import lda.datasets
import xml.dom.minidom
import os
import re

def is_degree(str):
    if re.search('.*?°.*?', str):
        str = '°'
        is_new_vocab(str)
        return True
    else:
        return False

def is_new_vocab(str):
    if str not in vocab:
        vocab.append(str)
        colnum = len(vocab) - 1
        title_vocab_mat_index.append([self_row, colnum])
    else:
        colnum = vocab.index(str) - 1
        title_vocab_mat_index.append([self_row, colnum])

def DFS_xml(node, nodelist):
    if node not in nodelist:
        nodelist.append(node)
        txt = node.getAttribute('text')
        desc = node.getAttribute('content-desc')
        resid = node.getAttribute('resource-id')
        if txt:
            print txt
            if is_degree(txt):
                pass
            else:
                if len(txt) > 40:
                    pass
                else:
                    is_new_vocab(txt)
        elif desc:
            is_new_vocab(desc)
        elif resid:
            is_new_vocab(resid.split('/')[1])
        for i in node.childNodes:
            DFS_xml(i, nodelist)

def visit(arg, dirname, files):
    global self_row
    for filename in files:
        if re.search('.*?hierarchy\.xml', filename):
            print filename + '>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
            dom = xml.dom.minidom.parse(dirname + '/' + filename)
            root = dom.documentElement
            nodelist = []
            DFS_xml(root, nodelist)
            self_row += 1
            titles.append(filename)

def construct_mat_from_index(list):
    global title_vocab_mat
    title_vocab_mat = [[0 for x in range(len(vocab))] for x in range(self_row + 1)]
    for i in list:
        title_vocab_mat[i[0]][i[1]] = 1

title_vocab_mat_index = []
vocab = []
titles = []
self_row = 0
os.path.walk('./', visit, None)
construct_mat_from_index(title_vocab_mat_index)
print len(titles), len(vocab)
print vocab
print title_vocab_mat

# extract text, content-desp and resID (only sub component) from xml

#
#X = lda.datasets.load_reuters()
#print X
#vocab = lda.datasets.load_reuters_vocab()
#print vocab
# print len(vocab)
#titles = lda.datasets.load_reuters_titles()
#print titles
# print len(titles)
# print X.shape
#
model = lda.LDA(n_topics=10, n_iter=500, random_state=1)
title_vocab_mat = np.array(title_vocab_mat)
model.fit(title_vocab_mat)
topic_word = model.topic_word_
n_top_words = 10 # -1
for i, topic_dist in enumerate(topic_word):
     topic_words = np.array(vocab)[np.argsort(topic_dist)][:-n_top_words:-1]
     print 'Topic {}: {}'.format(i, ' ; '.join(topic_words).encode('utf-8'))
