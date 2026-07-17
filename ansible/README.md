# Ansible integration model

The Ansible content in this POC should consume validated contract artifacts, not raw edits from the catalog tree.

## Intended pattern

1. Contract YAML is reviewed and validated.
2. A pipeline generates normalized variables or templates from the contract.
3. Playbooks and roles consume generated inputs.
4. AAP executes against approved environments.

## Suggested next repo additions

- `ansible/playbooks/mock-infoblox-provision.yml`
- `ansible/roles/contract_preflight/`
- `ansible/roles/contract_generate_vars/`
- `ansible/roles/mock_infoblox/`
- `ansible/generated-vars/`

## Why this pattern matters

It avoids coupling operational automation directly to arbitrary hand-edited metadata and gives you a clean promotion point after validation.

## Runnable mock flow

The repository now includes a thin mock provisioning path:

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
