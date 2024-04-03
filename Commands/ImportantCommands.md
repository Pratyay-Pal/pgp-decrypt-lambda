To build image for lambda-
docker build --platform linux/amd64 -t "image_name":"tag" .

Login to ECR-
aws ecr get-login-password --region "region" | docker login --username AWS --password-stdin "account_id".dkr.ecr."region".amazonaws.com

Retag Image-
docker tag "image_name":"tag" "account_id".dkr.ecr."region".amazonaws.com/"image_name":"tag"