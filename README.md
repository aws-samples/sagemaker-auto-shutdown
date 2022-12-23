# sagemaker-auto-shutdown

This project creates a scheduled job that delete your SageMaker resources (endpoints and notebook instances) to save cost. It is ideal for your development accounts. It will ignore resources with certain tags (default: `env:prod`, configurable).

## Configuration

* Schedule: set the `Resources > DeleteSageMakerResourcesFunction > Events > CloudWatchEvent > Properties > Schedule`. Default: every day at 20:00 UTC.
* Tags to ignore: set the `TAG_TO_EXCLUDE` in `lambda/app.py`. The application will not delete the resources with this tag. Default: `env:prod`
* Log level: change the line `logger.setLevel(logging.INFO)` in `lambda/app.py`. Default: INFO.

## Deploy the application

To use the, you need the following tools:

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* Optional - for local testing
  * [Python 3 installed](https://www.python.org/downloads/)
  * Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

To build and deploy your application for the first time, run the following in your shell:

```bash
sam deploy --guided
```

The command will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

## Tests

Tests are defined in the `tests` folder in this project. Use PIP to install the test dependencies and run tests.

```bash
sagemaker-auto-shutdown$ pip install -r tests/requirements.txt --user
# unit test
sagemaker-auto-shutdown$ python -m pytest tests/unit -v
# integration test, requiring deploying the stack first.
# Create the env variable AWS_SAM_STACK_NAME with the name of the stack we are testing
sagemaker-auto-shutdown$ AWS_SAM_STACK_NAME=<stack-name> python -m pytest tests/integration -v
```

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name sagemaker-auto-shutdown