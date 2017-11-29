import numpy as np
import itertools
from scipy.sparse import csr_matrix
import pickle as pk

def create_skill_base(skill_dict):
	
	return skill_base
def generate_word_index_mapping(skills):
    # create word - index mappings
    mappings = {}
    for i in range(len(skills)):
        mappings[skills[i]] = i
    
    return mappings

def create_co_matrix(skill_base, skill_dict):
    count = []
    rows = []
    columns = []
    num_skills = len(skill_base)
    mappings = generate_word_index_mapping(skill_base)
    for i in range(len(skill_dict)):
        profile = skill_dict.values()[i]
        if(len(profile)<2):
            continue
        for pair in itertools.combinations(profile,2):
            idx1 = mappings[pair[0]]
            idx2 = mappings[pair[1]]
            rows.append(idx1)
            columns.append(idx2)
            count.append(1)
    
    co_occurrence = csr_matrix((count,(rows,columns)), shape = (num_skills,num_skills))
    
    return co_occurrence

if __name__ == '__main__':
	with open("linkedin_person_skills_all.pkl",'r') as f:
		skill_dict = pk.load(f)
	f.close()
    skill_base = create_skill_base(skill_dict)
    co_matrix = create_co_matrix(skill_base,skill_dict)

