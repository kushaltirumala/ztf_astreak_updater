from panoptes_client import Panoptes, Project, panoptes
import pandas as pd
from creds import username, password
import datetime
from StringIO import StringIO
import json

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
