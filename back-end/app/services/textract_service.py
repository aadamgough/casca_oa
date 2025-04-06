import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
import asyncio
import time
import uuid

load_dotenv()

class TextractService:
    def __init__(self):
        self.textract = boto3.client(
            'textract',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('AWS_S3_BUCKET')

    async def start_document_analysis(self, file_path):
        """Start async Textract job using S3"""
        try:
            # Upload to S3 first
            file_name = f"uploads/{str(uuid.uuid4())}.pdf"
            with open(file_path, 'rb') as file:
                self.s3.upload_fileobj(file, self.bucket_name, file_name)

            # debug for file upload test
            head = self.s3.head_object(Bucket=self.bucket_name, Key=file_name)
            print(f"File uploaded. Content-Length: {head['ContentLength']}")
            print(f"Uploaded to: s3://{self.bucket_name}/{file_name}")
            
            # Start Textract job
            response = self.textract.start_document_analysis(
                DocumentLocation={
                    'S3Object': {
                        'Bucket': self.bucket_name,
                        'Name': file_name
                    }
                },
                FeatureTypes=['TABLES']
            )
            
            return response['JobId'], file_name
            
        except ClientError as e:
            print(f"Error starting Textract job: {e}")
            raise Exception(f"Failed to start document analysis: {str(e)}")

    async def get_document_analysis(self, job_id):
        """Get results of async Textract job"""
        try:
            max_retries = 30  # Maximum number of retries
            retry_count = 0
            
            while retry_count < max_retries:
                response = self.textract.get_document_analysis(JobId=job_id)
                status = response['JobStatus']
                
                if status == 'SUCCEEDED':
                    # Collect all pages
                    pages = []
                    pages.extend(response['Blocks'])
                    
                    next_token = response.get('NextToken')
                    while next_token:
                        response = self.textract.get_document_analysis(
                            JobId=job_id,
                            NextToken=next_token
                        )
                        pages.extend(response['Blocks'])
                        next_token = response.get('NextToken')
                    
                    return pages
                
                elif status == 'FAILED':
                    raise Exception(f"Textract analysis failed: {response.get('StatusMessage', 'Unknown error')}")
                
                retry_count += 1
                await asyncio.sleep(2)  # Wait 2 seconds between checks
            
            raise Exception("Textract analysis timed out")
            
        except ClientError as e:
            print(f"Error getting Textract results: {e}")
            raise Exception(f"Failed to get analysis results: {str(e)}")