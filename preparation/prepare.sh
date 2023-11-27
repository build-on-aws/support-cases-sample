#!/bin/bash

export TABLE_NAME="support-cases"
export IAM_ROLE="support-cases-role"
export ACCOUNT_ID=$(aws sts get-caller-identity --output text --query 'Account') 
export AWS_REGION=$(aws configure get region)
if [ -z ${AWS_REGION} ]; then echo "you need to export the AWS_REGION variable"; exit; fi

aws dynamodb create-table \
    --table-name $TABLE_NAME \
    --attribute-definitions AttributeName=caseid,AttributeType=S \
    --key-schema AttributeName=caseid,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region $AWS_REGION 

echo "waiting a few seconds for the table to be available"
sleep 10 

aws dynamodb put-item \
    --table-name $TABLE_NAME \
    --item '{
        "caseid": {"S": "a375a138-0eef-43db-9756-1872a426f04a"},
        "title": {"S": "Issue with Account"},
        "description": {"S": "I cannot access my account. It says user does not exist."},
        "status": {"S": "Open"}
    }' \
    --region $AWS_REGION 


aws iam create-role --role-name $IAM_ROLE --assume-role-policy-document file://apprunner-trust-policy.json
sed -e "s@ACCOUNT_ID@$ACCOUNT_ID@g" -e "s@AWS_REGION@$AWS_REGION@g" -e "s@TABLE_NAME@$TABLE_NAME@g" ddb-policy.json > filled-ddb-policy.json
aws iam create-policy --policy-name ddb-policy --policy-document file://./filled-ddb-policy.json
rm  filled-ddb-policy.json
aws iam attach-role-policy --role-name $IAM_ROLE --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/ddb-policy
aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess --role-name $IAM_ROLE
