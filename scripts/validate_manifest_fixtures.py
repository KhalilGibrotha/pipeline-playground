#!/usr/bin/env python3
"""Validate relationships among approved events, mappings, and expected manifests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SERVER_BUILD_ROOT = (
    "catalog/domains/infrastructure-provisioning/products/server-build"
)
INTAKE_EXAMPLES_ROOT = "catalog/domains/automation-intake/examples/server-requests"
ADDRESS_MANAGEMENT_ROOT = (
    "catalog/domains/network-services/products/address-management"
)


def load_yaml(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_pair(event_path: str, manifest_path: str) -> None:
    contract = load_yaml(f"{SERVER_BUILD_ROOT}/contracts/lifecycle/contract.yaml")
    mapping = load_yaml(f"{SERVER_BUILD_ROOT}/mappings/server-build-defaults.yaml")
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
    mapping = load_yaml(f"{SERVER_BUILD_ROOT}/mappings/server-build-defaults.yaml")
    event = load_yaml(f"{INTAKE_EXAMPLES_ROOT}/invalid-request-approved.yaml")
    requested = event["spec"]["requested_build"]
    os_profile = mapping["spec"]["osProfiles"][requested["os_version"]]
    require(
        os_profile["os_family"] != requested["os_family"],
        "Invalid fixture no longer exercises an OS family/version mismatch",
    )


def validate_catalog_relationships() -> None:
    catalog = load_yaml("catalog/catalog.yaml")
    lifecycle = load_yaml(f"{SERVER_BUILD_ROOT}/contracts/lifecycle/contract.yaml")
    mapping = load_yaml(f"{SERVER_BUILD_ROOT}/mappings/server-build-defaults.yaml")
    manifest_contract = load_yaml(
        f"{SERVER_BUILD_ROOT}/contracts/build-manifest/contract.yaml"
    )
    request_contract = load_yaml(
        "catalog/domains/automation-intake/contracts/"
        "server-request-approved/contract.yaml"
    )
    network_contract = load_yaml(
        f"{ADDRESS_MANAGEMENT_ROOT}/contracts/address-allocation/contract.yaml"
    )
    infoblox_adapter = load_yaml(
        f"{ADDRESS_MANAGEMENT_ROOT}/adapters/infoblox/adapter.yaml"
    )

    domain_refs = {item["ref"] for item in catalog["spec"]["domains"]}
    require(
        domain_refs
        == {
            "domain:automation-intake",
            "domain:infrastructure-provisioning",
            "domain:network-services",
        },
        "Catalog domain index is incomplete",
    )
    require(
        lifecycle["metadata"]["id"]
        == "contract:infrastructure-provisioning/server-build/lifecycle",
        "Server-build lifecycle contract ID changed",
    )
    require(
        manifest_contract["metadata"]["id"]
        == "contract:infrastructure-provisioning/server-build/build-manifest",
        "Build-manifest contract ID changed",
    )
    require(
        request_contract["metadata"]["id"]
        == "contract:automation-intake/server-request-approved",
        "Approved-request contract ID changed",
    )
    require(
        infoblox_adapter["spec"]["implements"] == network_contract["metadata"]["id"],
        "Infoblox adapter does not implement the address-allocation contract",
    )
    require(
        set(mapping["spec"]["networkProfiles"])
        <= set(
            network_contract["spec"]["inputs"]["network_profile"]["allowedValues"]
        ),
        "Server-build mapping contains a network profile rejected by "
        "the address-allocation contract",
    )


def main() -> None:
    validate_pair(
        f"{INTAKE_EXAMPLES_ROOT}/windows-request-approved.yaml",
        f"{SERVER_BUILD_ROOT}/examples/build-manifests/windows-build-complete.yaml",
    )
    validate_pair(
        f"{INTAKE_EXAMPLES_ROOT}/linux-request-approved.yaml",
        f"{SERVER_BUILD_ROOT}/examples/build-manifests/linux-build-complete.yaml",
    )
    validate_invalid_fixture()
    validate_catalog_relationships()
    print(
        "Validated catalog relationships, Windows/Linux manifests, "
        "and invalid platform scenario."
    )


if __name__ == "__main__":
    main()
