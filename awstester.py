import boto3, traceback, json
from botocore.exceptions import ClientError
from sflogger import sfLogger


class awsTester:
    def __init__(self, pkgid, accesskey, secretkey, stoken, awsservice, region):
        self.pkgid = pkgid
        self.accesskey = accesskey
        self.secretkey = secretkey
        self.stoken = stoken
        self.awsservice = awsservice
        self.region = region

    def s3_check(self, bucket, command):
        s3 = boto3.resource('s3')
        s3bucket = s3.Bucket(bucket)
        if command == 'ls':
            try:
                if (s3bucket.objects):
                    print ("This is vulnerable")
                    
            except ClientError as e:
                print (e)

    def kinesis_check(self, bucket, command):
        kinesis = boto3.resource('kinesis')
        if command == 'list_streams':
            try:
                if kinesis.list_streams() :
                    print ("This is vulnerable")

            except ClientError as e:
                print (e)
