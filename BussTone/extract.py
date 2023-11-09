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
        
def get_paragraph(dirc):
    with open(dirc, 'r', encoding='utf-8') as f:
        data = f.readlines()
        data = ''.join(data)
    indices = [m.start() for m in re.finditer('CCPA', data)]
    boundary = 2000
    all_script = []
    for i in indices:
        piece = data[i-boundary:i+boundary+1]
        all_period = [m.start() for m in re.finditer(r'\.', piece)]
        all_exclamation = [m.start() for m in re.finditer(r'\!', piece)]
        all_newline = [m.start() for m in re.finditer('\n', piece)]
        
        all_endings = all_period + all_exclamation + all_newline + [0, 2*boundary]
        sorted_endings = np.array(sorted(all_endings, key=lambda x: abs(boundary - x)))
        start = sorted_endings[sorted_endings<boundary][1]
        end = sorted_endings[sorted_endings>boundary][1]
        # print(start)
        # print(end)
        all_script.append(data[i-boundary+start+1 : i-boundary+end+1])
    return all_script
 

write_script = True   
# load the model
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

data_home = r'D:\Dropbox\companyfacts\download\10K\sec-edgar-filings'
write_to = r'D:\Dropbox\Shan\Tone_analysis'

for kid in os.listdir(data_home):
    output_dirc = os.mkdir(os.path.join(write_to, kid))
    path1 = os.path.join(os.path.join(data_home, kid), 'sec-edgar-filings')
    for kid_v in os.listdir(path1):
        root = os.path.join(path1, kid_v)
        dirc = os.path.join(root, 'full-submission.txt')
        to_dirc = os.path.join(root, 'transfer.txt')
        
        # convert html to txt
        html_to_txt(dirc, to_dirc)
        
        # extract key words from txt
        all_scripts = get_paragraph(to_dirc)
        
        # write extracted paragraph to a file
        if write_script:
            to_script = os.path.join(output_dirc, kid_v)
            to_script = os.path.join(to_script, 'script.txt')
            with open (to_script, 'w', encoding='utf-8') as f:
                for script in all_scripts:
                    f.write(script)
                    f.write('\n\n')    
        scores = []
        for script in all_scripts:
            inputs = tokenizer(script, return_tensors="pt")   
            with torch.no_grad():
                logits = model(**inputs).logits
            scores.append(logits.squeeze())
                
                # predicted_class_id = logits.argmax().item()
                # model.config.id2label[predicted_class_id]
    
        
        
        