import gnupg
import boto3
import json

#User Defined Values
QueueName="ProcessFiles"
PGPPrivateKeyLocation='PGPPrivate'
PassphraseLocation='PGPpassphrase'

#Initializing AWS services. Proper roles must be created
sqs = boto3.client('sqs', region_name='us-east-1')
s3 = boto3.client('s3', region_name='us-east-1')
ssm = boto3.client('ssm', region_name='us-east-1')
#Initializing GNUPG. This will create keyring and secret keyring in Lambda Ephemeral storage
gpg = gnupg.GPG(gnupghome='/tmp')

def create_resources():    
    try:
        #Retrieving GPG related stuff from SSM Parameter store. Ideally they should be encrypted
        pvtKey = ssm.get_parameter(Name=PGPPrivateKeyLocation, WithDecryption=False)['Parameter']['Value']
        passphrase = ssm.get_parameter(Name=PassphraseLocation, WithDecryption=False)['Parameter']['Value']

        #Loading key into secret keyring
        gpg.import_keys(key_data=pvtKey,passphrase=passphrase)
        print("Keyring created")

        #SQS Queue for output
        response = sqs.get_queue_url(QueueName=QueueName)
        SQSUrl = response['QueueUrl']
    except Exception as e:
        print("Error creating necessary resources. Failed with error "+e)
        return {
            'statusCode': 500,
            'body': json.dumps("Error creating Keyring. Failed with error "+e)
        }
    return (pvtKey, passphrase, SQSUrl)

def perform_decryption(record,passphrase,SQSUrl):
    try:
        #Get info from event
        bucketName = record['s3']['bucket']['name']
        path2file = record['s3']['object']['key']
        filename=path2file.split('/')[-1]
        tmp_file="/tmp/"+filename
        print("Starting decryption of "+filename+" received at location "+path2file+" in bucket "+bucketName)

        #Download file
        with open(tmp_file, 'wb') as f:
            s3.download_fileobj(bucketName, path2file, f)           
        
        #Decrypt file
        decrypted_data = gpg.decrypt_file(fileobj_or_path=tmp_file, passphrase=passphrase, output=None, always_trust=True)
        print("Decryption of "+filename+"Successful")

        return (decrypted_data,filename) 
    except Exception as e:
        print("Error during decryption. Failed with error "+e)
        return {
            'statusCode': 500,
            'body': json.dumps("Error during decryption. Failed with error "+e)
        }

def handler(event, context):
    pvtKey, passphrase, SQSUrl = create_resources()

    for record in event['Records']:
        decrypted_data, filename =perform_decryption(record,passphrase,SQSUrl)

        #Push to SQS
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