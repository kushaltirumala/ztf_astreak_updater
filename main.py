from panoptes_client import Panoptes, Project, panoptes
import pandas as pd
from creds import username, password
import datetime
from StringIO import StringIO

# project_link = 'aschig/ztf-astreaks'
project_link = 'kushaltirumala/test'
export_type = 'subjects'
generate_new_set = False

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
    wait_export(export_type)

resp = project.get_export(export_type)
buff = StringIO(resp.content)
df = pd.read_csv(buff)



