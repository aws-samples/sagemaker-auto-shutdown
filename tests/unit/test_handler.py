import json

import pytest

import os

from cleaner import app

def test_config_parser():
    os.environ["ENDPOINT_EXCLUDE_TAG"] = '{ "Key": "env", "Value": "prod" }'
    os.environ["NOTEBOOK_EXCLUDE_TAG"] = '{ "Key": "project", "Value": "ciritical" }'
    
    config = app.parse_config()
    
    assert config["ENDPOINT_EXCLUDE_TAG"] ==  { 'Key': 'env', 'Value': 'prod' }
    assert config["NOTEBOOK_EXCLUDE_TAG"] ==  { 'Key': 'project', 'Value': 'ciritical' }
    
def test_config_parser_has_default():
    del os.environ["ENDPOINT_EXCLUDE_TAG"]
    del os.environ["NOTEBOOK_EXCLUDE_TAG"]
    
    config = app.parse_config()
    
    assert config["ENDPOINT_EXCLUDE_TAG"] == None 
    assert config["NOTEBOOK_EXCLUDE_TAG"] == None
    
def test_try_parse_env():
    os.environ["ENDPOINT_EXCLUDE_TAG"] = '{ "Key": "env", "Value": "prod" }'
    oneEnv = app.try_parse_env("ENDPOINT_EXCLUDE_TAG")
    assert oneEnv == { 'Key': 'env', 'Value': 'prod' }
    
def test_try_parse_env_invalid_json():
    
    os.environ["ENDPOINT_EXCLUDE_TAG"] = "MAL_FORMED_JSON:{}"
    with pytest.raises(Exception):
        oneEnv = app.try_parse_env("ENDPOINT_EXCLUDE_TAG")