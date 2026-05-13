#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2

from stacks.queue_stack import QueueStack
from stacks.storage_stack import StorageStack
from stacks.webhook_stack import WebhookStack
from stacks.worker_stack import WorkerStack

app = cdk.App()

env = cdk.Environment(
    account=app.node.try_get_context("account"),
    region=app.node.try_get_context("region") or "us-east-1",
)

# Shared VPC
vpc_stack = cdk.Stack(app, "BoostVPC", env=env)
vpc = ec2.Vpc(vpc_stack, "VPC", max_azs=2, nat_gateways=1)

# Queues
queue_stack = QueueStack(app, "BoostQueues", env=env)

# Storage (Redis + RDS)
storage_stack = StorageStack(app, "BoostStorage", vpc=vpc, env=env)
storage_stack.add_dependency(vpc_stack)

# Webhook (ECS Fargate)
webhook_stack = WebhookStack(
    app,
    "BoostWebhook",
    vpc=vpc,
    messages_queue=queue_stack.messages_queue,
    env=env,
)
webhook_stack.add_dependency(queue_stack)
webhook_stack.add_dependency(vpc_stack)

# Workers (Lambda)
redis_endpoint = storage_stack.redis_cluster.attr_redis_endpoint_address
worker_stack = WorkerStack(
    app,
    "BoostWorkers",
    vpc=vpc,
    messages_queue=queue_stack.messages_queue,
    redis_url=f"redis://{redis_endpoint}:6379",
    db_secret_arn=storage_stack.db_secret.secret_arn,
    env=env,
)
worker_stack.add_dependency(queue_stack)
worker_stack.add_dependency(storage_stack)
worker_stack.add_dependency(vpc_stack)

app.synth()
