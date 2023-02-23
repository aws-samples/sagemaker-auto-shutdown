import json
import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def try_parse_env(key):
    if key not in os.environ:
        logger.warning("No %s set, will not exlude any resources.", key)
    else:
        try:
            return json.loads(os.getenv(key, "null"))
        except Exception as e:
            logger.error("Invalid syntax for %s, abort to avoid deleting resources.", key)
            raise e

def parse_config():
    return {
        "ENDPOINT_EXCLUDE_TAG": try_parse_env("ENDPOINT_EXCLUDE_TAG"),
        "NOTEBOOK_EXCLUDE_TAG": try_parse_env("NOTEBOOK_EXCLUDE_TAG"),
        "MAX_COUNT": try_parse_env("MAX_COUNT") or 100
    }

def is_serverless_endpoint(client, endpoint_name):
    endpoint = client.describe_endpoint(EndpointName = endpoint_name)
    endpoint_config = client.describe_endpoint_config(EndpointConfigName = endpoint["EndpointConfigName"])
    product_variants = endpoint_config["ProductionVariants"]
    return "ServerlessConfig" in product_variants[0]

def get_endpoint_names(client, config):
    logger.info('Getting InService endpoints')
    endpoint_names = []
    endpoints =  client.list_endpoints(
        SortBy = 'CreationTime',
        SortOrder = 'Descending',
        StatusEquals = 'InService',
        MaxResults = config["MAX_COUNT"]
    )["Endpoints"]
    
    for each in endpoints:
        name = each["EndpointName"]
        tags = client.list_tags(ResourceArn = each["EndpointArn"])
        if config["ENDPOINT_EXCLUDE_TAG"] in tags['Tags']:
            logger.debug('Ignoring because of tag: %s', name)
            continue
        if is_serverless_endpoint(client, name):
            logger.debug('Ignoring because of serverless endpoint: %s', name)
            continue
        logger.debug('Will delete: %s', name)
        endpoint_names.append(name)
    return endpoint_names

def get_notebook_names(client, state, config):
    logger.info('Getting %s notebooks', state)
    notebook_names = []
    notebooks = client.list_notebook_instances(
        SortBy = 'CreationTime',
        SortOrder = 'Descending',
        StatusEquals = state,
        MaxResults = config["MAX_COUNT"]
    )["NotebookInstances"]
    for each in notebooks:
        if each['NotebookInstanceStatus'] == state:
            name = each["NotebookInstanceName"]
            tags = client.list_tags(ResourceArn = each["NotebookInstanceArn"])
            if config["NOTEBOOK_EXCLUDE_TAG"] in tags['Tags']:
                logger.debug('Ignoring because of tag: %s', name)
                continue
            logger.debug('Will delete: %s', name)
            notebook_names.append(name)
    return notebook_names

def delete_endpoints(client, endpoint_names):
    logger.info('Deleting endpoints')
    count = 0
    for name in endpoint_names:
        client.delete_endpoint(EndpointName = name)
        count += 1
    logger.info('Deleted %s endpoints', count)
    return

def stop_notebook_instances(client, notebook_names):
    logger.info('Stopping notebooks')
    count = 0
    for name in notebook_names:
        try:
            client.stop_notebook_instance(NotebookInstanceName = name)
            count += 1
        except:
            continue
    logger.info('Stopped %s notebooks', count)
    return

def lambda_handler(event, context):

    client = boto3.client('sagemaker')
    
    config = parse_config()

    endpoint_names = get_endpoint_names(client, config)
    delete_endpoints(client, endpoint_names)

    notebook_names = get_notebook_names(client, 'InService', config)
    stop_notebook_instances(client, notebook_names)

    return {
        'statusCode': 200,
        'body': json.dumps('Completed lambda function to clean SageMaker resources.')
    }
