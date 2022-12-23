import json
import boto3
import logging

TAG_TO_EXCLUDE = { 'Key': 'env', 'Value': 'prod' }
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# logging.basicConfig(level=logging.DEBUG)

def get_endpoint_names(client):
    logger.info('Getting InService endpoints')
    endpoint_names = []
    endpoints =  client.list_endpoints(
        SortBy = 'CreationTime',
        SortOrder = 'Descending',
        StatusEquals = 'InService',
        MaxResults = 100
    )["Endpoints"]
    for each in endpoints:
        name = each["EndpointName"]
        tags = client.list_tags(ResourceArn = each["EndpointArn"])
        if TAG_TO_EXCLUDE in tags['Tags']:
            logger.info('Ignoring because of tag: %s', name)
            continue
        logger.info('Will delete: %s', name)
        endpoint_names.append(name)
    return endpoint_names
    
def get_notebook_names(client, state):
    logger.info('Getting %s notebooks', state)
    notebook_names = []
    notebooks = client.list_notebook_instances(
        SortBy = 'CreationTime',
        SortOrder = 'Descending',
        StatusEquals = state,
        MaxResults = 100
    )["NotebookInstances"]
    for each in notebooks:
        if each['NotebookInstanceStatus'] == state:
            name = each["NotebookInstanceName"]
            tags = client.list_tags(ResourceArn = each["NotebookInstanceArn"])
            if TAG_TO_EXCLUDE in tags['Tags']:
                logger.info('Ignoring because of tag: %s', name)
                continue
            logger.info('Will delete: %s', name)
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
    logger.info('Deleting notebooks')
    count = 0 
    for name in notebook_names:
        try:
            client.stop_notebook_instance(NotebookInstanceName = name)
            count += 1
        except:
            continue
    logger.info('Deleted %s notebooks', count)
    return

def lambda_handler(event, context):

    client = boto3.client('sagemaker')
    
    logger.info("Excluding resources with the tag %s", TAG_TO_EXCLUDE)
    
    endpoint_names = get_endpoint_names(client)
    
    delete_endpoints(client, endpoint_names)

    notebook_names = get_notebook_names(client, 'InService')

    stop_notebook_instances(client, notebook_names)

    return {
        'statusCode': 200,
        'body': json.dumps('Completed lambda function to clean SageMaker resources.')
    }