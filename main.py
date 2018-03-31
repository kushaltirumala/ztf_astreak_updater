from panoptes_client import Panoptes, Project, panoptes
import pandas as pd
from creds import username, password
import datetime
from StringIO import StringIO
import json

def create_html(images):
    with open("index.html", "w") as f:
        msg = """<!DOCTYPE html><head><title>Skipped images</title><link href='https://fonts.googleapis.com/css?family=Raleway' rel='stylesheet' type='text/css'></head><body style='text-align:center; font-family: "Raleway", sans-serif;'><h1 style='margin:50px;'>Skipped images</h1>"""
        for img in images:
            msg += """<div style='float:left; margin:20px; padding: 10px;'><img height=200 width=200 src='""" + img + """'></div>"""
        msg += """</body>"""
        print msg
        f.write(msg)

project_link = 'aschig/ztf-astreaks'
# project_link = 'kushaltirumala/test-2'
export_type = 'classifications'
generate_new_set = True

Panoptes.connect(username=username, password=password)
project = Project.find(slug=project_link)


try:
    meta_class = project.describe_export(export_type)
    last_generated = meta_class['media'][0]['updated_at'][0:19]
    tdelta = (datetime.datetime.now() - datetime.datetime.strptime(last_generated, '%Y-%m-%dT%H:%M:%S')).total_seconds()
except panoptes.PanoptesAPIException:
    # means a classifications set has never been created
    tdelta = 68401 # just to make it more than 24 hours
    
# means it has been 24 hours until 
if (300 + tdelta / 60) >= 24 * 60 and generate_new_set:
    project.generate_export(export_type)
    Panoptes.connect(username=username, password=password)
    project = Project.find(slug=project_link)
    # this is to wait for export to be finished in the case of large sets
    while True: 
        export_description = project.describe_export(export_type)
        export_metadata = export_description['media'][0]['metadata']
        if export_metadata.get('state', '') in ('ready', 'finished'):
            print 'Done exporting data!'
            break



resp = project.get_export(export_type)
buff = StringIO(resp.content)
df = pd.read_csv(buff)

# df = pd.read_csv('ztf-astreaks-classifications_20180328.csv')
values = [json.loads(row['annotations'])[0]['value'] for index, row in df.iterrows()]
df['classification_name'] = values
# log distribution of classifications
print df['classification_name'].value_counts()

# generate index.html of skipped images
skips = df[df['classification_name']=="Skip (Includes 'Not Sure' and seemingly 'Blank Images')"]

# will fill with actual images srcs from subject set
# image_srcs = [
#     "https://panoptes-uploads.zooniverse.org/production/subject_location/94362a72-3597-4640-add6-e1b3ce4ec3a6.jpeg",
#     "https://panoptes-uploads.zooniverse.org/production/subject_location/d6d70aba-bf36-4c82-ace7-30ebf791b3fb.jpeg",
#     "https://panoptes-uploads.zooniverse.org/production/subject_location/f4c91f1b-037e-44d6-95d5-83fed4e00879.jpeg"
# ]
# create_html(image_srcs)














