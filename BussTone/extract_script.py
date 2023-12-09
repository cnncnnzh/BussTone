# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 17:23:48 2023

@author: zhuhe
"""


import os
import re
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import torch
from gibberish_detector import detector


def html_to_txt(dirc, to_dirc):
    with open (dirc, 'r', encoding='utf-8') as f:
        data = f.readlines()
    data = ''.join(data)
    gfg = BeautifulSoup(data)
    res = gfg.get_text('\n')
    with open(to_dirc, 'w', encoding='utf-8') as f:
        f.write(res)

def check_repeat(i, all_paragraphs):
    for left, right in all_paragraphs:
        if left < i < right:
            return True
    return False

def check_abbv(i, piece):
    abbv = ('E.U.', 'U.S.', 'U.K.', 'i.e.')
    return piece[i-3:i+1] in abbv\
        or piece[i-1:i+3] in abbv

def get_paragraph(dirc, split_sentence):
    with open(dirc, 'r', encoding='utf-8') as f:
        data = f.readlines()
        data = ''.join(data)
    indices = [m.start() for m in re.finditer('CCPA', data)]
    boundary = 4000
    all_script = []
    all_paragraphs = []
    gibberish_detector = detector.create_from_model(r'D:\Dropbox\Shan\BussTone\big.model')
    for i in indices: 

        start = i-boundary
        piece = data[start : start+2*boundary+1]

        if check_repeat(i, all_paragraphs):
            continue

        all_newline = [m.start() for m in re.finditer('\n', piece)]
        # sorted_newline = np.array(sorted(all_newline, key=lambda x: abs(boundary - x)))
        # left_para = sorted_newline[sorted_newline<boundary][0]
        # right_para = sorted_newline[sorted_newline>boundary][0]
        # all_paragraphs.append([start+left_para, start+right_para])
        
        all_period = [m.start() for m in re.finditer(r'\.', piece) if not check_abbv(m.start(), piece)]
        all_exclamation = [m.start() for m in re.finditer(r'\!', piece)]
        all_endings = all_period + all_exclamation + all_newline
        
        sorted_endings = np.array(sorted(all_endings, key=lambda x: abs(boundary - x)))
        
        left = sorted_endings[sorted_endings<boundary]
        right = sorted_endings[sorted_endings>boundary]
        right = np.array([left[0]] + list(right))
        left_end, right_end = 0, 2 * boundary 
        left_org = []
        for i in range(len(left)):
            if i == 0:
                if piece[left[i]]=='\n' or piece[left[i]+1] != ' ':
                    left_end = max(left[i], left_end)
                    break
                continue
            sentence = piece[left[i]+1 : left[i-1]+1]
            if gibberish_detector.is_gibberish(sentence):
                continue
            left_org.append(sentence)
            if piece[left[i]]=='\n' or piece[left[i]+1] != ' ':
                left_end = max(left[i], left_end)
                break
        all_script += left_org[::-1]
        for i in range(1, len(right)):
            sentence = piece[right[i-1]+1 : right[i]+1]
            if gibberish_detector.is_gibberish(sentence):
                continue
            all_script.append(sentence)
            if piece[right[i]]=='\n' or piece[right[i]+1] != ' ':
                right_end = min(right[i], right_end)
                break 
        all_paragraphs.append([start+left_end, start+right_end])
        all_script.append('-----------')
        # s1, s2, s3, s4, s5, s6 = left[2], left[1], left[0], right[0], right[1], right[2]
        # if split_sentence.lower() == 'true':
        #     # print(start)
        #     # print(end)
        #     if s2 - s1 < 512 and piece[s3] != '\n' and piece[s2] != '\n':
        #         all_script.append(data[i-boundary+s1+1 : i-boundary+s2+1])
        #     if s3 - s2 < 512 and piece[s2] != '\n':
        #         all_script.append(data[i-boundary+s2+1 : i-boundary+s3+1])
        #     if s4 - s3 < 512:
        #         all_script.append(data[i-boundary+s3+1 : i-boundary+s4+1])
        #     if s5 - s4 < 512 and piece[s4] != '\n':
        #         all_script.append(data[i-boundary+s4+1 : i-boundary+s5+1])
        #     if s6 - s5 < 512 and piece[s4] != '\n' and piece[s5] != '\n':
        #         all_script.append(data[i-boundary+s5+1 : i-boundary+s6+1])
        # else:
        #     if s5 - s2 < 512 and piece[s3] != '\n' and piece[s4] != '\n':
        #         all_script.append(data[i-boundary+s2+1 : i-boundary+s5+1])
        #     elif s5 - s3 < 512 and piece[s4] != '\n':
        #         all_script.append(data[i-boundary+s3+1 : i-boundary+s5+1])
        #     elif s4 - s3 < 512:
        #         all_script.append(data[i-boundary+s3+1 : i-boundary+s4+1])
                
    return all_script

def gen_script(script, to_file):
    with open (to_file, 'a', encoding='utf-8') as f:
        f.write(script)
        f.write('\n\n')
    

        
        