#!/usr/bin/env python3
"""Validate relationships among approved events, mappings, and expected manifests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_pair(event_path: str, manifest_path: str) -> None:
    contract = load_yaml("catalog/contracts/server-build/contract.yaml")
    mapping = load_yaml("catalog/mappings/server-build-defaults.yaml")
    event = load_yaml(event_path)
    manifest = load_yaml(manifest_path)

    requested = event["spec"]["requested_build"]
    request = event["spec"]["request"]
    approval = event["spec"]["approval"]
    manifest_spec = manifest["spec"]

    build_profile = mapping["spec"]["buildProfiles"][requested["build_profile"]]
    os_profile = mapping["spec"]["osProfiles"][requested["os_version"]]
    placement_profile = mapping["spec"]["placementProfiles"][requested["site"]]
    network_profile = mapping["spec"]["networkProfiles"][requested["network_profile"]]
    platform_operations = mapping["spec"]["platformOperations"][requested["os_family"]]
    environment_operations = mapping["spec"]["environmentOperations"][
        requested["environment"]
    ]
    environment_group = mapping["spec"]["environmentGroups"][requested["environment"]]

    supported_versions = contract["spec"]["supportedPlatforms"][requested["os_family"]][
        "osVersions"
    ]
    require(
        requested["os_version"] in supported_versions,
        "Requested OS version is not supported",
    )
    require(
        os_profile["os_family"] == requested["os_family"],
        "OS family and profile do not match",
    )
    require(
        manifest["kind"] == "BuildManifest", "Expected artifact is not a BuildManifest"
    )
    require(
        manifest["metadata"]["revision"] == 1, "Initial manifest must be revision 1"
    )
    require(
        manifest["metadata"]["contract"] == "server-build@0.2.0",
        "Contract version mismatch",
    )
    require(
        manifest_spec["request"] == request,
        "Request identity or source reference changed",
    )
    require(manifest_spec["approval"] == approval, "Approval evidence changed")
    require(
        manifest_spec["build"]["os_family"] == requested["os_family"],
        "Manifest OS family mismatch",
    )
    require(
        manifest_spec["build"]["os_version"] == requested["os_version"],
        "Manifest OS version mismatch",
    )
    require(
        manifest_spec["build"]["cpu_count"] == build_profile["cpu_count"],
        "CPU mapping mismatch",
    )
    require(
        manifest_spec["build"]["memory_gb"] == build_profile["memory_gb"],
        "Memory mapping mismatch",
    )
    require(
        manifest_spec["virtualization"]["provider"] == "vmware",
        "Virtualization provider mismatch",
    )
    require(
        manifest_spec["virtualization"]["template"] == os_profile["vmware_template"],
        "VMware template mapping mismatch",
    )
    require(
        manifest_spec["placement"]["compute_cluster"]
        == placement_profile["compute_cluster"],
        "VMware cluster mapping mismatch",
    )
    require(
        manifest_spec["placement"]["storage_policy"]
        == placement_profile["storage_policy"],
        "Storage policy mapping mismatch",
    )
    require(
        manifest_spec["integrations"]["ipam"]["dns_domain"]
        == network_profile["dns_domain"],
        "Network profile mapping mismatch",
    )
    require(
        manifest_spec["operations"]["support_group"]
        == platform_operations["support_group"],
        "Support-group mapping mismatch",
    )
    require(
        manifest_spec["operations"]["monitoring_profile"]
        == environment_operations["monitoring_profile"],
        "Monitoring mapping mismatch",
    )
    require(
        manifest_spec["operations"]["backup_profile"]
        == environment_operations["backup_profile"],
        "Backup mapping mismatch",
    )

    expected_groups = [
        *os_profile["inventory_groups"],
        *placement_profile["inventory_groups"],
        environment_group,
    ]
    require(
        manifest_spec["derived"]["inventory_groups"] == expected_groups,
        "Inventory group mapping mismatch",
    )
    require(
        manifest_spec["derived"]["connection_profile"]
        == os_profile["connection_profile"],
        "Connection profile mapping mismatch",
    )
    require(
        manifest_spec["provenance"]["source_event"] == event["metadata"]["event_id"],
        "Source event provenance mismatch",
    )


def validate_invalid_fixture() -> None:
    mapping = load_yaml("catalog/mappings/server-build-defaults.yaml")
    event = load_yaml("catalog/request-events/examples/invalid-request-approved.yaml")
    requested = event["spec"]["requested_build"]
    os_profile = mapping["spec"]["osProfiles"][requested["os_version"]]
    require(
        os_profile["os_family"] != requested["os_family"],
        "Invalid fixture no longer exercises an OS family/version mismatch",
    )


def main() -> None:
    validate_pair(
        "catalog/request-events/examples/windows-request-approved.yaml",
        "catalog/build-manifests/examples/windows-build-complete.yaml",
    )
    validate_pair(
        "catalog/request-events/examples/linux-request-approved.yaml",
        "catalog/build-manifests/examples/linux-build-complete.yaml",
    )
    validate_invalid_fixture()
    print("Validated Windows/Linux manifest fixtures and invalid platform scenario.")


if __name__ == "__main__":
    main()
