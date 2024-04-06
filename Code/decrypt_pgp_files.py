import gnupg
import boto3
import json

YourQueueName="ProcessFiles"

sqs = boto3.client('sqs', region_name='us-east-1')
s3 = boto3.client('s3', region_name='us-east-1')
ssm = boto3.client('ssm', region_name='us-east-1')
gpg = gnupg.GPG(gnupghome='/tmp')

def handler(event, context):
    try:
        pvtKey = ssm.get_parameter(Name='PGPPrivate', WithDecryption=False)['Parameter']['Value']
        passphrase = ssm.get_parameter(Name='PGPpassphrase', WithDecryption=False)['Parameter']['Value']
        gpg.import_keys(key_data=pvtKey,passphrase=passphrase)
        print("Keyring created")
        response = sqs.get_queue_url(QueueName=YourQueueName)
        SQSUrl = response['QueueUrl']
    except Exception as e:
        print("Error creating keyring")
        print(e)
    
    try:
        for record in event['Records']:
            bucketName = record['s3']['bucket']['name']
            path2file = record['s3']['object']['key']
            filename=path2file.split('/')[-1]
            tmp_file="/tmp/"+filename
            print("Starting decryption of "+filename+" received at location "+path2file+" in bucket "+bucketName)

            with open(tmp_file, 'wb') as f:
                s3.download_fileobj(bucketName, path2file, f)           
            
            decrypted_data = gpg.decrypt_file(fileobj_or_path=tmp_file, passphrase=passphrase, output=None, always_trust=True)
            print("Decryption Successful, pushing to SQS")

            response = sqs.send_message(
            QueueUrl=SQSUrl,
            MessageAttributes={
                    'Filename': {
                        'DataType': 'String',
                        'StringValue': filename[:-4]
                    }                    
                },
                MessageBody=str(decrypted_data)
            )
            print(filename[:-4]+" pushed to SQS with message id "+response['MessageId'])

        return {
            'statusCode': 200,
            'body': json.dumps('Message decrypted and pushed to SQS successfully')
        }

    except Exception as e:
        print(e)