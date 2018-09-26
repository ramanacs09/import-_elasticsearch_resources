#!/usr/bin/env python

import os
import json
import boto3
from upload_es_resources.elasticsearch_client import ElasticsearchClient
from botocore.exceptions import ClientError
from upload_es_resources.convert_to_valid_json import convert


def load_files_from_s3(s3_bucket):
    resource = None
    es = None
    try:
        resource = boto3.resource('s3', region_name=os.environ['aws_region'])
    except ClientError as ce:
        raise ce
    try:
        my_bucket = resource.Bucket(s3_bucket)

        prefix = 'Index Patterns/'
        input_key = ""
        index_pattern_files = list(my_bucket.objects.filter(Prefix=prefix))
        for pattern_file in index_pattern_files:
            if prefix != pattern_file.key:
               input_key = pattern_file.key

        if input_key != "":
            input_file = my_bucket.download_file(input_key, 'input_file.json')
            convert('input_file.json', 'output_file.json')

        es = ElasticsearchClient()

        # Elasticsearch cluster details
        print("\n*********Elasticsearch cluster info********")
        print(es.es_info())

        print("\n*********Elasticsearch cluster health details***********")
        print(es.cluster_health())

        # Reading template files from s3
        print("\n*********Uploading template files from "+s3_bucket+"************")
        prefix = 'Templates/'
        template_files = list(my_bucket.objects.filter(Prefix=prefix))
        list_of_templates = [template_file for template_file in template_files if prefix != template_file.key]
        for template_file in list_of_templates:
            content = template_file.get()['Body'].read()
            upload_template_to_es(content, es)

        # Clearing kibana objects
        print("\n*********Clearing kibana objects**************")
        es.clear_kibana_objects('search')
        es.clear_kibana_objects('dashboard')
        es.clear_kibana_objects('visualization')

        # Reading kibana objects from s3
        print("\n*********Uploading kibana objects from "+s3_bucket+"************")
        prefix = 'Kibana Objects/'
        kibana_files = list(my_bucket.objects.filter(Prefix=prefix))
        list_of_kibana_obj = [obj for obj in kibana_files if prefix != obj.key]
        for kibana_file in list_of_kibana_obj:
            content = kibana_file.get()['Body'].read()
            upload_kibana_objects(content, es)

        # Reading index patterns from s3
        if input_key != "":
            print("\n*********Uploading index patterns from "+s3_bucket+"************")
            with open('output_file.json', 'r') as fd:
                data = fd.read()
            upload_index_patterns(data, es)

            # Deleting input and output json files
            os.remove('input_file.json')
            os.remove('output_file.json')
        else:
           print("No index patterns file found... So skipping uploading index patterns...")

    except Exception as e:
        print(e)
    finally:
        print("***********Closing Connection**********")
        es.closeConnection()


def upload_template_to_es(content, es):
    template_name = None
    json_content = json.loads(content)
    for key, value in json_content.iteritems():
        template_name = key
        es.put_template(template_name, value)


def upload_kibana_objects(content, es):
    json_content = json.loads(content)
    for obj in json_content:
        es.put_kibana_object(obj)

def upload_index_patterns(content, es):
    index_content = json.loads(content)
    filtered_source = index_content['hits']['hits']
    for pattern in filtered_source:
        es.put_index_patterns(pattern['_source']['title'], pattern['_source'])


if __name__ == '__main__':
    load_files_from_s3(os.environ['ES_RESOURCES_BUCKET'])
