import csv
import re
import pandas as pd
import os
import shutil

global_node_list={}
extracted_data=[]

folder_name = "real-world-datasets"
if os.path.exists(folder_name) and os.path.isdir(folder_name):
    shutil.rmtree(os.getcwd()+'\\'+folder_name)
os.mkdir(folder_name)

folder_name="intermediate"
if os.path.exists(folder_name) and os.path.isdir(folder_name):
    shutil.rmtree(os.getcwd()+'\\'+folder_name)
os.mkdir(folder_name)

def extract(header):
    
    # Regular expressions to extract the month, year, to and from fields
    month_regex = r'Date: \w+, (\d{2}) (\w+) (\d{4})'
    month_regex2 = r'Date: \w+, (\d{1}) (\w+) (\d{4})'
    from_regex = r'From: (.*)'
    to_regex = r'To: (.*)'
    cc_regex = r'Cc: (.*)'

    cc_recipent=""
    cc_emails=[]
    # Extract the month, year, to and from fields using regular expressions
    month_match = re.search(month_regex, header)
    if month_match:
        day, month, year = month_match.groups()
    month_match = re.search(month_regex2, header)
    if month_match:
        day, month, year = month_match.groups()

    from_match = re.search(from_regex, header)
    if from_match:
        sender = from_match.group(1)

    to_match = re.search(to_regex, header)
    if to_match:
        recipent = to_match.group(1)
        to_emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', recipent)

    cc_match = re.search(cc_regex, header)
    if cc_match:
        cc_recipent = cc_match.group(1)
        cc_emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', cc_recipent)

    return month,year,sender,to_emails,cc_emails

def get_node_id(email):
    if email in global_node_list.keys():
        return global_node_list[email]
    else:
        id=len(global_node_list.keys())
        global_node_list[email]=id
        return id

senders=set()
chunksize = 50000
chunks = pd.read_csv('emails.csv', chunksize=chunksize)
for chunk in chunks:
    for index, row in chunk.iterrows():
        folder= row['file'].split('/')[1] 
        if folder!="sent":
            continue 
        month,year,sender,to_emails,cc_emails=extract(row['message'])
        senders.add(sender)

chunksize = 50000
chunks = pd.read_csv('emails.csv', chunksize=chunksize)
for chunk in chunks:
    for index, row in chunk.iterrows():
        folder= row['file'].split('/')[1] 
        if folder!="sent":
            continue 
        month,year,sender,to_emails,cc_emails=extract(row['message'])
        id_from=get_node_id(sender)
        for recipent in to_emails:
            if recipent in senders:
                id_to=get_node_id(recipent)
                extracted_data.append([id_from,id_to,month,year])
        for cc_recipent in cc_emails:
            if cc_recipent in senders:
                id_to=get_node_id(cc_recipent)
                extracted_data.append([id_from,id_to,month,year])

fields=['from','to','month','year']
with open("intermediate/dataset-preprocessed-stage1.csv",'w',newline='') as datafile:
    csvwriter=csv.writer(datafile)
    csvwriter.writerow(fields)
    csvwriter.writerows(extracted_data)

email_to_id = pd.DataFrame.from_dict(global_node_list, orient='index', columns=['Id'])
email_to_id.index.name = 'Email'
email_to_id.reset_index(inplace=True)
email_to_id.to_csv("intermediate/email_to_id.csv", index=False)



file_to_data={}

def add_data(source,target,file_name):
    pair=(source,target)
    if pair in file_to_data[file_name]:
        file_to_data[file_name][pair]+=1
    pair=(target,source)
    if pair in file_to_data[file_name]:
        file_to_data[file_name][pair]+=1
    else:
        file_to_data[file_name][pair]=1


with open("intermediate/dataset-preprocessed-stage1.csv", mode ='r') as file:
    csvFile = csv.DictReader(file)
    for line in csvFile:
        month=line['month']
        year=line['year']
        file_name = "real-world-datasets/"+year+"_"+month+".csv"
        source=line['from']
        target=line['to']
        if file_name in file_to_data.keys():
            add_data(source,target,file_name)
        else: 
            file_to_data[file_name]={}
            add_data(source,target,file_name)

            
for key in file_to_data.keys():
    with open(key, mode ='w',newline='') as fl:
        writer = csv.writer(fl)
        if fl.tell()==0:
            writer.writerow(['source', 'target', 'weight'])
        for pair in file_to_data[key].keys():
            writer.writerow([pair[0],pair[1],file_to_data[key][pair]])

