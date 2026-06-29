import boto3
import datetime

cloudwatch = boto3.client('cloudwatch')
ec2 = boto3.client('ec2')
dynamodb = boto3.resource('dynamodb')
compute_optimizer = boto3.client('compute-optimizer')

table = dynamodb.Table('CostOptimization')

def lambda_handler(event, context):
    # --- Part 1: Idle Instance Check ---
    instances = ec2.describe_instances(Filters=[
        {'Name': 'instance-state-name', 'Values': ['running']}
    ])

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            
            # Get CPU utilization (last 7 days)
            end_time = datetime.datetime.utcnow()
            start_time = end_time - datetime.timedelta(days=7)
            
            metrics = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,  # daily
                Statistics=['Average']
            )
            
            if metrics['Datapoints']:
                avg_cpu = sum(dp['Average'] for dp in metrics['Datapoints']) / len(metrics['Datapoints'])
            else:
                avg_cpu = 0
            
            # Idle check
            if avg_cpu < 5:
                table.put_item(Item={
                    'ResourceId': instance_id,
                    'Service': 'EC2',
                    'Issue': 'Idle Instance',
                    'Recommendation': 'Stop or Terminate',
                    'EstimatedSavings': 'Manual Estimate',
                    'Status': 'Open'
                })
    
    # --- Part 2: Compute Optimizer Recommendations ---
    recommendations = compute_optimizer.get_ec2_instance_recommendations()
    
    for rec in recommendations['instanceRecommendations']:
        instance_id = rec['instanceArn'].split("/")[-1]
        finding = rec['finding']  # e.g. "Overprovisioned"
        
        if finding == "Overprovisioned":
            # Pick first recommended option
            if rec['recommendationOptions']:
                option = rec['recommendationOptions'][0]
                rec_type = option['instanceType']
                savings = option.get('performanceRisk', 'N/A')  # AWS doesn't give exact cost saving
                
                table.put_item(Item={
                    'ResourceId': instance_id,
                    'Service': 'EC2',
                    'Issue': 'Overprovisioned',
                    'Recommendation': f'Right-size to {rec_type}',
                    'EstimatedSavings': f"Potential savings (risk {savings})",
                    'Status': 'Open'
                })
    
    return {"status": "done"}
