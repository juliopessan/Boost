import json
import boto3
import structlog
from botocore.exceptions import ClientError

log = structlog.get_logger()


class SQSService:
    def __init__(self, queue_url: str, region: str = "us-east-1"):
        self.queue_url = queue_url
        self.client = boto3.client("sqs", region_name=region)

    def publish(self, envelope: dict, deduplication_id: str) -> str:
        try:
            response = self.client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(envelope),
                MessageGroupId="whatsapp-messages",
                MessageDeduplicationId=deduplication_id,
            )
            message_id = response["MessageId"]
            log.info("sqs.published", message_id=message_id, dedup_id=deduplication_id)
            return message_id
        except ClientError as e:
            log.error("sqs.publish_failed", error=str(e), dedup_id=deduplication_id)
            raise
