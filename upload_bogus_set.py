from panoptes_client import Panoptes, Project, panoptes, Subject, SubjectSet
import pandas as pd
from creds import username, password
import datetime
from StringIO import StringIO
import json
import logging
import os
import csv

upload_frequency = 750
upper_limit = 5000

def create_subject_set(directory, project):
	temp_break = False
	number_uploaded = 0
	subject_set = SubjectSet()
	subject_set.links.project = project
	subject_set.display_name = "new_upload"
	subject_set.save()
	subjects_to_add = []
	for sub_dir in os.listdir(directory): 
		print("ON SUB DIRECTORY %s \n" % sub_dir)
		temp_dir = os.path.join(directory, sub_dir)
		if os.path.isdir(temp_dir):
			for filename in os.listdir(temp_dir):
				full_path = os.path.join(temp_dir, filename)
				print("SAVING FILE: %s \n" % full_path)
				subject = Subject()
				subject.links.project = project
				subject.add_location(full_path)
				subject.metadata['filename'] = filename
				subject.save()
				subjects_to_add.append(subject)
				number_uploaded += 1
				if (number_uploaded % upload_frequency == 0):
					print ("saving subject set for %d batch")
					subject_set.add(subjects_to_add)
					subject_set.save()
					subjects_to_add = []
				if (number_uploaded > upper_limit):
					temp_break = True
					break
			if temp_break:
				break;

	if (len(subjects_to_add) != 0):
		print("ADDING REST OF THE SUBJECTS TO SUBJECT SET\n")
		subject_set.add(subjects_to_add)


Panoptes.connect(username=username, password=password)
project_link = 'aschig/ztf-astreaks'
project = Project.find(slug=project_link)
create_subject_set("bogus_set_20180523/", project)
