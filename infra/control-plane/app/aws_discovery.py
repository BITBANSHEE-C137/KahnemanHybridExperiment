"""Multi-project AWS resource discovery with TTL caching.

Provides cached, read-only access to AWS resources across multiple
projects. Resources are classified by tags, naming conventions, and
a hardcoded project registry.
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger("control-plane.discovery")


@dataclass
class ProjectConfig:
    """Configuration for project resource classification."""

    name: str
    display_name: str
    tag_filters: dict[str, str] = field(default_factory=dict)
    s3_prefixes: list[str] = field(default_factory=list)
    lambda_prefixes: list[str] = field(default_factory=list)
    fleet_ids: list[str] = field(default_factory=list)
    route53_zone_ids: list[str] = field(default_factory=list)
    cloudfront_patterns: list[str] = field(default_factory=list)


PROJECTS: dict[str, ProjectConfig] = {
    "ml-lab": ProjectConfig(
        name="ml-lab",
        display_name="ML Lab",
        tag_filters={"Project": "ml-lab"},
        s3_prefixes=["ml-lab"],
        fleet_ids=["fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a"],
        route53_zone_ids=["Z03629483MIHQSCG59T8J"],
    ),
    "deadcatsociety": ProjectConfig(
        name="deadcatsociety",
        display_name="Dead Cat Society",
        tag_filters={"Project": "deadcatsociety"},
        s3_prefixes=["deadcatsociety", "dcs-"],
        lambda_prefixes=["deadcatsociety", "dcs-", "DeadCat"],
        cloudfront_patterns=["deadcat", "dcs"],
    ),
    "bitbanshee": ProjectConfig(
        name="bitbanshee",
        display_name="Bitbanshee",
        tag_filters={"Project": "bitbanshee"},
        s3_prefixes=["bitbanshee"],
        cloudfront_patterns=["bitbanshee"],
        route53_zone_ids=["Z03629483MIHQSCG59T8J"],
    ),
}


@dataclass
class _CacheEntry:
    data: Any
    expires_at: float


class AWSDiscovery:
    """Cached multi-project AWS resource discovery engine."""

    TTL_EC2 = 60
    TTL_LAMBDA = 300
    TTL_S3 = 300
    TTL_CLOUDFRONT = 300
    TTL_ROUTE53 = 300
    TTL_COST = 3600

    def __init__(self) -> None:
        """Initializes boto3 clients and the TTL cache."""
        self._ec2 = boto3.client("ec2")
        self._lambda_client = boto3.client("lambda")
        self._s3 = boto3.client("s3")
        self._cloudfront = boto3.client("cloudfront")
        self._route53 = boto3.client("route53")
        self._cloudwatch = boto3.client("cloudwatch")
        self._cache: dict[str, _CacheEntry] = {}

    def _cached(self, key: str, ttl: float, fetcher: Callable[[], Any]) -> Any:
        """Return cached data or call fetcher and cache the result."""
        entry = self._cache.get(key)
        if entry and time.time() < entry.expires_at:
            return entry.data
        data = fetcher()
        self._cache[key] = _CacheEntry(data=data, expires_at=time.time() + ttl)
        return data

    def _classify_by_tags(self, tags: dict[str, str]) -> Optional[str]:
        """Check tags against all project tag filters."""
        for proj_name, proj in PROJECTS.items():
            for tag_key, tag_val in proj.tag_filters.items():
                if tags.get(tag_key, "").lower() == tag_val.lower():
                    return proj_name
        return None

    def _classify_bucket(self, name: str, tags: dict[str, str]) -> str:
        """Classify an S3 bucket to a project by tags then name prefix."""
        by_tag = self._classify_by_tags(tags)
        if by_tag:
            return by_tag
        name_lower = name.lower()
        for proj_name, proj in PROJECTS.items():
            for prefix in proj.s3_prefixes:
                if name_lower.startswith(prefix.lower()):
                    return proj_name
        return "other"

    def _classify_lambda(self, name: str, tags: dict[str, str]) -> str:
        """Classify a Lambda function to a project by tags then name prefix."""
        by_tag = self._classify_by_tags(tags)
        if by_tag:
            return by_tag
        name_lower = name.lower()
        for proj_name, proj in PROJECTS.items():
            for prefix in proj.lambda_prefixes:
                if name_lower.startswith(prefix.lower()):
                    return proj_name
        return "other"

    def _classify_distribution(self, dist: dict[str, Any]) -> str:
        """Classify a CloudFront distribution by comment and aliases."""
        comment = (dist.get("Comment") or "").lower()
        aliases = dist.get("Aliases", {}).get("Items", []) or []
        combined = comment + " " + " ".join(a.lower() for a in aliases)
        for proj_name, proj in PROJECTS.items():
            for pattern in proj.cloudfront_patterns:
                if pattern.lower() in combined:
                    return proj_name
        return "other"

    def get_ec2_instances(self, project: Optional[str] = None) -> list[dict[str, Any]]:
        """Get EC2 instances, optionally filtered by project.

        Args:
            project: Filter to this project name, or None/\"all\" for all.

        Returns:
            List of instance dicts with project classification.
        """
        def fetch() -> list[dict[str, Any]]:
            try:
                instances: list[dict[str, Any]] = []
                paginator = self._ec2.get_paginator("describe_instances")
                filters = [{"Name": "instance-state-name",
                            "Values": ["pending", "running", "stopping", "stopped"]}]
                for page in paginator.paginate(Filters=filters):
                    for res in page.get("Reservations", []):
                        for inst in res.get("Instances", []):
                            tags = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
                            inst_project = self._classify_by_tags(tags) or "other"
                            launch_time = inst.get("LaunchTime")
                            if isinstance(launch_time, datetime):
                                launch_time = launch_time.isoformat()
                            instances.append({
                                "instance_id": inst.get("InstanceId"),
                                "instance_type": inst.get("InstanceType"),
                                "state": inst.get("State", {}).get("Name"),
                                "az": inst.get("Placement", {}).get("AvailabilityZone"),
                                "public_ip": inst.get("PublicIpAddress"),
                                "private_ip": inst.get("PrivateIpAddress"),
                                "launch_time": launch_time,
                                "name": tags.get("Name", ""),
                                "project": inst_project,
                            })
                return instances
            except ClientError as e:
                logger.error("EC2 describe_instances failed: %s", e)
                return []

        all_instances = self._cached("ec2_instances", self.TTL_EC2, fetch)
        if project and project != "all":
            return [i for i in all_instances if i["project"] == project]
        return all_instances

    def get_lambda_functions(self, project: Optional[str] = None) -> list[dict[str, Any]]:
        """Get Lambda functions with 24h invocation and error counts.

        Args:
            project: Filter to this project name, or None/\"all\" for all.

        Returns:
            List of function dicts with CloudWatch metrics.
        """
        def fetch() -> list[dict[str, Any]]:
            try:
                functions: list[dict[str, Any]] = []
                paginator = self._lambda_client.get_paginator("list_functions")
                for page in paginator.paginate():
                    for fn in page.get("Functions", []):
                        name = fn.get("FunctionName", "")
                        tags: dict[str, str] = {}
                        try:
                            tags = self._lambda_client.list_tags(
                                Resource=fn["FunctionArn"]
                            ).get("Tags", {})
                        except ClientError:
                            pass
                        functions.append({
                            "name": name,
                            "runtime": fn.get("Runtime", ""),
                            "memory": fn.get("MemorySize"),
                            "timeout": fn.get("Timeout"),
                            "last_modified": fn.get("LastModified"),
                            "code_size": fn.get("CodeSize"),
                            "project": self._classify_lambda(name, tags),
                            "invocations_24h": 0,
                            "errors_24h": 0,
                        })

                # Fetch 24h CloudWatch metrics per function
                now = datetime.now(timezone.utc)
                start = now - timedelta(hours=24)
                for fn in functions:
                    try:
                        for metric, key in [("Invocations", "invocations_24h"),
                                            ("Errors", "errors_24h")]:
                            resp = self._cloudwatch.get_metric_statistics(
                                Namespace="AWS/Lambda",
                                MetricName=metric,
                                Dimensions=[{"Name": "FunctionName",
                                             "Value": fn["name"]}],
                                StartTime=start, EndTime=now,
                                Period=86400, Statistics=["Sum"],
                            )
                            dps = resp.get("Datapoints", [])
                            if dps:
                                fn[key] = int(dps[0].get("Sum", 0))
                    except ClientError:
                        pass
                return functions
            except ClientError as e:
                logger.error("Lambda list_functions failed: %s", e)
                return []

        all_fns = self._cached("lambda_functions", self.TTL_LAMBDA, fetch)
        if project and project != "all":
            return [f for f in all_fns if f["project"] == project]
        return all_fns

    def get_s3_buckets(self, project: Optional[str] = None) -> list[dict[str, Any]]:
        """Get all S3 buckets with tags and location.

        Args:
            project: Filter to this project name, or None/\"all\" for all.

        Returns:
            List of bucket dicts with project classification.
        """
        def fetch() -> list[dict[str, Any]]:
            try:
                buckets: list[dict[str, Any]] = []
                for b in self._s3.list_buckets().get("Buckets", []):
                    name = b.get("Name", "")
                    tags: dict[str, str] = {}
                    try:
                        tag_resp = self._s3.get_bucket_tagging(Bucket=name)
                        tags = {t["Key"]: t["Value"]
                                for t in tag_resp.get("TagSet", [])}
                    except ClientError:
                        pass
                    location = ""
                    try:
                        loc = self._s3.get_bucket_location(Bucket=name)
                        location = loc.get("LocationConstraint") or "us-east-1"
                    except ClientError:
                        pass
                    created = b.get("CreationDate")
                    if isinstance(created, datetime):
                        created = created.isoformat()
                    buckets.append({
                        "name": name,
                        "region": location,
                        "created": created,
                        "project": self._classify_bucket(name, tags),
                    })
                return buckets
            except ClientError as e:
                logger.error("S3 list_buckets failed: %s", e)
                return []

        all_buckets = self._cached("s3_buckets", self.TTL_S3, fetch)
        if project and project != "all":
            return [b for b in all_buckets if b["project"] == project]
        return all_buckets

    def get_cloudfront_distributions(self, project: Optional[str] = None) -> list[dict[str, Any]]:
        """Get all CloudFront distributions.

        Args:
            project: Filter to this project name, or None/\"all\" for all.

        Returns:
            List of distribution dicts with project classification.
        """
        def fetch() -> list[dict[str, Any]]:
            try:
                dists: list[dict[str, Any]] = []
                paginator = self._cloudfront.get_paginator("list_distributions")
                for page in paginator.paginate():
                    dist_list = page.get("DistributionList", {})
                    for d in dist_list.get("Items", []) or []:
                        aliases = d.get("Aliases", {}).get("Items", []) or []
                        dists.append({
                            "id": d.get("Id"),
                            "domain": d.get("DomainName"),
                            "aliases": aliases,
                            "status": d.get("Status"),
                            "enabled": d.get("Enabled"),
                            "comment": d.get("Comment", ""),
                            "project": self._classify_distribution(d),
                        })
                return dists
            except ClientError as e:
                logger.error("CloudFront list_distributions failed: %s", e)
                return []

        all_dists = self._cached("cloudfront_dists", self.TTL_CLOUDFRONT, fetch)
        if project and project != "all":
            return [d for d in all_dists if d["project"] == project]
        return all_dists

    def get_route53_zones(self, project: Optional[str] = None) -> list[dict[str, Any]]:
        """Get Route53 hosted zones with record counts.

        Args:
            project: Filter to this project name, or None/\"all\" for all.

        Returns:
            List of zone dicts with project classification.
        """
        def fetch() -> list[dict[str, Any]]:
            try:
                zones: list[dict[str, Any]] = []
                for z in self._route53.list_hosted_zones().get("HostedZones", []):
                    zone_id = z.get("Id", "").split("/")[-1]
                    zone_project = "other"
                    for pn, pc in PROJECTS.items():
                        if zone_id in pc.route53_zone_ids:
                            zone_project = pn
                            break
                    zones.append({
                        "id": zone_id,
                        "name": z.get("Name", "").rstrip("."),
                        "record_count": z.get("ResourceRecordSetCount", 0),
                        "private": z.get("Config", {}).get("PrivateZone", False),
                        "project": zone_project,
                    })
                return zones
            except ClientError as e:
                logger.error("Route53 list_hosted_zones failed: %s", e)
                return []

        all_zones = self._cached("route53_zones", self.TTL_ROUTE53, fetch)
        if project and project != "all":
            return [z for z in all_zones if z["project"] == project]
        return all_zones

    def get_cost_summary(self) -> dict[str, Any]:
        """Get month-to-date cost estimate from CloudWatch billing metrics.

        Returns:
            Dict with 'mtd' dollar amount and 'currency'.
        """
        def fetch() -> dict[str, Any]:
            try:
                now = datetime.now(timezone.utc)
                start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                resp = self._cloudwatch.get_metric_statistics(
                    Namespace="AWS/Billing",
                    MetricName="EstimatedCharges",
                    Dimensions=[{"Name": "Currency", "Value": "USD"}],
                    StartTime=start, EndTime=now,
                    Period=86400, Statistics=["Maximum"],
                )
                dps = resp.get("Datapoints", [])
                if dps:
                    latest = max(dps, key=lambda d: d.get("Timestamp", ""))
                    return {"mtd": round(latest.get("Maximum", 0), 2),
                            "currency": "USD"}
                return {"mtd": None, "currency": "USD"}
            except ClientError as e:
                logger.warning("Billing metrics unavailable: %s", e)
                return {"mtd": None, "currency": "USD", "error": str(e)}

        return self._cached("cost_summary", self.TTL_COST, fetch)

    def get_all_projects_summary(self) -> list[dict[str, Any]]:
        """Get resource counts per project for the overview.

        Returns:
            List of project summary dicts with counts per resource type.
        """
        ec2 = self.get_ec2_instances()
        lambdas = self.get_lambda_functions()
        s3 = self.get_s3_buckets()
        cf = self.get_cloudfront_distributions()
        r53 = self.get_route53_zones()

        all_projects: set[str] = set(PROJECTS.keys()) | {"other"}
        for lst in (ec2, lambdas, s3, cf, r53):
            for r in lst:
                all_projects.add(r["project"])

        summaries = []
        for proj in sorted(all_projects):
            config = PROJECTS.get(proj)
            summaries.append({
                "name": proj,
                "display_name": config.display_name if config else proj.title(),
                "ec2": len([r for r in ec2 if r["project"] == proj]),
                "lambda": len([r for r in lambdas if r["project"] == proj]),
                "s3": len([r for r in s3 if r["project"] == proj]),
                "cloudfront": len([r for r in cf if r["project"] == proj]),
                "route53": len([r for r in r53 if r["project"] == proj]),
            })
        return summaries

    def get_project_resources(self, project: str) -> dict[str, Any]:
        """Get all resources for a single project.

        Args:
            project: The project name.

        Returns:
            Dict with all resource types for the project.
        """
        config = PROJECTS.get(project)
        return {
            "project": project,
            "display_name": config.display_name if config else project.title(),
            "ec2": self.get_ec2_instances(project),
            "lambda": self.get_lambda_functions(project),
            "s3": self.get_s3_buckets(project),
            "cloudfront": self.get_cloudfront_distributions(project),
            "route53": self.get_route53_zones(project),
        }
