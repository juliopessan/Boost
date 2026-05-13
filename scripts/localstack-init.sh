#!/bin/bash
# Cria as filas SQS no LocalStack para desenvolvimento local
awslocal sqs create-queue \
  --queue-name boost-messages-dlq.fifo \
  --attributes FifoQueue=true,ContentBasedDeduplication=true

awslocal sqs create-queue \
  --queue-name boost-messages.fifo \
  --attributes FifoQueue=true,ContentBasedDeduplication=true,RedrivePolicy='{"deadLetterTargetArn":"arn:aws:sqs:us-east-1:000000000000:boost-messages-dlq.fifo","maxReceiveCount":"3"}'

echo "SQS queues created."
