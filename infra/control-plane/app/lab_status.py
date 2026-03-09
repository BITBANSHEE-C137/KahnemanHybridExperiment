"""AWS resource status queries for the ML Lab Control Plane.

Provides read-only access to fleet status, training status, and cost
data from the lab's AWS infrastructure. All methods handle boto3
exceptions gracefully and return error information rather than raising.
"""

import json
from typing import Any

import boto3
from botocore.exceptions import ClientError


_FLEET_ID = "fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a"
_S3_BUCKET = "ml-lab-004507070771"
_S3_PREFIX = "dual-system-research-data"


class LabStatus:
    """Queries AWS resources for lab infrastructure status.

    Provides fleet, training, and cost status from EC2, S3, and
    CloudWatch respectively.
    """

    def __init__(self) -> None:
        """Initializes boto3 clients for EC2, S3, and CloudWatch."""
        self._ec2 = boto3.client("ec2")
        self._s3 = boto3.client("s3")
        self._cloudwatch = boto3.client("cloudwatch")

    def get_fleet_status(self) -> dict[str, Any]:
        """Returns the current EC2 Fleet status and instance details.

        Calls DescribeFleets and DescribeFleetInstances for the
        configured fleet ID.

        Returns:
            Dict with fleet state, capacity info, and running instances.
            On error, returns a dict with 'status': 'error' and 'message'.
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
                "fulfilled_on_demand_capacity": fleet.get(
                    "FulfilledOnDemandCapacity"
                ),
            }

            # Get running instances
            instances_resp = self._ec2.describe_fleet_instances(
                FleetId=_FLEET_ID
            )
            active_instances = instances_resp.get("ActiveInstances", [])
            result["instances"] = [
                {
                    "instance_id": inst.get("InstanceId"),
                    "instance_type": inst.get("InstanceType"),
                    "spot_request_id": inst.get("SpotInstanceRequestId"),
                    "health": inst.get("InstanceHealth"),
                }
                for inst in active_instances
            ]

            return result

        except ClientError as exc:
            return {
                "status": "error",
                "fleet_id": _FLEET_ID,
                "message": str(exc),
            }

    def get_training_status(self) -> dict[str, Any]:
        """Returns the latest training status from S3.

        Reads training_status.json from the lab's S3 bucket.

        Returns:
            The parsed JSON contents of the training status file.
            On error, returns {"status": "unknown"}.
        """
        key = f"{_S3_PREFIX}/status/training_status.json"
        try:
            resp = self._s3.get_object(Bucket=_S3_BUCKET, Key=key)
            body = resp["Body"].read().decode("utf-8")
            return json.loads(body)
        except (ClientError, json.JSONDecodeError, KeyError):
            return {"status": "unknown"}

    def get_cost_status(self) -> dict[str, Any]:
        """Returns the current cost ledger data from S3.

        Reads ledger.json from the lab's S3 bucket.

        Returns:
            The parsed JSON contents of the cost ledger file.
            On error, returns {"status": "unknown"}.
        """
        key = f"{_S3_PREFIX}/cost/ledger.json"
        try:
            resp = self._s3.get_object(Bucket=_S3_BUCKET, Key=key)
            body = resp["Body"].read().decode("utf-8")
            return json.loads(body)
        except (ClientError, json.JSONDecodeError, KeyError):
            return {"status": "unknown"}

    def get_full_status(self) -> dict[str, Any]:
        """Returns combined fleet, training, and cost status.

        Calls all three status methods and combines them into a
        single response dict.

        Returns:
            Dict with 'fleet', 'training', and 'cost' keys.
        """
        return {
            "fleet": self.get_fleet_status(),
            "training": self.get_training_status(),
            "cost": self.get_cost_status(),
        }
