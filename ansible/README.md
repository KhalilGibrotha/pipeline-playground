# Ansible integration model

This directory implements approved-event manifest creation and the earlier mocked IPAM vertical slice. It does not yet implement readiness transitions or VMware and OS provisioning from `docs/server-build-poc.md`.

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

- add one readiness playbook for Windows and Linux manifests
- report missing fields with their expected source and decision owner
- generate normalized VMware placement, inventory, and variables
- represent a safe staged build and resume behavior
- retain manifest versions, events, and evidence through a local object-store adapter
- retain the existing mock Infoblox role as an integration adapter

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
