import json

def lambda_handler(event, context):
    # 1. Parse the incoming order data
    # If using a Function URL, the body is usually in event['body']
    try:
        body = json.loads(event.get('body', '{}'))
        order_id = body.get('order_id', 'Unknown')
        message = body.get('msg', 'No message provided')
        
        print(f"RECEIVED EVENT: Order #{order_id} - {message}")
        
        # 2. Return a success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'Success',
                'processed_order': order_id
            })
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }