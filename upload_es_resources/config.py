#!/usr/bin/env python
import os

# es config params
es_tunnel_name = 'es-tunnel'
es_local_port = 2443
es_remote_port = 443
es_endpoint = "search-dtvnivpa1d-elasticsearch-h6kzkl5od22vfsy7i72ib7vwhq.us-west-2.es.amazonaws.com"

# common config params
aws_private_key = os.environ['aws_private_key']
bastion_user = 'centos'
bastion_ip = "34.222.33.88"
localhost = '127.0.0.1'
aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
aws_region = os.environ['aws_region']
