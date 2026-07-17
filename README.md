# Pipeline Playground

Reference implementation for contract-driven infrastructure automation, Ansible development workflows, and a mock IPAM provisioning path.

This repository is a starter proof of concept for two things that need to fit together:

1. A data contract catalog that describes datasets, owners, interfaces, schemas, quality expectations, and control requirements.
2. A mature automation development pipeline for Ansible Automation Platform that can consume catalog metadata and turn approved contracts into automation inputs.

The current goal is not to fully implement a platform. The goal is to make the operating model concrete enough to review, identify gaps, and decide what to build next.

## Why this repo exists

Teams often have three separate problems:

- automation depends on shared data that is not governed clearly
- Ansible development practices drift between teams
- integrations with systems like IPAM or inventory become hard-coded before the input contract is stable

This repository shows a practical way to connect those concerns:

- define a contract
- validate it
- generate normalized automation inputs
- run automation against a controlled toolchain
- simulate an external integration before wiring real infrastructure

## What is in this repo

- [docs/poc-overview.md](docs/poc-overview.md) - scope, objectives, assumptions, and phased build-out
- [docs/architecture.md](docs/architecture.md) - architecture and flow from contract to automation
- [docs/toolchain.md](docs/toolchain.md) - development workflow for local workstations and OpenShift Dev Spaces
- [docs/reality-check.md](docs/reality-check.md) - what in the current concept is solid, what needs adjustment, and what to prove first
- [docs/infoblox-simulation.md](docs/infoblox-simulation.md) - practical mock strategy for the IPAM use case without a real target platform
- [catalog/contracts/customer-360/contract.yaml](catalog/contracts/customer-360/contract.yaml) - example data contract
- [catalog/contracts/server-build-infoblox/contract.yaml](catalog/contracts/server-build-infoblox/contract.yaml) - example infrastructure contract tied to server provisioning and IP allocation
- [ansible/README.md](ansible/README.md) - how Ansible development ties into catalog content
- [ansible/playbooks/mock-infoblox-provision.yml](ansible/playbooks/mock-infoblox-provision.yml) - runnable mock contract-to-provisioning flow
- [.devfile.yaml](.devfile.yaml) - starter OpenShift Dev Spaces definition
- [execution-environment/Containerfile](execution-environment/Containerfile) - starter execution environment for consistent automation development

## Intended POC outcome

The POC should answer these questions:

- What does a useful internal data contract look like?
- What metadata should be authoritative in the catalog?
- Which parts of the contract should drive automation generation or policy checks?
- What is the minimum development toolchain needed to safely build and test AAP automation around those contracts?
- Where are the architecture and governance gaps before production rollout?

## Public repository note

The examples in this repository are intentionally sanitized:

- no internal organization names
- no production endpoints
- no private datasets
- mock infrastructure payloads only

Vendor and open-source product names are used only to illustrate generally applicable patterns.

## Repository structure

```text
catalog/
  contracts/
docs/
ansible/
  playbooks/
  roles/
  vars/
execution-environment/
simulations/
```

## Quick start

Use the mock provisioning flow as the first runnable demo.

With Ansible installed:

```bash
cd ansible
ansible-playbook playbooks/mock-infoblox-provision.yml -e @vars/request-good.yml
```

With ansible-navigator:

```bash
cd ansible
ansible-navigator run playbooks/mock-infoblox-provision.yml -e @vars/request-good.yml --mode stdout
```

Expected output artifacts:

- `ansible/generated-vars/<request_id>-contract-vars.yml`
- `ansible/generated-vars/<request_id>-host-record.json`

## Recommended next steps

1. Replace the sample contract with one real internal use case.
2. Add your architecture documents into `docs/input/`.
3. Refine the metadata model based on those documents.
4. Decide whether the first automation target is:
   - validation only,
   - inventory/config generation,
   - or AAP job template provisioning.
5. Add a thin validation pipeline once the contract shape is stable.
6. Use the IPAM simulation path to prove the contract-to-automation flow before attempting real API integration.

## Current runnable demo path

The current repo can now demonstrate:

- contract-driven input validation
- derived zone-token generation
- normalized vars generation for automation consumption
- mocked IPAM subnet lookup and IP allocation
- mock host-record payload generation
