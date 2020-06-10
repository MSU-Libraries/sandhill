from . import solr
from flask import request

def load_data(data_dict):
    data = None
    if 'type' in data_dict and data_dict['type'] == 'solr': 
        data = solr.query_record(data_dict)
    return data
