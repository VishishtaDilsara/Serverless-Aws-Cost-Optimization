import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CostOptimization')
ec2 = boto3.client('ec2')   # ✅ needed for stop/terminate/delete

def lambda_handler(event, context):
    method = event['httpMethod']
    path = event['path']
    print(path)
    headers = {
        "Access-Control-Allow-Origin": "*",   # replace * with frontend domain in prod
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    
    # ✅ Handle CORS preflight
    if method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({"message": "CORS preflight OK"})
        }

    if method == 'GET' and path.endswith("/recommendations"):
        response = table.scan()
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(response['Items'])
        }
    
    elif method == 'POST' and path.endswith("/update-status"):
        body = json.loads(event['body'])
        resource_id = body['ResourceId']
        issue = body['Issue']
        new_status = body['Status']
        
        table.update_item(
            Key={'ResourceId': resource_id, 'Issue': issue},
            UpdateExpression="SET #s = :status",
            ExpressionAttributeNames={'#s': 'Status'},
            ExpressionAttributeValues={':status': new_status}
        )
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'Status updated'})
        }

    elif method == 'POST' and path.endswith("/action"):
        body = json.loads(event['body'])
        resource_id = body['ResourceId']
        issue = body['Issue']
        action = body['Action']   # e.g., stop, terminate, delete
        service = body['Service']

        result = {}
        try:
            if service == "EC2":
                if action == "stop":
                    ec2.stop_instances(InstanceIds=[resource_id])
                    result = {"message": f"Instance {resource_id} stopped"}
                elif action == "terminate":
                    ec2.terminate_instances(InstanceIds=[resource_id])
                    result = {"message": f"Instance {resource_id} terminated"}
            
            elif service == "EBS":
                if issue == "Unattached Volume" and action == "delete":
                    ec2.delete_volume(VolumeId=resource_id)
                    result = {"message": f"Volume {resource_id} deleted"}
                elif issue == "Old Snapshot" and action == "delete":
                    ec2.delete_snapshot(SnapshotId=resource_id)
                    result = {"message": f"Snapshot {resource_id} deleted"}
            
            # ✅ Update DynamoDB
            table.update_item(
                Key={'ResourceId': resource_id, 'Issue': issue},
                UpdateExpression="SET #s = :status",
                ExpressionAttributeNames={'#s': 'Status'},
                ExpressionAttributeValues={':status': f"Closed ({action})"}
            )
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(result)
            }
        
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({"error": str(e)})
            }
    
    else:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'message': 'Unsupported method'})
        }
