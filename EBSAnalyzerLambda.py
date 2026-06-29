import boto3
import datetime

ec2 = boto3.client('ec2')
cloudwatch = boto3.client('cloudwatch')
dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('CostOptimization')

def lambda_handler(event, context):
    now = datetime.datetime.utcnow()
    cutoff_days = 1
    cutoff_date = now - datetime.timedelta(days=cutoff_days)

    # --- Part 1: EBS Volumes ---
    volumes = ec2.describe_volumes(Filters=[])
    for vol in volumes['Volumes']:
        vol_id = vol['VolumeId']
        state = vol['State']
        size = vol['Size']  # GB
        vol_type = vol['VolumeType']

        # 1️⃣ Unattached Volumes
        if state == 'available':
            table.put_item(Item={
                'ResourceId': vol_id,
                'Service': 'EBS',
                'Issue': 'Unattached Volume',
                'Recommendation': 'Delete if not needed',
                'EstimatedSavings': f"{size} GB storage/month",
                'Status': 'Open'
            })

        # 2️⃣ gp2 Check
        if vol_type == 'gp2':
            table.put_item(Item={
                'ResourceId': vol_id,
                'Service': 'EBS',
                'Issue': 'gp2 Volume',
                'Recommendation': 'Migrate to gp3',
                'EstimatedSavings': 'Up to 20% lower cost',
                'Status': 'Open'
            })

        # 3️⃣ Overprovisioned Volume Check (using CloudWatch Agent metrics)
        try:
            metrics = cloudwatch.get_metric_statistics(
                Namespace='CWAgent',
                MetricName='disk_used_percent',
                Dimensions=[{'Name': 'InstanceId', 'Value': vol['Attachments'][0]['InstanceId']}],
                StartTime=now - datetime.timedelta(days=7),
                EndTime=now,
                Period=86400,
                Statistics=['Average']
            )

            if metrics['Datapoints']:
                avg_used_percent = metrics['Datapoints'][0]['Average']
                if avg_used_percent < 30:  # e.g. using less than 30% of volume
                    table.put_item(Item={
                        'ResourceId': vol_id,
                        'Service': 'EBS',
                        'Issue': 'Overprovisioned Volume',
                        'Recommendation': 'Consider reducing volume size',
                        'EstimatedSavings': f"Currently using only {avg_used_percent:.1f}% of {size} GB",
                        'Status': 'Open'
                    })
        except Exception as e:
            print(f"No usage metrics for volume {vol_id}: {str(e)}")

    # --- Part 2: Old Snapshots ---
    snapshots = ec2.describe_snapshots(OwnerIds=['self'])
    for snap in snapshots['Snapshots']:
        snap_id = snap['SnapshotId']
        start_time = snap['StartTime'].replace(tzinfo=None)

        if start_time < cutoff_date:
            size = snap['VolumeSize']
            table.put_item(Item={
                'ResourceId': snap_id,
                'Service': 'EBS',
                'Issue': 'Old Snapshot',
                'Recommendation': f'Review/Delete snapshot older than {cutoff_days} days',
                'EstimatedSavings': f"{size} GB storage/month",
                'Status': 'Open'
            })

    return {"status": "done"}
