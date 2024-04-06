# pgp-decrypt-lambda

Decryption of PGP encrypted files using Lambda Containers.

Resources-
1. S3 Bucket
2. S3 Bucket Trigger to trigger Lambda
3. Secret Key in SSM Parameter Store
4. Passphrase in SSM Parameter Store
5. SQS Queue to receive decrypted files
6. Lambda of Container Type
7. ECR to store images for Lambda

Procedure to use the code is present in Commands/Procedure.md