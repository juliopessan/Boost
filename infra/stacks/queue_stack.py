from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
)
from constructs import Construct


class QueueStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.dlq = sqs.Queue(
            self,
            "BoostDLQ",
            queue_name="boost-messages-dlq.fifo",
            fifo=True,
            content_based_deduplication=True,
            retention_period=Duration.days(14),
        )

        self.messages_queue = sqs.Queue(
            self,
            "BoostMessagesQueue",
            queue_name="boost-messages.fifo",
            fifo=True,
            content_based_deduplication=True,
            visibility_timeout=Duration.seconds(60),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,
                queue=self.dlq,
            ),
        )
