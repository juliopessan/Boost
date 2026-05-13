from aws_cdk import (
    Stack,
    aws_elasticache as elasticache,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_secretsmanager as sm,
    RemovalPolicy,
    Duration,
)
from constructs import Construct


class StorageStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Security groups
        self.redis_sg = ec2.SecurityGroup(self, "RedisSG", vpc=vpc, description="Boost Redis SG")
        self.rds_sg = ec2.SecurityGroup(self, "RDSSG", vpc=vpc, description="Boost RDS SG")

        # Redis (ElastiCache)
        redis_subnet_group = elasticache.CfnSubnetGroup(
            self,
            "RedisSubnetGroup",
            description="Boost Redis subnet group",
            subnet_ids=[s.subnet_id for s in vpc.private_subnets],
        )

        self.redis_cluster = elasticache.CfnCacheCluster(
            self,
            "BoostRedis",
            cache_node_type="cache.t3.micro",
            engine="redis",
            num_cache_nodes=1,
            cache_subnet_group_name=redis_subnet_group.ref,
            vpc_security_group_ids=[self.redis_sg.security_group_id],
        )

        # RDS PostgreSQL
        self.db_secret = sm.Secret(
            self,
            "DBSecret",
            generate_secret_string=sm.SecretStringGenerator(
                secret_string_template='{"username": "boost"}',
                generate_string_key="password",
                exclude_characters="/@\"",
            ),
        )

        self.db = rds.DatabaseInstance(
            self,
            "BoostDB",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3, ec2.InstanceSize.MICRO
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[self.rds_sg],
            credentials=rds.Credentials.from_secret(self.db_secret),
            database_name="boost",
            removal_policy=RemovalPolicy.SNAPSHOT,
            deletion_protection=True,
            backup_retention=Duration.days(7),
        )
