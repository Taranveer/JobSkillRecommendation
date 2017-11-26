#import requests
from lxml import html
from bs4 import BeautifulSoup
import sys
import os
import pickle
import csv
import re

input_directory = sys.argv[1]

def get_filelist(folder):
    return [folder+'/'+name for name in os.listdir(folder)
            if not os.path.isdir(os.path.join(folder, name)) and name[0] != '.']
def get_folderlist(folder):
    return [folder+'/'+name for name in os.listdir(folder)
            if os.path.isdir(os.path.join(folder, name))]

folders = get_folderlist(input_directory)
files = []

for f in folders:
	files += get_filelist(f)

skill_set = set()

for each_file in files:
    with open(each_file, 'r') as file:
        soup = BeautifulSoup(file, "html.parser")
        result1 = (soup.find_all("li", "endorse-item has-endorsements "))
        #result2 = (soup.find_all("a", href=re.compile("https://www.linkedin.com/topic/")))
        #<a href="https://in.linkedin.com/topic/hibernate?trk=pprofile_topic" title="Hibernate"><span class="wrap">Hibernate</span></a>
        result2 = (soup.find_all("a", href=re.compile("linkedin.com/topic/"))) #the other kind of format for skills

        #if len(result1 + result2) < 10:
        #    print(each_file +"has: " + str(len(result1 + result2)))

        for s in result1:
            if 'data-endorsed-item-name' in s.attrs:
                skill_set.add(s['data-endorsed-item-name'])
            #print(type(s.attrs)) dictionary
        for s in result2:
            if 'title' in s.attrs:
                skill_set.add(s['title'])


print(skill_set)

with open("Skill_List"+str(input_directory) + '.txt', 'w') as f:
    for i in skill_set:
	    f.write(i+'\n')
