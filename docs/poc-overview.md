# POC overview

## Objective

Prove an achievable development and delivery pattern for modular Ansible automation by applying it to Windows and Linux virtual-machine builds on VMware.

The data contract catalog records stable definitions that teams need to share. A manifest created at request approval retains desired values and tracks one build through pauses, integrations, reconciliation, and handoff.

## Leadership primer

### Data contracts as code

A data contract is a versioned agreement about the information automation may
trust. It defines valid fields, accountable owners and sources, compatibility,
and which values are required at each phase.

Keeping the contract in source control makes changes reviewable and testable.
It reduces developer guesswork, makes integration handoffs explicit, and
creates a stable interface for reusable automation.

### Build manifest

A build manifest is the durable tracking record for one approved server
request. It preserves the original intent, current phase, missing information,
next owner, resume point, and evidence references.

The manifest makes waiting visible and allows a build to stop safely instead of
holding an AAP job open while people gather data. It also preserves pre-build
intent that a discovery-only CMDB cannot observe.

### AAP workflow

AAP coordinates short jobs: load the current manifest, assess readiness,
execute one phase, and persist the result. If a required value is missing, the
workflow records a controlled blocked state and exits. A later request event,
webhook, or schedule launches the next short run from the retained revision.

The contract defines the rules, the manifest carries state and evidence, AAP
coordinates execution, and the CMDB continues to represent discovered
operational state.

## Problems to solve

1. Integration and build data cannot be discovered or tracked consistently.
2. A server is partially built and waits indefinitely for later manual inputs.
3. A discovery-only CMDB does not preserve approved pre-build intent.
4. Developers choose inventory groups and variables because decision ownership is unclear.
5. Automation logic is copied because teams cannot safely consume shared modules.
6. Windows and Linux lifecycle behavior drifts even where requirements are common.
7. Shared folders and CSV files are slow, difficult to automate, and weak at retaining provenance.
8. Handoffs do not identify completed work, blockers, evidence, reconciliation, or the next owner.

## Artifact model

| Artifact | Purpose | Likely home |
| --- | --- | --- |
| Contract definition | Required fields, ownership, mappings, readiness gates, and interfaces | Git repository |
| Build manifest | Approved intent, current phase, values, provenance, blockers, and artifact references for one server | S3-compatible object store, coordinated by workflow/request system |
| Lifecycle event | Append-only record of a transition, failure, retry, or resume | S3-compatible object store |
| Evidence artifact | VMware, IPAM, OS, testing, and reconciliation results | S3-compatible object store |
| Final handoff snapshot | Origin, final desired/observed result, and handoff success | retained object storage |
| CMDB record | Discovered operational state | existing discovery-driven CMDB |

The manifest does not replace the CMDB. It preserves intent before discovery and provides reconciliation evidence after discovery.

## Primary test case

The focused scenario is documented in [server-build-poc.md](server-build-poc.md).

It covers:

- manifest creation from an approved request event
- a common Windows/Linux lifecycle
- stage-specific pause and resume behavior
- deterministic VMware placement, inventory, and variables
- OS-specific configuration adapters behind a common interface
- mocked Infoblox allocation and DNS behavior
- S3-compatible artifact retention
- desired-state comparison with simulated VMware and CMDB observations
- explicit completion evidence and handoff ownership

## In scope for the first maturity target

- common contract and build-manifest format
- Windows and Linux fixtures
- request-approval trigger contract and idempotency rule
- field source, owner, and provenance metadata
- stage-specific readiness rules
- VMware-first placement and provisioning model
- good, incomplete, invalid, and retry scenarios
- normalized inventory and variable generation
- local object-storage adapter and artifact layout
- reusable Ansible role boundaries
- lint, syntax, fixture, and behavior tests
- purpose-built execution environment
- local Podman and OpenShift Dev Spaces workflow
- generated readiness, reconciliation, and handoff evidence

## Deferred until the first path is proven

- production request-system, CMDB, VMware, Infoblox, Windows, Linux, or object-storage connectivity
- policy-as-code beyond validation and readiness rules
- catalog UI or developer portal
- enterprise approval orchestration redesign
- a new authoritative CMDB or inventory product
- automated controller configuration for all environments
- universal execution environment or collection governance

## Success criteria

1. An approved request creates exactly one logical manifest with an approval snapshot.
2. Windows and Linux use the same lifecycle and evidence envelope.
3. An incomplete request reports the blocked phase, missing fields, expected sources, and owners.
4. A paused build retains desired and derived values and resumes without manual reconstruction.
5. The same approved facts produce the same VMware placement, inventory, and normalized variables.
6. Platform-specific behavior is isolated behind common role interfaces.
7. Good, invalid, blocked, retry, and mismatch paths run in a repeatable toolchain.
8. Object storage retains version and evidence references without exposing credentials.
9. Handoff compares desired state with available VMware, guest, and CMDB observations.
10. The final artifact shows origination, outcomes, discrepancies, and handoff success.

## Delivery stages

### Stage 1: create and retain the tracking artifact

- define the common contract and manifests
- accept a synthetic approved-request payload
- create one idempotent manifest
- retain approval provenance
- write artifacts locally first, then through an S3-compatible adapter

### Stage 2: make readiness and pause/resume visible

- evaluate common lifecycle gates
- emit actionable blocker details
- retain phase, safe state, and next owner
- resume from an updated manifest

### Stage 3: standardize inputs and VMware provisioning

- encode owned placement and template mappings
- generate inventory and role inputs
- implement a VMware simulator adapter
- retain intended and returned VM identifiers

### Stage 4: prove Windows/Linux parity and modularity

- implement common role interfaces
- add thin Windows and Linux adapters
- test common outcomes and platform-specific differences
- promote stable, reusable content into a collection when a second consumer exists

### Stage 5: integrate and reconcile

- use the existing Infoblox mock
- simulate monitoring, backup, and discovery results
- compare desired and observed values
- generate the final handoff snapshot

### Stage 6: connect controlled systems

- test the organization's on-premises S3-compatible service
- replace VMware and IPAM mocks through supported collection-backed adapters
- use disposable Windows and Linux targets
- run through non-production AAP

## Questions the POC should force the organization to answer

- Which approval event authorizes manifest creation?
- Which system coordinates active phase transitions and prevents concurrent updates?
- Which system owns each required input?
- What is a safe VMware holding state at each blocked phase?
- Which defaults and mappings are platform standards?
- Which desired values must reconcile with discovery before handoff?
- How long are manifests and evidence retained?
- How are active builds searched without returning to shared CSV tracking?
- Who owns shared automation and its release lifecycle?
