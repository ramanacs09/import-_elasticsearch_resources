#!/usr/bin/env python

import os
import json
import config
from sshTunnel import *
import requests
from requests.exceptions import ConnectionError
from elasticsearch import Elasticsearch, RequestsHttpConnection, ElasticsearchException
from requests_aws4auth import AWS4Auth



class ElasticsearchClient(object):
    """Elasticsearch class to Connect to AWS Elasticsearch"""

    def __init__(self):
        tunnel = createTunnel(config.es_tunnel_name, config.es_local_port, config.es_endpoint, config.es_remote_port,
                              config.aws_private_key, config.bastion_user, config.bastion_ip)
        self.awsauth = AWS4Auth(config.aws_access_key_id,
                                config.aws_secret_access_key, config.aws_region,'es')
        self.es = Elasticsearch(
            hosts=[{'host': config.localhost, 'port': config.es_local_port}],
            http_auth=self.awsauth,
            use_ssl=True,
            verify_certs=False,
            connection_class=RequestsHttpConnection
        )

    def put_template(self, template_name, template_json):
        create = False
        if not self.template_exists(template_name):
            create = True
        try:
            print("Uploading template.... "+str(template_name))
            self.es.indices.put_template(name=template_name, body=template_json, create=create)
        except Exception as err:
            print("Error in uploading template %s and details are -- %s" % (template_name, err))
            

    def cluster_health(self):
        try:
           print(self.es.cluster.health())
        except ElasticsearchException as ex:
           print("Error in retrieving cluster health details....")

    def es_info(self):
        try:
           print(self.es.info())
        except:
           print("Error in retrieving cluster information....")

    def template_exists(self, template_name):
        return self.es.indices.exists_template(name=template_name)

    def put_index_patterns(self, index_id, index_input_json):
        try:
           print("Uploading index pattern %s" % (index_id))
           self.es.index(index='.kibana', doc_type='index-pattern', id=index_id, body=index_input_json)
        except Exception as e:
           print("Error in uploading index pattern %s and details are -- %s" % (index_id, e))

    def clear_kibana_objects(self, type):
        query_body = '{"query":{"match_all":{}}}'
        try:
            self.es.delete_by_query(index='.kibana', doc_type=type, body=query_body)
        except Exception as e:
            print("Error in deleting %s and details are-- %s" % (type, e))

    def put_kibana_object(self, kibana_obj):
        try:
           host = 'https://'+config.localhost+':'+str(config.es_local_port)
           url = "%s/%s/%s/%s" % (host, '.kibana', kibana_obj['_type'], kibana_obj['_id'])
           headers = {'Content-Type': 'application/json'}
           print("Uploading kibana object of type %s and the id is %s" % (kibana_obj['_type'], kibana_obj['_id']))
           response = requests.post(url, headers=headers, data=json.dumps(kibana_obj['_source']), verify=False)
           if response.status_code not in [200,201]:
               print("Error in uploading %s of type %s and details are %s" % (kibana_obj['_id'], kibana_obj['_type'],str(response.json())))     
        except ConnectionError as ce:
           print(ce) 

    def closeConnection(self):
        closeSSHTunnel(config.es_tunnel_name, config.bastion_user, config.bastion_ip)
