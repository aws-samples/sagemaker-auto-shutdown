import json
import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

print(logger.level)

def lambda_handler(event, context):
    endpoint_spec = json.loads(os.environ['ENDPOINT_SPEC'])
    logger.info("Endpoint spec: " + str(endpoint_spec))
    if not endpoint_spec:
        logger.error("Environment variable 'ENDPOINT_SPEC' not set")
        raise Exception("Environment variable 'ENDPOINT_SPEC' not set")
    # verify if endpoint_spec is an array
    if not isinstance(endpoint_spec, list):
        logger.error("Environment variable 'ENDPOINT_SPEC' must be an array")
        raise Exception("Environment variable 'ENDPOINT_SPEC' must be an array")
    # check if every element in the array has the required  keys
    for endpoint_spec_element in endpoint_spec:
        if not ('EndpointConfigName' in endpoint_spec_element and 'EndpointName' in endpoint_spec_element):
            logger.error("Environment variable 'ENDPOINT_SPEC' is in the wrong format")
            raise Exception("Environment variable 'ENDPOINT_SPEC' is in the wrong format")

    sm_client = boto3.client('sagemaker')
    anyFailed = False
    for endpoint_spec_element in endpoint_spec:
        logger.info("Creating SageMaker Endpoint: " + endpoint_spec_element['EndpointName'])
        response = sm_client.create_endpoint(
            EndpointName=endpoint_spec_element['EndpointName'],
            EndpointConfigName=endpoint_spec_element['EndpointConfigName']
        )
    
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            logger.error("Error creating endpoint: " + str(response))
            anyFailed = True
            # continue with the other endpoint creation
            
    if anyFailed:
        raise Exception("Error creating endpoint")
        
    return {
        'statusCode': 200,
        'body': json.dumps('Created SageMaker Endpoint successfully')
    }
