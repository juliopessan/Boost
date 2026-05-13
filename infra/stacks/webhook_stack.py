from aws_cdk import (
    Stack,
    Duration,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ec2 as ec2,
    aws_sqs as sqs,
    aws_secretsmanager as sm,
    aws_certificatemanager as acm,
    aws_route53 as route53,
)
from constructs import Construct


class WebhookStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.Vpc,
        messages_queue: sqs.Queue,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        cluster = ecs.Cluster(self, "BoostCluster", vpc=vpc)

        self.service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "WebhookService",
            cluster=cluster,
            cpu=256,
            memory_limit_mib=512,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset("../webhook"),
                container_port=8000,
                environment={
                    "SQS_QUEUE_URL": messages_queue.queue_url,
                    "AWS_REGION": Stack.of(self).region,
                },
                secrets={},
            ),
            public_load_balancer=True,
            health_check_grace_period=Duration.seconds(60),
        )

        self.service.target_group.configure_health_check(path="/health")

        messages_queue.grant_send_messages(
            self.service.task_definition.task_role
        )
