# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 17:23:48 2023

@author: zhuhe
"""

import fitz
import copy
import re
from pyhtml2pdf import converter
#import pdfkit
import os
from transformers import AutoTokenizer, AutoModel

from busstone.filter import find_sentences

def delete_page_break(html, to_html):
    with open(html, 'r') as t:
        txt = t.read()
    new_txt = txt.replace("page-break-after:always", "page-break-after:auto")
    with open(to_html, 'w') as t:
        t.write(new_txt) 

def html_to_pdf(dirc, to_dirc):
    converter.convert(dirc, to_dirc)
    #config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    #pdfkit.from_file(dirc, to_dirc, configuration=config)
 
def perge(blocks):
    '''
    Get rid of footnotes, headers, etc.
    '''
    Banned = ['Table of Contents', 'TABLE OF CONTENTS', 'ITEM', 'Item']
    perged_list = []
    for i, block in enumerate(blocks):
        if any([block[4].startswith(b) for b in Banned]):
            continue
        if len(block[4]) < 35:
            continue
        # remove footers
        if i == len(blocks) - 1 and re.match(r'^\d+'+'\n$', block[4]):
            continue
        perged_list.append(block)
    return perged_list
 
def check_split_paragraph(last_block, this_block):
    a = 0 <= ord(this_block[4][0]) - ord('a') <= 25
    b = last_block[4][-2] != '.'
    return a or b

def combine_block(blocks, threshold=1.0):
    if len(blocks) <= 1:
        return blocks
    new_blocks = []
    prev = list(blocks[0])
    for i in range(1, len(blocks)):
        if blocks[i][1] - blocks[i-1][3] < threshold or check_split_paragraph(blocks[i-1], blocks[i]):   # if the begining of the current block is too close to the previous
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

def attach_next_page(prevprevpage, prevpage, thispage, nextpage, nextnextpage):
    if not thispage:
        return 
    first_paragraph = thispage[0][4]
    
    if prevpage:
        if check_split_paragraph(prevpage[-1], thispage[0]):
            first_paragraph = prevpage[-1][4] + first_paragraph
        if len(prevpage) == 1 and prevprevpage and check_split_paragraph(prevprevpage[-1], prevpage[0]):
            first_paragraph = prevprevpage[-1][4] + first_paragraph
    elif prevprevpage and check_split_paragraph(prevprevpage[-1], thispage[0]):
        first_paragraph = prevprevpage[-1][4] + first_paragraph

    last_paragraph = first_paragraph if len(thispage) == 1 else thispage[-1][4]
    if nextpage:    
        if check_split_paragraph(thispage[-1], nextpage[0]):
            last_paragraph = last_paragraph + nextpage[0][4]
            if len(nextpage) == 1 and nextnextpage and check_split_paragraph(nextpage[-1], nextnextpage[0]):
                last_paragraph = last_paragraph + nextnextpage[0][4]
    elif nextnextpage and check_split_paragraph(thispage[-1], nextnextpage[0]):  
        last_paragraph = last_paragraph + nextnextpage[0][4]
            
    thispage[0] = (
        thispage[0][0],
        thispage[0][1],
        thispage[0][2],
        thispage[0][3],
        first_paragraph,
        thispage[0][5],
        thispage[0][6],
    )
    thispage[-1] = (
        thispage[-1][0],
        thispage[-1][1],
        thispage[-1][2],
        thispage[-1][3],
        last_paragraph,
        thispage[-1][5],
        thispage[-1][6],
    )


def remove_duplicate(text):
    #remove duplicate first
    new_text = []
    for t in text:
        if t not in new_text:
            new_text.append(t)
    
    new_new_text = []
    #then remove a paragraph if it is included in another
    for i in range(len(new_text)):
        if any([new_text[i] in new_text[j] for j in range(len(new_text)) if i != j]):
            continue
        new_new_text.append(text[i])
    return new_new_text

def replace(text):
    for i in range(len(text)):
        text[i] = text[i].replace('�', 'ti')
        text[i] = text[i].replace('\n', ' ')
        text[i] = text[i].replace('U.S.', 'US')
        text[i] = text[i].replace('E.U.', 'EU')
        text[i] = text[i].replace('U.K.', 'UK')
        text[i] = text[i].replace('e.g.', 'for example')
        text[i] = text[i].replace('E.g.', 'for example')
        text[i] = text[i].replace('i.e.', 'in other words')      
    return text

def split(text):
    # split paragraph into sentences
    new_list = []
    for t in text:
        sentences = t.split('.')
        sentences = [s for s in sentences if s] # remove empty
        new_list += sentences
        new_list.append('-------------')
    return new_list        

    
def get_text(page, blocks, text):
    '''
    find the text blocks that contains word 'CCPA'
    '''
    visited = set()
    word_blocks = page.search_for("CCPA")
    for word_block in word_blocks:
        for block in blocks:
            #if the word block is in the block 
            if block[1] not in visited and\
                block[0] - 0.2 < word_block[0] < block[2] + 0.2 and\
                    block[1] - 0.2 < word_block[1] < block[3] + 0.2:
                text.append(block[4])     # append the actual text block that contains word 'CCPA' to the list
                visited.add(block[1])

    
def semantic_filter(texts):
    all_sentences = " ".join(texts).split('.') 
    filtered_sentences = find_sentences(all_sentences)
    return filtered_sentences 

def extract(pdf_path):
    '''
    Main function for extracting CCPA-related information fron the whole text
    This is method one, hard coded. Extract paragraphs that contains CCPA. 

    '''

    text = []
    with fitz.open(pdf_path) as doc:
        for i in range(2, len(doc)-2):
            prevprevpage = combine_block(
                perge(
                    doc[i-2].get_text("blocks")
                )
            )
            prevpage = combine_block(
                perge(
                    doc[i-1].get_text("blocks")
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
            nextnextpage = combine_block(
                perge(
                    doc[i+2].get_text("blocks")
                )
            )
        
            
            attach_next_page(prevprevpage, prevpage, thispage, nextpage, nextnextpage)
            get_text(doc[i], thispage, text)     
            # print(text)
    text = replace(remove_duplicate(text))    
    return text, semantic_filter(text)

if __name__ == "__main__":
    dirc = r'D:\Dropbox\Shan\10K_new\sec-edgar-filings\0000028412\10-K\0000028412-20-000034_2019-12-31\primary-document.html'   
    to_dirc = r'D:\Dropbox\Shan\10K_new\sec-edgar-filings\0000028412\10-K\0000028412-20-000034_2019-12-31\script.pdf' 
    #html_to_pdf(dirc, to_dirc)
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

    
    
    
    
    
    
    