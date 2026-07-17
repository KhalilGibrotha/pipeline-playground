# S3-compatible artifact storage

## Recommendation

S3-compatible object storage makes sense for build manifests and automation evidence, especially when the current alternative is slow shared folders and ad hoc CSV tracking.

Use it as a durable artifact and history layer. Do not treat it as a transactional workflow database, a relational reporting store, or a replacement for CMDB discovery.

## Why it fits this POC

Build automation produces naturally object-shaped records:

- approved request snapshots
- YAML or JSON manifests
- readiness reports
- normalized variables and inventory snapshots
- VMware, IPAM, and OS results
- logs and test evidence
- reconciliation reports
- final handoff snapshots

An object API also avoids coupling automation to a mounted file-share path. Object keys, versions, checksums, metadata, access policies, and lifecycle capabilities are better aligned with machine-to-machine automation than users editing a shared CSV.

## Proposed object layout

```text
server-builds/
  requests/<request-id>/
    manifest.yaml
    approval/
      request-snapshot.yaml
    events/
      <timestamp>-manifest-created.json
      <timestamp>-infrastructure-provisioned.json
      <timestamp>-build-blocked.json
      <timestamp>-build-resumed.json
    artifacts/
      normalized-vars.yaml
      inventory.yaml
      vmware-result.json
      ipam-result.json
      os-configuration-result.json
      reconciliation.json
    handoff/
      final-manifest.yaml
      handoff-evidence.json
```

Recommended behavior:

- `manifest.yaml` is the latest projection and relies on bucket versioning for prior versions.
- `events/` is append-only and provides an understandable transition history.
- `artifacts/` stores phase outputs using unique keys where practical.
- `handoff/` is written only after completion and retained according to an agreed schedule.

## Request approval trigger

The request system or an integration event should call a small manifest-creation workflow when approval succeeds:

1. verify the event is an approved request and has not already been processed
2. capture an approval/request snapshot or immutable source reference
3. select the contract version
4. create the initial manifest
5. write a `manifest-created` event
6. return the object key, version ID or checksum, and correlation ID
7. begin readiness assessment

Idempotency should use the source request ID plus approval reference. A retry must return or update the same logical build record instead of creating a second server request.

## Desired-state retention and CMDB reconciliation

The manifest fills a gap that discovery-only CMDB data cannot fill before the VM exists. It records what was approved and what automation intended to build.

At handoff:

1. read desired values from the manifest
2. gather observed VMware and guest values
3. read available CMDB discovery values
4. compare the fields that should agree
5. record matches, mismatches, and unavailable discovered values
6. store the reconciliation artifact and final manifest snapshot

This creates lineage without pretending the object store is the authoritative operational inventory.

## Capability checks for an on-premises service

Do not assume every S3-compatible implementation supports every AWS S3 feature identically. Evaluate:

- object and bucket versioning
- conditional writes or another concurrency strategy
- checksums and ETags
- encryption in transit and at rest
- service-account and bucket/prefix access policies
- retention, lifecycle, and legal-hold/object-lock behavior if required
- event notifications
- replication and recovery
- object size and metadata limits
- audit logging
- API compatibility with the selected SDK or Ansible module
- performance from Dev Spaces, CI runners, and AAP execution nodes

## POC comparison with the file-share approach

Measure rather than argue only from architecture. A useful demonstration compares:

| Measure | Shared folder and CSV | S3-compatible artifact flow |
| --- | --- | --- |
| Create/read latency | record observed timing | record observed timing |
| Concurrent writers | manual coordination or file locking | unique keys plus tested concurrency behavior |
| History | copies and filenames | object versions and append-only events |
| Machine access | mount and path dependency | authenticated API |
| Integrity | informal | checksum/version evidence |
| Automation trigger | polling or manual | API call and optional event notification |
| Retention | folder convention | tested lifecycle/retention capability |
| Traceability | CSV row and file timestamps | request key, event history, versions, and evidence |

The POC should publish measured results and limitations of the actual on-premises service.

## Local development path

A local S3-compatible service can be run with Podman or Kubernetes to prove object keys, version handling, retries, and artifact layout. That validates the adapter behavior, not the enterprise service's performance or feature set.

The adapter should accept endpoint, bucket, and credential references at runtime. No endpoint or credential should be embedded in a manifest.

The `amazon.aws.s3_object` module supports an alternate `endpoint_url` and several S3-compatible services, but its documentation notes that non-AWS endpoints are not all tested by the collection. Compatibility with the organization's service must therefore be an explicit POC test.

## Production questions left open

- Which system owns active lifecycle state and concurrency?
- Which object is mutable, and which records must be append-only?
- What is the retention period after handoff or cancellation?
- Is object lock required, permitted, or unnecessary?
- How will consumers search builds without listing large prefixes?
- What metadata may be stored, and what must be excluded?
- How are service identities, certificates, and endpoint trust distributed to AAP?
