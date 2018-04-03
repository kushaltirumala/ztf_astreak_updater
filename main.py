from panoptes_client import Panoptes, Project, panoptes
import pandas as pd
from creds import username, password
import datetime
from StringIO import StringIO
import json
import logging
logging.basicConfig(filename='distribution.log',level=logging.INFO, format='%(asctime)s\n%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def create_html(images):
    with open("index.html", "w") as f:
        msg = """<!DOCTYPE html><head><title>Skipped images</title><link href='https://fonts.googleapis.com/css?family=Raleway' rel='stylesheet' type='text/css'></head><body style='text-align:center; font-family: "Raleway", sans-serif;'><h1 style='margin:50px;'>Skipped images</h1>"""
        for img in images:
            msg += """<div style='float:left; margin:20px; padding: 10px;'><img height=200 width=200 src='""" + img + """'></div>"""
        msg += """</body>"""
        f.write(msg)

def return_csv(project_link, export_type):
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
    return df

def main():
    project_link = 'aschig/ztf-astreaks'
    generate_new_set = True

    df = return_csv(project_link, 'classifications')
    values = [json.loads(row['annotations'])[0]['value'] for index, row in df.iterrows()]
    df['classification_name'] = values

    # log distribution of classifications
    print df['classification_name'].value_counts()
    logging.info(df['classification_name'].value_counts())

    # generate index.html of skipped images
    skips = df[df['classification_name']=="Skip (Includes 'Not Sure' and seemingly 'Blank Images')"]

    df_subjects = return_csv(project_link, 'subjects')

    image_srcs = [json.loads(df_subjects[df_subjects["subject_id"] == row["subject_ids"]]["locations"].iloc[0])["0"] 
              for index, row in skips.iterrows()]

    create_html(image_srcs)

if __name__ == "__main__":
    main()














