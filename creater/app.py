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
    if not ('EndpointConfigName' in endpoint_spec and 'EndpointName' in endpoint_spec):
        logger.error("Environment variable 'ENDPOINT_SPEC' is in the wrong format")
        raise Exception("Environment variable 'ENDPOINT_SPEC' is in the wrong format")

    logger.info("Creating SageMaker Endpoint")
    sm_client = boto3.client('sagemaker')
    response = sm_client.create_endpoint(
        EndpointName=endpoint_spec['EndpointName'],
        EndpointConfigName=endpoint_spec['EndpointConfigName']
    )
    
    # Check the response
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        logger.error("Error creating endpoint: " + str(response))
        raise Exception("Error creating endpoint: " + str(response))
        
    return {
        'statusCode': 200,
        'body': json.dumps('Created SageMaker Endpoint successfully')
    }
