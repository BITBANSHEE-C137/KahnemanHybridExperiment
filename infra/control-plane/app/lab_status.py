"""AWS resource status queries for the ML Lab Control Plane.

Provides read-only access to fleet status, training status, and cost
data from the lab's AWS infrastructure. All methods handle boto3
exceptions gracefully and return error information rather than raising.
"""

import json
from datetime import datetime, timezone
from typing import Any

import boto3
from botocore.exceptions import ClientError


_FLEET_ID = "fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a"
_S3_BUCKET = "ml-lab-004507070771"
_S3_PREFIX = "dual-system-research-data"


class LabStatus:
    """Queries AWS resources for lab infrastructure status."""

    def __init__(self) -> None:
        self._ec2 = boto3.client("ec2")
        self._s3 = boto3.client("s3")
        self._cloudwatch = boto3.client("cloudwatch")

    def _enrich_instances(self, instances: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Enrich fleet instances with AZ, public IP, launch time, and spot price.

        Takes the basic instance list from describe_fleet_instances and adds
        detailed information from describe_instances and current spot pricing.

        Args:
            instances: List of instance dicts with at least 'instance_id' and
                'instance_type' keys.

        Returns:
            The same list with additional keys added to each instance dict:
            az, public_ip, private_ip, launch_time, state, spot_price.
        """
        if not instances:
            return instances

        instance_ids = [
            inst["instance_id"]
            for inst in instances
            if inst.get("instance_id")
        ]
        if not instance_ids:
            return instances

        # Fetch detailed instance info
        detail_map: dict[str, dict[str, Any]] = {}
        try:
            paginator = self._ec2.get_paginator("describe_instances")
            for page in paginator.paginate(InstanceIds=instance_ids):
                for reservation in page.get("Reservations", []):
                    for ec2_inst in reservation.get("Instances", []):
                        iid = ec2_inst.get("InstanceId")
                        launch_time = ec2_inst.get("LaunchTime")
                        if isinstance(launch_time, datetime):
                            launch_time = launch_time.isoformat()
                        detail_map[iid] = {
                            "az": ec2_inst.get("Placement", {}).get("AvailabilityZone"),
                            "public_ip": ec2_inst.get("PublicIpAddress"),
                            "private_ip": ec2_inst.get("PrivateIpAddress"),
                            "launch_time": launch_time,
                            "state": ec2_inst.get("State", {}).get("Name"),
                            "instance_type": ec2_inst.get("InstanceType"),
                        }
        except ClientError:
            # If describe_instances fails, continue without enrichment
            pass

        # Collect unique (instance_type, az) pairs for spot price lookups
        spot_queries: set[tuple[str, str]] = set()
        for inst in instances:
            iid = inst.get("instance_id")
            detail = detail_map.get(iid, {})
            az = detail.get("az")
            itype = detail.get("instance_type") or inst.get("instance_type")
            if az and itype:
                spot_queries.add((itype, az))

        # Fetch current spot prices
        spot_prices: dict[tuple[str, str], str] = {}
        for itype, az in spot_queries:
            try:
                resp = self._ec2.describe_spot_price_history(
                    InstanceTypes=[itype],
                    AvailabilityZone=az,
                    ProductDescriptions=["Linux/UNIX"],
                    StartTime=datetime.now(timezone.utc),
                    MaxResults=1,
                )
                history = resp.get("SpotPriceHistory", [])
                if history:
                    spot_prices[(itype, az)] = history[0].get("SpotPrice", "")
            except ClientError:
                continue

        # Merge enrichment data into instance dicts
        for inst in instances:
            iid = inst.get("instance_id")
            detail = detail_map.get(iid, {})

            inst["az"] = detail.get("az")
            inst["public_ip"] = detail.get("public_ip")
            inst["private_ip"] = detail.get("private_ip")
            inst["launch_time"] = detail.get("launch_time")
            inst["state"] = detail.get("state")

            az = detail.get("az")
            itype = detail.get("instance_type") or inst.get("instance_type")
            if az and itype:
                inst["spot_price"] = spot_prices.get((itype, az))
            else:
                inst["spot_price"] = None

        return instances

    def get_fleet_status(self) -> dict[str, Any]:
        """Get EC2 Fleet status including enriched instance details.

        Returns:
            Dict with fleet state, capacity info, and enriched instance list.
        """
        try:
            fleet_resp = self._ec2.describe_fleets(FleetIds=[_FLEET_ID])
            fleets = fleet_resp.get("Fleets", [])
            if not fleets:
                return {"status": "not_found", "fleet_id": _FLEET_ID}

            fleet = fleets[0]
            result: dict[str, Any] = {
                "fleet_id": _FLEET_ID,
                "state": fleet.get("FleetState"),
                "target_capacity": fleet.get("TargetCapacitySpecification", {}),
                "fulfilled_capacity": fleet.get("FulfilledCapacity"),
                "fulfilled_on_demand_capacity": fleet.get("FulfilledOnDemandCapacity"),
            }

            instances_resp = self._ec2.describe_fleet_instances(FleetId=_FLEET_ID)
            active_instances = instances_resp.get("ActiveInstances", [])
            instances = [
                {
                    "instance_id": inst.get("InstanceId"),
                    "instance_type": inst.get("InstanceType"),
                    "spot_request_id": inst.get("SpotInstanceRequestId"),
                    "health": inst.get("InstanceHealth"),
                }
                for inst in active_instances
            ]

            result["instances"] = self._enrich_instances(instances)
            return result

        except ClientError as exc:
            return {
                "status": "error",
                "fleet_id": _FLEET_ID,
                "message": str(exc),
            }

    def get_training_status(self) -> dict[str, Any]:
        """Get latest training status from S3.

        Returns:
            Dict with training metrics or {"status": "unknown"} on failure.
        """
        key = f"{_S3_PREFIX}/status/training_status.json"
        try:
            resp = self._s3.get_object(Bucket=_S3_BUCKET, Key=key)
            body = resp["Body"].read().decode("utf-8")
            return json.loads(body)
        except (ClientError, json.JSONDecodeError, KeyError):
            return {"status": "unknown"}

    def get_cost_status(self) -> dict[str, Any]:
        """Get cost ledger from S3.

        Returns:
            Dict with cost data or {"status": "unknown"} on failure.
        """
        key = f"{_S3_PREFIX}/cost/ledger.json"
        try:
            resp = self._s3.get_object(Bucket=_S3_BUCKET, Key=key)
            body = resp["Body"].read().decode("utf-8")
            return json.loads(body)
        except (ClientError, json.JSONDecodeError, KeyError):
            return {"status": "unknown"}

    def get_full_status(self) -> dict[str, Any]:
        """Get combined fleet, training, and cost status.

        Returns:
            Dict with 'fleet', 'training', and 'cost' keys.
        """
        return {
            "fleet": self.get_fleet_status(),
            "training": self.get_training_status(),
            "cost": self.get_cost_status(),
        }
