import numpy as np
import itertools
from scipy.sparse import csr_matrix
import pickle as pk
import sys
import re
import os
from sklearn.feature_extraction.text import CountVectorizer
from scripts.data_prepration_scripts.process_concepts import getCleanText
#import builtin

def create_skill_base(skill_dict):
    
    skill_dict_copy = skill_dict.copy()
    
    for n,i in enumerate(skill_dict):
        skill_dict_copy[i] = sorted(list(skill_dict[i]))
        for j in range(len(skill_dict_copy[i])):
            skill_dict_copy[i][j] = getCleanText(skill_dict_copy[i][j])
        if n%1000==0:
            print(n)
        
    print("Copy Made!")
    
    skill_base = set()
    for n,i in enumerate(skill_dict_copy):
        skill_base = skill_base | set(skill_dict_copy[i])
        if n%1000==0:
            print(n)
        
    skill_base = (list(skill_base))
    print("Cleaning up!")
    for n,i in enumerate(skill_dict_copy):
        skill_dict_copy[i] = list(set(skill_dict_copy[i]))
        if n%1000==0:
            print(n)
    
    return skill_base,skill_dict_copy
    
    
def generate_word_index_mapping(skills):
    # create word - index mappings
    mappings = {}
    inv_mappings = {}
    for i in range(len(skills)):
        mappings[skills[i]] = i
        inv_mappings[i] = skills[i]
    return mappings, inv_mappings

def create_co_matrix(skill_base, skill_dict):
    def create_co_matrix(skill_base, skill_dict):
    count = []
    rows = []
    columns = []
    
    num_skills = len(skill_base)
    
    mappings, inv_map = generate_word_index_mapping(skill_base)
    for n,i in enumerate(skill_dict):
        profile = skill_dict[i]
        if(len(profile)<2):
            continue
        for pair in itertools.combinations(profile,2):
            idx1 = mappings[pair[0]]
            idx2 = mappings[pair[1]]
            rows.append(idx1)
            columns.append(idx2)
            count.append(1)
        if n%3000==0:
            print(n)
    co_occurrence = csr_matrix((count,(rows,columns)), shape = (num_skills,num_skills))
    
    return mappings,inv_map,co_occurrence

if __name__ == '__main__':
	with open("linkedin_person_skills_all.pkl",'r') as f:
		skill_dict = pk.load(f)
	skill_base,skill_dict = create_skill_base(skill_dict)
    skill_2_index_mapping, index_2_skill_mapping, skill_co_occurence_matrix = create_co_matrix(skill_base,skill_dict)
    ##order of co-occurence
    skill_co_occurence_matrix = skill_co_occurence_matrix.T + skill_co_occurence_matrix
    #Pickled files for future use
    with open("C:\\Users\\Swapnil\\Downloads\\05899\\Project\\JobSkillRecommendation\\skills\\skill_2_index_mapping_pickle.pkl",'wb') as file:
    pk.dump(skill_2_index_mapping,file)
    with open("C:\\Users\\Swapnil\\Downloads\\05899\\Project\\JobSkillRecommendation\\skills\\index_2_skill_mapping_pickle.pkl",'wb') as file:
    pk.dump(index_2_skill_mapping,file)
    with open("C:\\Users\\Swapnil\\Downloads\\05899\\Project\\JobSkillRecommendation\\skills\\skill_co_occurence_pickle.pkl",'wb') as file:
    pk.dump(skill_co_occurence_matrix,file)
