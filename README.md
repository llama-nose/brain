# Llama Nose Brain Core

contact: edwinpan@cs.stanford.edu, joyangseph@gmail.com

## Installation
0. Setup conda environment
```bash
conda create -n lln-brain python=3.11
conda activate lln-brain
pip install -e .
```

### Setup AWS ECR and Lambda
1. Create a new ECR repository. This is a one-time setup. Make sure to verify the region and repository name. 
```bash
aws ecr create-repository --repository-name lln-brain --profile lln-profile --region us-east-2 --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
```

2. Create an execution role for the Lambda function. 
This is a one-time setup. Make sure to verify the region and role name.
```bash
aws iam create-role --role-name lln-ml-ex --profile lln-profile --assume-role-policy-document file://policies/trust-policy.json
```

3. Attach the AWSLambdaBasicExecutionRole policy to the role
This is a one-time setup. Make sure to verify the role name.
```bash
aws iam attach-role-policy --role-name lln-ml-ex --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole --profile lln-profile
```
```bash
aws iam put-role-policy --role-name lln-ml-ex --policy-name dmInvokePolicy --policy-document file://policies/dm-policy.json
```

### Build and push the Docker image to ECR
4. Build the Docker image. Make sure to verify the Guardrails token.
```bash
docker build \
  --build-arg GUARDRAILS_TOKEN=$(echo $GUARDRAILS_TOKEN) \
  --platform linux/amd64 \
  -t lln-brain:test .
```

5. Login to AWS ECR. We are in the `us-east-2` region. `158267493868` is the account number.
```bash
aws ecr get-login-password --region us-east-2 --profile lln-profile | docker login --username AWS --password-stdin 158267493868.dkr.ecr.us-east-2.amazonaws.com
```

6. Tag the Docker image
```bash
docker tag lln-brain:test 158267493868.dkr.ecr.us-east-2.amazonaws.com/lln-brain:latest
```

7. Push the Docker image to AWS ECR. Note that the image name is `lln-brain` and the tag is `latest`.
```bash
docker push 158267493868.dkr.ecr.us-east-2.amazonaws.com/lln-brain:latest
```

### Setup the Lambda Function
1. Create a new Lambda function.
This is a one-time setup. Make sure to verify the region, role, and function name.
```bash
``` bash
aws lambda create-function \
  --function-name llnBrainLambda \
  --profile lln-profile \
  --package-type Image \
  --code ImageUri=158267493868.dkr.ecr.us-east-2.amazonaws.com/lln-brain:latest \
  --role arn:aws:iam::158267493868:role/lln-ml-ex
```

2. Update the Lambda function.
This is a one-time setup. Make sure to verify the region, role, and function name.
```bash
aws lambda update-function-configuration \
  --function-name llnBrainLambda \
  --profile lln-profile \
  --timeout 120
```

### Manual Deployment
1. Run the update_lambda.sh script to update the Lambda function with the new Docker image. See UPDATE.md for more details.
```bash
./scripts/update_lambda.sh
```