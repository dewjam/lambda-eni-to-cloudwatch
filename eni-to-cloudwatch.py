from collections import defaultdict
import boto3

# Checks if the ENI is attached to a Lambda Function
def is_attached_to_lambda(eni):
    if 'Attachment' in eni and 'InstanceOwnerId' in eni['Attachment']:
        if eni['Attachment']['InstanceOwnerId'] == 'aws-lambda':
            return True
    return False

# Groups ENIs by function name and subnetId and returns a list of metrics that can be sent to cloudwatch
def get_metric_data(enis):
    metric_data = []
    lambda_count = defaultdict(dict)
    for eni in enis:
        if is_attached_to_lambda(eni):
            if eni['SubnetId'] not in lambda_count[eni['RequesterId']]:
                lambda_count[eni['RequesterId']][eni['SubnetId']] = 0
            lambda_count[eni['RequesterId']][eni['SubnetId']] += 1
    for function, subnets in lambda_count.items():
        for subnet in subnets:
            metric_data.append(
                {
                    'MetricName': 'ENI-Usage',
                    'Dimensions': [
                        {
                            'Name': 'SubnetID',
                            'Value': subnet
                        },
                        {
                            'Name': 'FunctionName',
                            'Value': function.split(":")[1]
                        }
                    ],
                    'Value': lambda_count[function][subnet],
                    'Unit': 'Count',
                    'StorageResolution': 60
                })
    return metric_data

# Puts metric data to cloudwatch under IPUsage namespace
def put_metrics_to_cloudwatch(metric_data):
    cloudwatch_client = boto3.client('cloudwatch')
    cloudwatch_client.put_metric_data(Namespace='Lambda-Custom', MetricData=metric_data)

# Entrypoint for the function
def lambda_handler(event, context):
    ec2_client = boto3.client('ec2')
    enis = ec2_client.describe_network_interfaces()['NetworkInterfaces']
    metric_data = get_metric_data(enis)
    if metric_data != []:
        put_metrics_to_cloudwatch(metric_data)
