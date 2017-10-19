#!/usr/bin/python

# import modules
import boto3
import datetime

# set AWS service & region
ec2 = boto3.client('ec2', 'ap-northeast-1')

# Set number of generations
num = 2


# lambda handler
def lambda_handler(event, context):
    create_snapshots()
    delete_snapshots()


# create snapshots
def create_snapshots():
    snap_inst = get_target_instances()
    description = "create snapshot %s" % datetime.datetime.today()

    for reservation in snap_inst['Reservations']:
        for instance in reservation['Instances']:
            for device in instance['BlockDeviceMappings']:
                volid = device['Ebs']['VolumeId']
                ebs_tag = get_tags(volid)
                print(ebs_tag['Tags'][0]['Value'], 'create snapshot start')
                snap_info = ec2.create_snapshot(
                                VolumeId=volid,
                                Description=description
                            )
                create_tags(snap_info, ebs_tag)
                print(ebs_tag['Tags'][0]['Value'], 'create snapshot end')


# delete snapshots
def delete_snapshots():
    old_snap = datetime.datetime.today() - datetime.timedelta(days=num)
    snap_list = get_snapshot_list()

    for snapshots in snap_list['Snapshots']:
        if snapshots['StartTime'].isoformat() < old_snap.isoformat():
            print(snapshots['SnapshotId'], 'delete snapshot start')
            ec2.delete_snapshot(SnapshotId=snapshots['SnapshotId'])
            print(snapshots['SnapshotId'], 'delete snapshot end')


# get snapshot target instances
def get_target_instances():
    return ec2.describe_instances(Filters=[{'Name': 'tag:auto-snapshot',
                                            'Values': ['yes']}])


# get EBS tags
def get_tags(volid):
    return ec2.describe_tags(Filters=[{'Name': 'resource-id',
                                       'Values': [volid]}])


# create snapshot tags
def create_tags(snap_info, ebs_tag):
    ec2.create_tags(
        Resources=[snap_info['SnapshotId']],
        Tags=[{'Key': 'Name', 'Value': ebs_tag['Tags'][0]['Value']},
              {'Key': 'auto-snapshot', 'Value': 'yes'}]
    )


# get snapshot list
def get_snapshot_list():
    return ec2.describe_snapshots(Filters=[{'Name': 'tag:auto-snapshot',
                                            'Values': ['yes']}])
