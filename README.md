## lambda-eni-to-cloudwatch
The purpose of this repo is to provide a method to track the number of ENIs that are in use by Lambda functions which are configured with access to a VPC. Once ENI information is collected it's pushed CloudWatch as a metric so that IP Usage can be trended over time.  This is particularly useful if you are having issues with IP space exhaustion in some of your AWS subnets and believe it's related to the use of ENIs by your Lambda functions.

---

### eni-cloudtrail-to-cloudwatch.py
#### Description:
This function will analyze CloudTrail Events and find events with type `CreateNetworkInterface` that were created over the last hour.  It will identify events which were created by Lambda functions and push a metric to CloudWatch to indicate how many ENIs were created.  This function is intended to run hourly via scheduled CloudWatch events.

*Namespace: Lambda-Custom*  
*Metric Name: ENI-Create-Events*  
*Dimensions:  FunctionName, SubnetId*

#### Requirements:
A standard Lambda Execution role that has permissions to read CloudTrail Events and write to CloudWatch Metrics.

**Permissions:**

| Service       | Access level         | Resource      |
| ------------- |:---------------------| :-------------|
| CloudWatch    | Write(PutMetricData) | All resources |
| CloudTrail    | List, Read           | All resources |

##### Caveats:
This function will not provide you with metrics about current Lambda ENI usage.  Only new ENIs will show up in the CloudWatch metric.  

---

### eni-to-cloudwatch.py
#### Description:
This function calls the EC2 API and looks for ENI resources that were created by Lambda.  Then a metric is pushed to CloudWatch which shows current ENI usage.  This function is intended to run via scheduled CloudWatch events (recommend running at least hourly).  Running the function more frequently will result in more granular metrics, but also could incur additional costs.

*Namespace: Lambda-Custom*  
*Metric Name: ENI-Usage*  
*Dimensions:  FunctionName, SubnetId*

#### Requirements:
A standard Lambda Execution role that has permissions to describe network interfaces from the EC2 API and write to CloudWatch Metrics.

**Permissions:**

| Service       | Access level                   | Resource      |
| ------------- |:------------------------------ | :-------------|
| CloudWatch    | Write:PutMetricData            | All resources |
| EC2           | List:DescribeNetworkInterfaces | All resources |


##### Caveats:
This function will provide you with metrics about current Lambda ENI usage only.  The CloudWatch metric will not reflect ENIs which were created and removed between executions of the function.  Additionally, there are times when ENIs are created by one function, but re-used by another if the same ENI attributes are required (the same subnet, security group, etc).  In these cases, the `FunctionName` dimension will remain that of the function which originally requested that the ENI be created.
