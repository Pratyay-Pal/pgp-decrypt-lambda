1. Create python script and docker file
2. Place files in a server
3. Install and start docker service
4. Create the image
5. Retag the image with correct URI
6. Login and push the image to ECR
7. Create Secret Key, Passphrase entry in Parameter Store, SQS, S3 bucket, S3 bucket trigger
7. Create Lambda of container type and choose image to deploy
8. Wait for Lambda to start
9. Run test event and hope it succeeds