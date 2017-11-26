'''
Total Number of records = 846613. To be used in &limit= section

use the site http://www.onetcenter.org/taxonomy.html to find the onet encoding of desired job and pass it as argmument

--file "abc" will store the data in abc.csv file
'''

import json
import urllib2
import argparse
import csv

if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument("--id", help="The unique identfier for the job posting")
	# parser.add_argument("--salaryCurrency", help="The currency (in 3-letter ISO 4217 format) of the salary")
	parser.add_argument("--occupationalCategory", help="categories describing the job. Use BLS O*NET-SOC taxonomy. Includes list of applicable ONET encodings")
	# parser.add_argument("--employmentType", help="Type of employment (e.g. full-time, part-time, contract, temporary, seasonal, internship)")
	# parser.add_argument("--qualifications", help="Specific qualifications required for this role")
	# parser.add_argument("--experienceRequirements", help="Description of experience requirements for the position")
	# parser.add_argument("--educationRequirements", help="Description of education requirements for the position")
	# parser.add_argument("--baseSalary", help="The base salary of the job or of an employee for the specified role")
	# parser.add_argument("--id", help="The unique identfier for the job posting")

	parser.add_argument("--file", help="Name of output csv file")

	#totalRecords = 




	args = parser.parse_args()

	main_url = 'http://opendata.cs.vt.edu/api/3/action/datastore_search?resource_id=jobpostings'

	fields = '&fields=title,normalizedTitle,responsibilities,skills,jobDescription'

	filters = '&q={'

	if args.occupationalCategory:
		filters += '"occupationalCategory":"' + args.occupationalCategory + '"'

	if args.id:
		if args.occupationalCategory:
			filters += ','
		filters += '"id":"' + args.id + '"'

	filters += '}'

	url = main_url + fields + filters + "&limit=846613"

	data = json.load(urllib2.urlopen(url))

	# Check if the results are true
	if data['result']['records']:
		filename = args.file + ".csv"
		f = csv.writer(open(filename, "wb+"))
		f.writerow(["title", "normalizedTitle", "responsibilities", "skills", "jobDescription"])
		index = 0
		for x in data['result']['records']:
			f.writerow([data['result']['records'][index]['title'],
				data['result']['records'][index]['normalizedTitle']['onetName'],
				data['result']['records'][index]['responsibilities'],
				data['result']['records'][index]['skills'],
				data['result']['records'][index]['jobDescription']]) 
			index += 1





























