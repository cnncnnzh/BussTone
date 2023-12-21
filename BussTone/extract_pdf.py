# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 17:23:48 2023

@author: zhuhe
"""

import requests
import fitz
import copy
import re
from pyhtml2pdf import converter
import os

def delete_page_break(html):
    with open(html, 'r') as t:
        txt = t.read()
    new_txt = txt.replace("page-break-after:always", "page-break-after:auto")
    with open(html, 'w') as t:
        t.write(new_txt) 

def html_to_pdf(dirc, to_dirc):
    converter.convert(dirc, to_dirc)
    
def combine_block(blocks, threshold=1.2):
    if len(blocks) <= 1:
        return blocks
    new_blocks = []
    prev = list(blocks[0])
    for i in range(1, len(blocks)):
        if blocks[i][1] - blocks[i-1][3] < threshold:  # if the begining of the current block is too close to the previous
            prev[4] += blocks[i][4]
            prev[3] = blocks[i][3]
            if i == len(blocks) - 1:
                new_blocks.append(prev) 
        else:
            new_blocks.append(prev)
            prev = list(blocks[i])
            if i == len(blocks) - 1:
                new_blocks.append(prev) 
    return new_blocks

def perge(blocks):
    perged_list = []
    for i, block in enumerate(blocks):
        if i == 0 and (block[4].startswith('Table of Contents') or block[4].startswith('ITEM')):
            continue
        if len(block[4]) < 15:
            continue
        # remove footers
        if i == len(blocks) - 1 and re.match(r'^\d+'+'\n$', block[4]):
            continue
        perged_list.append(block)
    return perged_list

def attach_next_page(prevpage, thispage, nextpage):
    if not thispage:
        return 
    if prevpage:
        if 0 <= ord(thispage[0][4][0]) - ord('a') <= 25:
                thispage[0] = (
                    thispage[0][0],
                    thispage[0][1],
                    thispage[0][2],
                    thispage[0][3],
                    prevpage[-1][4] + thispage[0][4],
                    thispage[0][5],
                    thispage[0][6],
                )
    if nextpage:
        if 0 <= ord(nextpage[0][4][0]) - ord('a') <= 25:
            if nextpage:
                thispage[-1] = (
                    thispage[-1][0],
                    thispage[-1][1],
                    thispage[-1][2],
                    thispage[-1][3],
                    thispage[-1][4] + nextpage[0][4],
                    thispage[-1][5],
                    thispage[-1][6],
                )

def get_text(page, blocks, text):
    visited = set()
    word_blocks = page.search_for("CCPA")
    for word_block in word_blocks:
        for block in blocks:
            #if the word block is in the block 
            if block[1] not in visited and block[1] - 0.2 < word_block[1] < block[3] + 0.2:
                text.append(block[4])
                visited.add(block[1])

def replace_garble(text):
    for i in range(len(text)):
        text[i] = text[i].replace('�', 'ti')
    return text

def extract(pdf_path):
    text = []
    with fitz.open(pdf_path) as doc:
        for i in range(1, len(doc)-1):
            prevpage = combine_block(
                perge(
                    doc[i-1].get_text("blocks")
                )
            )
            if i > 2 and len(prevpage) == 0:
                prevpage = combine_block(
                    perge(
                        doc[i-2].get_text("blocks")
                    )
                )
            thispage = combine_block(
                perge(
                    doc[i].get_text("blocks")
                )
            )
            nextpage = combine_block(
                perge(
                    doc[i+1].get_text("blocks")
                )
            )
            if i < len(doc) - 2 and len(nextpage) == 0:
                nextpage = combine_block(
                    perge(
                        doc[i+2].get_text("blocks")
                    )
                )
            
            
            attach_next_page(prevpage, thispage, nextpage)
            get_text(doc[i], thispage, text)
            
    return text


if __name__ == "main":
    dirc = r'D:\Dropbox\Shan\10K_new\sec-edgar-filings\0000028412\10-K\0000028412-20-000034_2019-12-31\primary-document.html'   
    to_dirc = r'D:\Dropbox\Shan\10K_new\sec-edgar-filings\0000028412\10-K\0000028412-20-000034_2019-12-31\script.pdf' 
    html_to_pdf(dirc, to_dirc)
    text = extract(os.path.join(to_dirc))


# API_ENDPOINT = "https://api.sec-api.io/filing-reader"
# API_KEY = "3a4102b4710db02169ba0f0a6638f8d2b155bed658ab97e283529d867133a942"

# # filing_url = "https://www.sec.gov/Archives/edgar/data/1294133/000156459020006402/ingn-10k_20191231.htm"
# # filing_url = "https://www.sec.gov/ix?doc=/Archives/edgar/data/1304421/000155837021001947/cnsl-20201231x10k.htm"
# # filing_url = "https://www.sec.gov/Archives/edgar/data/5513/000000551322000030/unm-20211231.htm"
# # filing_url = "https://www.sec.gov/Archives/edgar/data/26058/000156459022007183/cts-10k_20211231.htm"
# # filing_url = 'https://www.sec.gov/Archives/edgar/data/21344/000002134422000009/ko-20211231.htm'
# filing_url = 'https://www.sec.gov/Archives/edgar/data/28412/000002841220000034/a201910k.htm'
# # filing_url = 'https://www.sec.gov/Archives/edgar/data/93314/000147793222001740/vnrx_10k.htm'
# # filing_url = 'https://www.sec.gov/Archives/edgar/data/84129/000155837021004887/rad-20210227x10k.htm'
# pdf_path = r'D:\Dropbox\Shan\PDFs\filing6.pdf'
# txt_path = r'D:\Dropbox\Shan\PDFs\test6.txt'

# api_url = API_ENDPOINT + "?token=" + API_KEY + "&url=" + filing_url + "&type=pdf"
# response = requests.get(api_url)

# with open(pdf_path, 'wb') as f:
#     f.write(response.content)

    
    
    
    
    
    
    