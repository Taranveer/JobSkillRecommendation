import pickle as pk
import numpy as np
import sklearn
from sklearn.metrics.pairwise import cosine_similarity
import argparse
from collections import Counter
import itertools

def parseArguments():
	args = argparse.ArgumentParser()
	#parse command line arguments
	args.add_argument("-m", "--co_matrix", type = str, default = 'C:\\github\\laeds\\JobSkillRecommendation\\skills\\SVD_U.pkl',help='enter the path of cooccurence file')
	args.add_argument("-i", "--skill2index", type =str, deafult = 'C:\\github\\laeds\\JobSkillRecommendation\\skills\\skill_2_index_mapping_pickle.pkl',help='enter the path of skill-index mapping')
	args.add_argument("-s", "--index2skill", type =str, deafult = 'C:\\github\\laeds\\JobSkillRecommendation\\skills\\index_2_skill_mapping_pickle.pkl',help='enter the path of index-skill mapping')

	return args

class LinkedInProfile(object):
	def __init__(args):
		with open(args["co_matrix"],"rb") as f:
			self.co_matrix = pk.load(f)
		with open(args["skill2index"],"rb") as f:
			self.skill2index = pk.load(f)
		with open(args["index2skill"],"rb") as f:
			self.index2skill = pk.load(f)

	# given an index corresponding to a skill, returns n closest skills
	def findClosestSkills(self,index,n):
		# find cosine similarity of the skill with every other skill and return 'n' skills with highest similarity
		closest_skills = list(cosine_similarity(self.co_matrix,self.co_matrix[index]))
		closest_indexes = np.argsort(closest_skills)[::-1]
		skills = []
		for i in range(n):
			skills.append(self.index2skill[closest_indexes[i]])
		return skills

	# given a lists of skills, returns the most similar skills
	def getSimilarConcepts(self, skills, num_top_skills, intersection):
		skill_indexes = []
		# original_skills = []

		# every string is represented as S_'skill name'_S. So we convert to 'skill name'
		skills_list = []
		for string in skills:
			skills_list.append(string[2:-2])

		for skill in skills_list:
			skill_indexes.append(self.skill2index[skill])
			# original_skills.append(self.index2skill[skill2index])
		closest_skills = []
		for index in skill_indexes:
			closest_skills.append(findClosestSkills(index,num_top_skills))

		similar_skills = []
		skills_stats = Counter(list(itertools.chain.from_iterable(closest_skills))).items()
		for i in range(len(skills_stats.items())):
			if(skills_stats.items()[i][1]>=intersection):
				similar_skills.append(skills_stats.items()[i][0])

		return skills_list + list(set(similar_skills)-set(skills_list))


if __name__ == '__main__':

	args = parseArguments()
	profile = LinkedInProfile(args)
