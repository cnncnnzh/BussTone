# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 17:23:48 2023

@author: zhuhe
"""

from bs4 import BeautifulSoup
import os
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import torch

def html_to_txt(dirc, to_dirc):
    with open (dirc, 'r', encoding='utf-8') as f:
        data = f.readlines()
    data = ''.join(data)
    gfg = BeautifulSoup(data)
    res = gfg.get_text()
    with open(to_dirc, 'w', encoding='utf-8') as f:
        f.write(res)
        
def get_paragraph(dirc, split_sentence):
    with open(dirc, 'r', encoding='utf-8') as f:
        data = f.readlines()
        data = ''.join(data)
    indices = [m.start() for m in re.finditer('CCPA', data)]
    boundary = 4000
    all_script = []
    for i in indices:
        piece = data[i-boundary:i+boundary+1]
        all_period = [m.start() for m in re.finditer(r'\.', piece)]
        all_exclamation = [m.start() for m in re.finditer(r'\!', piece)]
        all_newline = [m.start() for m in re.finditer('\n', piece)]
        
        all_endings = all_period + all_exclamation + all_newline + [0, 2*boundary]
        sorted_endings = np.array(sorted(all_endings, key=lambda x: abs(boundary - x)))
        left = sorted_endings[sorted_endings<boundary]
        right = sorted_endings[sorted_endings>boundary]
        s1, s2, s3, s4, s5, s6 = left[2], left[1], left[0], right[0], right[1], right[2]
        if split_sentence == 'true':
            # print(start)
            # print(end)
            if s2 - s1 < 512:
                all_script.append(data[i-boundary+s1+1 : i-boundary+s2+1])
            if s3 - s2 < 512:
                all_script.append(data[i-boundary+s2+1 : i-boundary+s3+1])
            if s4 - s3 < 512:
                all_script.append(data[i-boundary+s3+1 : i-boundary+s4+1])
            if s5 - s4 < 512:
                all_script.append(data[i-boundary+s4+1 : i-boundary+s5+1])
            if s6 - s5 < 512:
                all_script.append(data[i-boundary+s5+1 : i-boundary+s6+1])
        else:
            if s5 - s2 < 512:
                all_script.append(data[i-boundary+s2+1 : i-boundary+s5+1])
            elif s5 - s3 < 512:
                all_script.append(data[i-boundary+s3+1 : i-boundary+s5+1])
            elif s4 - s3 < 512:
                all_script.append(data[i-boundary+s3+1 : i-boundary+s4+1])
                
    return all_script

def gen_script(all_scripts, to_file):
    with open (to_file, 'w', encoding='utf-8') as f:
        for script in all_scripts:
            f.write(script)
            f.write('\n\n')
    

        
        