import boto3
import logging
import os
import time
from botocore.exceptions import ClientError, NoCredentialsError

def upload_file_to_s3(file_path, bucket, object_name=None):
    """
    Upload a file to an S3 bucket.

    :param file_path: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_path)

    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_path, bucket, object_name)
    except ClientError as e:
        logging.error(f"S3 Upload Failed: {e}")
        return False
    except NoCredentialsError:
        logging.error("S3 Upload Failed: No AWS credentials found")
        return False
    return True

class CloudWatchLogHandler(logging.Handler):
    """
    Custom logging handler to send logs to AWS CloudWatch Logs.
    """
    def __init__(self, log_group, log_stream_name):
        super().__init__()
        self.log_group = log_group
        self.log_stream_name = log_stream_name
        self.client = boto3.client('logs')
        self.sequence_token = None
        
        # Ensure log group and stream exist
        self._initialize_log_group_stream()

    def _initialize_log_group_stream(self):
        try:
            self.client.create_log_group(logGroupName=self.log_group)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass
        except Exception as e:
            print(f"Failed to create log group: {e}")

        try:
            self.client.create_log_stream(logGroupName=self.log_group, logStreamName=self.log_stream_name)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass
        except Exception as e:
            print(f"Failed to create log stream: {e}")

    def emit(self, record):
        try:
            msg = self.format(record)
            timestamp = int(round(time.time() * 1000))

            event = {
                'timestamp': timestamp,
                'message': msg
            }

            kwargs = {
                'logGroupName': self.log_group,
                'logStreamName': self.log_stream_name,
                'logEvents': [event]
            }

            if self.sequence_token:
                kwargs['sequenceToken'] = self.sequence_token

            response = self.client.put_log_events(**kwargs)
            self.sequence_token = response.get('nextSequenceToken')

        except Exception:
            self.handleError(record)
