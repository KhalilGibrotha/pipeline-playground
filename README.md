# Pipeline Playground

Proof of concept for a modern Ansible automation development and delivery model, demonstrated through Windows and Linux server builds on VMware.

The practical goal is to replace incomplete handoffs, developer-created inventory decisions, slow file-share tracking, and manually assembled variables with a visible, tested, repeatable flow.

## Problem this POC addresses

A server request may be approved before every downstream integration value is available. That commonly leads to:

- a server being partially built and held while people search for missing information
- intended build data being scattered across tickets, CSV files, shared folders, inventories, and playbooks
- a discovery-only CMDB seeing a machine after creation but not preserving its approved intent or build history
- automation developers deciding values that should have an accountable business or platform owner
- Windows and Linux teams implementing similar lifecycle behavior differently
- handoffs that do not clearly state what is complete, blocked, or still owned by another group

## POC thesis

A small set of practices can improve this without first building an enterprise platform:

1. Create a build manifest when a server request is approved.
2. Preserve approved, supplied, and derived values with provenance throughout the build.
3. Evaluate stage-specific readiness so a build can pause and resume safely.
4. Generate inventory and automation variables from approved inputs and owned mappings.
5. Use one common lifecycle for Windows and Linux, with small platform-specific profiles.
6. Isolate VMware, IPAM, object storage, and other systems behind integration adapters.
7. Run tested Ansible content in a repeatable execution environment.
8. Retain final evidence showing origination, build results, reconciliation, and handoff success.

The contract catalog defines stable rules and interfaces. A build manifest is the instance-level desired-state and tracking record for one server. Object storage retains manifests, versions, events, and evidence. The workflow engine or request system still owns active coordination.

## Primary test case

```text
request approved -> manifest created -> readiness assessment
                 -> VMware provisioning -> OS-specific configuration
                 -> IPAM/DNS and operational integrations
                 -> observed-state reconciliation -> handoff snapshot
```

The same flow applies to Windows and Linux as far as practical. VMware is the primary infrastructure adapter and Infoblox is the first network integration adapter.

See [docs/server-build-poc.md](docs/server-build-poc.md) for the scenario and acceptance criteria.

## Artifact and state model

- **Contract definition** - fields, ownership, mappings, readiness gates, interfaces, and compatibility.
- **Build manifest** - approved intent, current phase, blockers, desired values, and provenance for one server.
- **Event/evidence artifacts** - append-only results from provisioning, validation, reconciliation, and handoff.
- **CMDB discovery** - observed operational state after infrastructure exists; it is not expected to create the pre-build record in this POC.

For production, an on-premises S3-compatible service is a strong candidate for durable artifacts. It is not assumed to be a transactional workflow database. See [docs/object-storage-artifacts.md](docs/object-storage-artifacts.md).

## Current state

The repository contains:

- a common server-build contract
- Windows and Linux build-manifest examples
- complete and intentionally blocked scenarios
- a mocked Infoblox variable-generation and allocation slice
- a starter execution environment and OpenShift Dev Spaces definition
- architecture, maturity, and object-storage guidance

Manifest creation, common Windows/Linux readiness assessment, and durable
pause/resume lifecycle updates are now implemented. The next slice is a local
S3-compatible artifact adapter.

## Repository guide

- [docs/poc-overview.md](docs/poc-overview.md) - scope, outcomes, and maturity stages
- [docs/server-build-poc.md](docs/server-build-poc.md) - Windows/Linux VMware test case
- [docs/architecture.md](docs/architecture.md) - state, artifact, adapter, and handoff boundaries
- [docs/process-views.md](docs/process-views.md) - complementary Mermaid views for leadership, architecture, and development discussions
- [docs/demo-runbook.md](docs/demo-runbook.md) - ten-minute engineering demonstration and reusable concept-lab pattern
- [docs/resources.md](docs/resources.md) - curated Red Hat, Ansible, workflow, testing, integration, and contract references
- [docs/roadmap.md](docs/roadmap.md) - maturity path and recommended next milestone
- [docs/object-storage-artifacts.md](docs/object-storage-artifacts.md) - S3-compatible artifact design and evaluation case
- [docs/toolchain.md](docs/toolchain.md) - local, Dev Spaces, CI, and AAP development flow
- [docs/reality-check.md](docs/reality-check.md) - grounded patterns, limitations, gaps, and first steps
- [docs/infoblox-simulation.md](docs/infoblox-simulation.md) - mock IPAM strategy
- [catalog/contracts/server-build/contract.yaml](catalog/contracts/server-build/contract.yaml) - common Windows/Linux build contract
- [catalog/contracts/server-build-infoblox/contract.yaml](catalog/contracts/server-build-infoblox/contract.yaml) - IPAM integration contract
- [catalog/mappings/server-build-defaults.yaml](catalog/mappings/server-build-defaults.yaml) - synthetic build, OS, placement, and inventory mappings
- [catalog/request-events/examples/](catalog/request-events/examples/) - synthetic approved-request events
- [catalog/build-manifests/examples/](catalog/build-manifests/examples/) - synthetic request instances
- [ansible/playbooks/mock-infoblox-provision.yml](ansible/playbooks/mock-infoblox-provision.yml) - current runnable mock slice

## Presentation assets

- [Leadership overview](outputs/pipeline-playground-leadership-brief.pptx) -
  problem framing, data contracts as code, the build manifest, the logical AAP
  workflow, proven outcomes, and a focused pilot decision.
- [Engineering walkthrough](outputs/pipeline-playground-engineering-demo.pptx) -
  repository layers, lifecycle roles, workflow nodes, testing gates, test
  responsibilities, and the next S3-compatible adapter increment.

## Current mock quick start

Create a Windows manifest from the default approved event:

```bash
cd ansible
ansible-playbook playbooks/create-build-manifest.yml
```

Create a Linux manifest:

```bash
cd ansible
ansible-playbook playbooks/create-build-manifest.yml \
  -e approved_event_name=linux-request-approved.yaml
```

Run the manifest creation, duplicate-event, Windows/Linux, and invalid-profile tests:

```bash
cd ansible
ansible-playbook playbooks/test-manifest-creation.yml
```

Run the blocked-to-ready Windows/Linux lifecycle test:

```bash
cd ansible
ansible-playbook playbooks/test-readiness-lifecycle.yml
```

Run the role-level Molecule scenario:

```bash
cd ansible
for role in roles/*; do
  (cd "$role" && molecule test)
done
```

The fixture relationships can also be checked from a Windows-native Python shell:

```bash
python scripts/validate_manifest_fixtures.py
```

The local artifact layout mirrors the proposed object-store keys under `ansible/generated-vars/server-builds/`.

Run the existing IPAM mock:

With Ansible installed:

```bash
cd ansible
ansible-playbook playbooks/mock-infoblox-provision.yml -e @vars/request-good.yml
```

With `ansible-navigator` and an execution environment:

```bash
cd ansible
ansible-navigator run playbooks/mock-infoblox-provision.yml -e @vars/request-good.yml --mode stdout
```

## Scope guardrails

The first maturity target does not require:

- a catalog portal or custom user interface
- a production policy engine
- write access to the CMDB
- production VMware, Infoblox, Windows, Linux, ITSM, or object-storage connectivity
- enterprise-wide workflow orchestration
- every automation group to adopt a collection on day one

## Public repository note

All examples are synthetic. The repository contains no internal organization names, production endpoints, credentials, private datasets, or real server records.
