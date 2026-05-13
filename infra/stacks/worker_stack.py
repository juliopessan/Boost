from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambda_,
    aws_lambda_event_sources as event_sources,
    aws_sqs as sqs,
    aws_iam as iam,
    aws_ec2 as ec2,
)
from constructs import Construct


class WorkerStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.Vpc,
        messages_queue: sqs.Queue,
        redis_url: str,
        db_secret_arn: str,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        worker_sg = ec2.SecurityGroup(self, "WorkerSG", vpc=vpc, description="Boost Worker Lambda SG")

        self.message_router = lambda_.Function(
            self,
            "MessageRouter",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="workers.message_router.handler",
            code=lambda_.Code.from_asset("../workers"),
            timeout=Duration.seconds(60),
            memory_size=256,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[worker_sg],
            environment={
                "REDIS_URL": redis_url,
            },
        )

        # SQS trigger
        self.message_router.add_event_source(
            event_sources.SqsEventSource(
                messages_queue,
                batch_size=5,
                max_batching_window=Duration.seconds(10),
            )
        )

        # Permissions
        messages_queue.grant_consume_messages(self.message_router)

        self.message_router.add_to_role_policy(
            iam.PolicyStatement(
                actions=["secretsmanager:GetSecretValue"],
                resources=[db_secret_arn],
            )
        )
