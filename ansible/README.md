# Ansible integration model

This directory implements approved-event manifest creation, common readiness
assessment, durable lifecycle updates, and the earlier mocked IPAM vertical
slice. It does not yet implement real VMware or OS provisioning from
`docs/server-build-poc.md`.

The Ansible content in this POC should consume validated contract artifacts, not raw edits from the catalog tree.

## Intended pattern

1. Contract YAML defines stable fields, ownership, gates, and integration behavior.
2. An approved-request event creates one idempotent build manifest.
3. The manifest carries desired values, provenance, phase, and artifact references.
4. Readiness checks identify which stage can proceed and explain blockers.
5. A pipeline generates normalized VMware placement, variables, inventory, and evidence.
6. Common roles call Windows, Linux, VMware, IPAM, storage, and reconciliation adapters.
7. AAP executes against approved environments.

## Next implementation slice

- retain manifest versions, events, and evidence through a local S3-compatible adapter
- test conditional writes and concurrent revision handling
- generate normalized VMware placement, inventory, and variables
- add a mocked VMware provider interface
- retain the existing mock Infoblox role as an integration adapter

## Readiness and lifecycle updates

The `readiness_assess` role evaluates every required field for a selected
contract gate. It returns all blockers with their expected source, decision
owner, safe state, and resume phase.

The `lifecycle_update` role:

1. verifies the expected manifest revision
2. rejects backward or unknown ready transitions
3. preserves the manifest `spec` while updating lifecycle status
4. writes an immutable numbered revision and current projection
5. writes an append-only lifecycle event
6. treats a replayed event ID as idempotent

Run the Windows/Linux blocked-to-ready regression:

```bash
cd ansible
ansible-playbook playbooks/test-readiness-lifecycle.yml
```

The test blocks a Windows build on network data and a Linux build on operations
data, supplies the missing values, resumes each build, rejects a stale revision,
and verifies that desired state is retained.

## Approved-event manifest creation

The `manifest_create` role:

1. validates approval evidence and build selectors
2. resolves owned build, OS, VMware placement, network, inventory, and operations mappings
3. rejects incompatible OS family/version combinations
4. creates manifest revision 1 under the local artifact root
5. writes an append-only `manifest-created` lifecycle event
6. treats request ID plus approval reference as the logical idempotency identity
7. rejects a conflicting event instead of overwriting the original manifest

Default Windows event:

```bash
cd ansible
ansible-playbook playbooks/create-build-manifest.yml
```

Linux event:

```bash
cd ansible
ansible-playbook playbooks/create-build-manifest.yml \
  -e approved_event_name=linux-request-approved.yaml
```

Behavior tests:

```bash
cd ansible
ansible-playbook playbooks/test-manifest-creation.yml
```

The tests compare generated Windows and Linux manifests with checked-in expected artifacts, replay the Windows event to verify idempotency, and confirm an incompatible platform request is rejected.

Role-level Molecule tests:

```bash
cd ansible
for role in roles/*; do
  (cd "$role" && molecule test)
done
```

Every role has a default Molecule scenario. The scenarios cover successful
behavior, Molecule's idempotence pass, deterministic outputs, and relevant
expected failures. They use Molecule's delegated driver because these roles
operate on catalog and simulation artifacts rather than managed target hosts.

## Why this pattern matters

It avoids coupling operational automation directly to arbitrary hand-edited metadata and gives you a clean promotion point after validation.

## Runnable mock flow

The repository includes a thin mock IPAM provisioning path:

1. load the provisioning contract
2. validate request inputs against required fields and enums
3. derive `ea_microsegment_id`
4. generate normalized vars into `ansible/generated-vars/`
5. simulate subnet lookup and IP allocation from mock Infoblox data
6. emit a mock host-record payload artifact

### Input files

- `ansible/vars/request-good.yml`
- `ansible/vars/request-no-subnet.yml`
- `ansible/vars/request-invalid.yml`

### Main playbook

- `ansible/playbooks/mock-infoblox-provision.yml`

### Expected outputs

- `ansible/generated-vars/<request_id>-contract-vars.yml`
- `ansible/generated-vars/<request_id>-host-record.json`

## How to run

### In Dev Spaces

From the repo root:

```bash
cd ansible
ansible-playbook playbooks/mock-infoblox-provision.yml -e @vars/request-good.yml
```

### With ansible-navigator against an execution environment

From the repo root:

```bash
cd ansible
ansible-navigator run playbooks/mock-infoblox-provision.yml -e @vars/request-good.yml --mode stdout
```

### Failure-path runs

Invalid enums:

```bash
cd ansible
ansible-playbook playbooks/mock-infoblox-provision.yml -e @vars/request-invalid.yml
```

No matching subnet in the mock data:

```bash
cd ansible
ansible-playbook playbooks/mock-infoblox-provision.yml -e @vars/request-no-subnet.yml
```
