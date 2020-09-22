import xlrd
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
import argparse

# set up args
parser = argparse.ArgumentParser(description='Script so useful.')
parser.add_argument('--folder-num', type=str, required=True)
parser.add_argument('--overwrite-alltime', type=str, default='true')

args = parser.parse_args()
folder_num = args.folder_num
overwrite = args.overwrite_alltime

# actual codes
front_url = 'https://scholar.google.com/scholar?start='
back_url = '&hl=en&as_sdt=2005&sciodt=0,5&as_ylo=2016&cites=17089488661544618798&scipsc='

def get_url_content(page_num):
    url = ''.join(map(str, [front_url, page_num*10, back_url]))
    print('Parsing from ', url)
    content = requests.get(url).text
    return content

root_name = "source_codes/google_scholar_search_"

def get_saved_content(page_num):
    path = ''.join(map(str, [root_name, str(folder_num), "/page_", str(page_num), ".txt"]))
    with open(path, encoding="utf8") as file:
        content = file.read()
        file.close()
    return content

# auto for auto extraction 
root_folder = ''.join(map(str, [root_name, str(folder_num)]))
num_of_items = len([name for name in os.listdir(root_folder) if os.path.isfile(os.path.join(root_folder, name))])-1

def parse_page_info(get_content_method, page_num):
    
    content = get_content_method(page_num)
    page = BeautifulSoup(content, 'lxml')

    title_list = []
    url_list = []
    source_list = []
    citation_list = []

    for entry in page.find_all("h3", attrs={"class": "gs_rt"}):
        title_list.append(entry.a.text)
        url_list.append(entry.a['href'])

    for entry in page.find_all(attrs={"class": "gs_a"}):
        source_list.append(entry.text)

    for entry in page.find_all(attrs={"class": "gs_fl"}):
        if '[' not in entry.text:
            citation_list.append(entry.text)

    page_df = pd.DataFrame(
        {'title': title_list,
         'author-source': source_list,
         'url_link': url_list,
         'cited_by': citation_list
        })
    
    return page_df

summary_df = pd.DataFrame()

for i in range(0,num_of_items):
    print('Parsing page '+str(i)+'...')
    page_df = parse_page_info(get_saved_content, page_num=i)
    page_df['page_num'] = i
    summary_df = summary_df.append(page_df)
    summary_df['search_round'] = str(folder_num)

summary_df.to_csv('output/google_scholar_search_'+str(folder_num)+'.csv', index=False)

if overwrite:
    # append only new rows
    alltime_df = pd.read_csv('output/google_scholar_search_all.csv')
    alltime_df = pd.concat([alltime_df, summary_df])
    alltime_df = alltime_df.drop_duplicates(subset=['title', 'author-source'], keep='first')
    alltime_df.to_csv('output/google_scholar_search_all.csv', index=False)