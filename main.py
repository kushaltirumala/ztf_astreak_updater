from panoptes_client import Panoptes, Project, panoptes
import pandas as pd
from creds import username, password
import datetime

Panoptes.connect(username=username, password=password)
project = Project.find(slug='aschig/ztf-astreaks')


try:
    meta_class = project.describe_export('classifications')
    last_generated = meta_class['media'][0]['updated_at'][0:19]
    tdelta = (datetime.datetime.now() - datetime.datetime.strptime(last_generated, '%Y-%m-%dT%H:%M:%S')).total_seconds()
except panoptes.PanoptesAPIException:
    # means a classifications set has never been created
    tdelta = 68401 # just to make it more than 24 hours
    

if (300 + tdelta / 60) >= 24 * 60:
    classifications = project.get_export('classifications', generate=True)
else: 
    # means that last export was generated less than 24 hours ago so we cannot generate a new one
    classifications = project.get_export('classifications')



