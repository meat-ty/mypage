#!/usr/bin/python

# import module
import boto3
import sys
import argparse
import datetime

# set comment
comment = """
Displays the resource usage status of the RDS instance.
"-i", "-m" option is a required option.
"""

# initialize
parser = argparse.ArgumentParser(
            description=comment,
            formatter_class=argparse.RawTextHelpFormatter
            )

# option setting
parser.add_argument(
    '-i',
    '--identifer',
    help='Specify the DBInstanceIdentifier of the target RDS instance.',
    metavar='<Identifier>',
    required=True
    )

parser.add_argument(
    '-m',
    '--metrics',
    help='Specify metrics for acquiring resource information.',
    metavar='<Metrics>',
    required=True
    )

parser.add_argument(
    '-r',
    '--region',
    help='Specify the Region the RDS instance residing.',
    metavar='<Region>',
    )

# set argument
argument = parser.parse_args()

# set default region
if(argument.region is None):
    argument.region = 'ap-northeast-1'

# set AWS service & region
conn = boto3.client('cloudwatch', region_name=argument.region)

# Metrics setting
metrics = {
    "CPUUtilization": {"type": "float", "value": None},
    "ReadLatency": {"type": "float", "value": None},
    "DatabaseConnections": {"type": "int", "value": None},
    "FreeableMemory": {"type": "float", "value": None},
    "ReadIOPS": {"type": "int", "value": None},
    "WriteLatency": {"type": "float", "value": None},
    "WriteThroughput": {"type": "float", "value": None},
    "WriteIOPS": {"type": "int", "value": None},
    "SwapUsage": {"type": "float", "value": None},
    "ReadThroughput": {"type": "float", "value": None},
    "DiskQueueDepth": {"type": "float", "value": None},
    "NetworkReceiveThroughput": {"type": "float", "value": None},
    "NetworkTransmitThroughput": {"type": "float", "value": None},
    "FreeStorageSpace": {"type": "float", "value": None}
}

# Time setting
end = datetime.datetime.utcnow()
start = end - datetime.timedelta(minutes=5)

for k, vh in metrics.items():
    if(k == argument.metrics):
        try:
            res = conn.get_metric_statistics(
                Namespace="AWS/RDS",
                MetricName=k,
                Dimensions=[
                    {
                        'Name': "DBInstanceIdentifier",
                        'Value': argument.identifer
                    }
                ],
                StartTime=start,
                EndTime=end,
                Period=60,
                Statistics=["Average"]
            )
        except Exception as err:
                print("status err Error running rds_stats: {0}".format(err))
                sys.exit(1)

        average = res.get('Datapoints')[-1].get('Average')

        # bytes -> Gbytes
        if (k == "FreeStorageSpace" or k == "FreeableMemory"):
                average = average / 1024.0**3.0

        # fourth decimal place
        if vh["type"] == "float":
                metrics[k]["value"] = "%.4f" % average

        if vh["type"] == "int":
                metrics[k]["value"] = "%i" % average

        print(vh["value"])
        break
