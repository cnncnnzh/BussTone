# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 17:23:48 2023

@author: zhuhe
"""


import os
import re
from bs4 import BeautifulSoup
# from transformers import AutoTokenizer, AutoModelForSequenceClassification
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

def check_repeat(i, all_paragraph_ranges):
    for left, right in all_paragraph_ranges:
        if left < i < right:
            return True
    return False

def check_abbv(i, piece):
    abbv = ('E.U.', 'U.S.', 'U.K.', 'i.e.', 'e.g', 'E.g.')
    return piece[i-3:i+1] in abbv\
        or piece[i-1:i+3] in abbv\
        or piece[i-3:i+1] == 'Inc.'

def check_true_div(i, piece):
    if i in (0, 1, len(piece)-1):
        return True
    return (0 <= ord(piece[i+1]) - ord('A') <= 25 or piece[i+1] == '\xa0')\
        and (piece[i-1] in ('.', '!', '\n', '\xa0') or piece[i-2] in ('.', '!','\n', '\xa0') or piece[i-3] in ('.', '!','\n', '\xa0'))
    
    
def get_paragraph(dirc, split_sentence):
    with open(dirc, 'r', encoding='utf-8') as f:
        data = f.readlines()
        data = ''.join(data)
    indices = [m.start() for m in re.finditer('CCPA', data)]
    boundary = 4000
    all_script = []
    all_paragraphs = []
    all_paragraph_ranges = []
    need_check = False
    gibberish_detector = detector.create_from_model(r'D:\Dropbox\Shan\BussTone\big.model')
    for i in indices: 

        start = i-boundary
        piece = data[start : start+2*boundary+1]

        if check_repeat(i, all_paragraph_ranges):
            continue

        all_newline = [m.start() for m in re.finditer('\n', piece)]
        
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
            if i == 0 and piece[left[i]]=='\n':
                left_end = max(left[i], left_end)
                break
            else:
                sentence = piece[left[i]+1 : left[i-1]+1]
                if gibberish_detector.is_gibberish(sentence):
                    continue
                left_org.append(sentence)
                if piece[left[i]]=='\n':
                    left_end = max(left[i], left_end)
                    break
        all_script += left_org[::-1]
        for i in range(1, len(right)):
            sentence = piece[right[i-1]+1 : right[i]+1]
            if gibberish_detector.is_gibberish(sentence):
                continue
            all_script.append(sentence)
            if piece[right[i]]=='\n':
                right_end = min(right[i], right_end)
                break 
        all_script.append('-----------')
        
        all_paragraph_ranges.append([start+left_end, start+right_end])
        paragraph = piece[left_end:right_end+1].strip()
        all_paragraphs.append(paragraph)
        need_check = (0 <= ord(paragraph[0]) - ord('a') <= 25 or not paragraph[-1] in ('.', '!'))
        
    if split_sentence.lower() == 'true':
        return all_script, need_check
    else: 
        return paragraph, need_check

def gen_script(script, to_file):
    with open (to_file, 'a', encoding='utf-8') as f:
        f.write(script)
        f.write('\n\n')
    

        
        