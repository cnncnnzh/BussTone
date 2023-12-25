# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 17:06:22 2023

@author: zhuhe
"""

from sec_edgar_downloader import Downloader
import pandas
from datetime import timedelta


def read_CIK(file):
    content = pandas.read_excel(file, sheet_name=-1)
    date_files = list(zip(
        content['Filed'] - timedelta(days=2),
        content['Filed'] + timedelta(days=2),
        content['CIK'],
        content['Reporting for']
        )
    )
    
    return date_files
    
d1 = Downloader("Tulane", "email@xxx.com", r"D:\Dropbox\Shan\10K_new")
date_files = read_CIK(r'D:\Dropbox\Shan\10K_12082023.xlsx')

count = 0
for start, end, CIK, date in date_files[4000:]:
    start_date = str(start).split(' ')[0]
    end_date = str(end).split(' ')[0]
    CIK_num = CIK.split(' ')[1]
    num_downloaded = d1.get(
        "10-K",
        CIK_num,
        after=start_date,
        before=end_date,
        download_details=True,
        added_name='_' + str(date).split(' ')[0]
    )
    count += num_downloaded
    print(CIK)
    print('number of files downloaded ', count)