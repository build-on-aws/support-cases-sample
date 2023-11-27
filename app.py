import os
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import boto3
import uuid
import json

app = Flask(__name__)

cors = CORS(app, resources={r"/api/*": {"Access-Control-Allow-Origin": "*"}})

# Initialize DynamoDB client
ddb_aws_region = os.getenv('DDB_AWS_REGION', "us-west-2")
ddb_table_name = os.getenv('DDB_TABLE_NAME', "support-cases")

ddb = boto3.resource('dynamodb', region_name=ddb_aws_region)
ddbtable = ddb.Table(ddb_table_name)

def create_case(data=None):
    if data is None:
        # If no data provided, set a default value or return an error
        data = {}
        # Alternatively, handle the error
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'No data provided'}),
            'headers': {'Content-Type': 'application/json'}
        }
    
    # Proceed with creating a case using the provided data

    # Generate a unique case ID
    caseid = str(uuid.uuid4())

    # Put the new item into the DynamoDB table
    ddbtable.put_item(Item={
            'caseid': caseid,
            'title': data['title'],
            'description': data['description'],
            'status': 'open',
            # Add any other fields you need
        })
   
    # Return a successful response
    return {
        "statusCode": 200,
        "body": caseid
        }

@app.route('/')
def home():
    html = "<h1>Welcome to the Support Cases App</h1><p><b>To create a new support case, you can make a post API call <p>/create_case</p> <b>To query the cases, you can call the following API(s):</b><p>/get_case/<caseid></p>"
    return {
        "statusCode": 200,
        "body": html,
        "headers": {
            "Content-Type": "text/html"
        }
    }


@app.route('/create_case', methods=['POST'])  
def api_create_case():
    # Get the JSON data sent with the request
    request_data = request.get_json()

    # Add additional data validation here as needed
    
    # Call create_case with the JSON data
    response = create_case(request_data)
    
    # Return the response from create_case
    return response

@app.route('/get_case/<caseid>', methods=['GET'])
def get_case(caseid):

  # Retrieve the item from the DynamoDB table
  response = ddbtable.get_item(Key={'caseid': caseid})

  if 'Item' not in response:
    return jsonify({'message': 'Case not found.'}), 404

  # Return the item as a JSON object  
  return jsonify(response['Item'])

# Define lambda handler
def lambda_handler(event, context):
    path = event.get('rawPath', '/')
    if path == '/':
        response = home()
    elif path == '/create_case':
        if 'body' in event:
            body = json.loads(event['body'])    
        else:
            # If no body, set data to None or some default value
            body = None

        # Call create_case function
        response=create_case(body)
    elif path == "/get_case":
       caseid = event['pathParameters']['caseid']  
       response = get_case(caseid)
    else:
        return{
                'statusCode': 400,
                'body': json.dumps({'message': 'Invalid path. Unable to process'}),
                'headers': {'Content-Type': 'application/json'}
            }
    
    return response


if __name__ == '__main__':
   app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))
   app.debug =True