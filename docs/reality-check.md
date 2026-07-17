# Reality check and planning guide

This is the maintained reality check for Pipeline Playground. Update it as the POC produces evidence.

## Current conclusion

Windows and Linux server builds on VMware are a strong first test case. They expose real problems in approval, desired-state retention, placement, inventory, integrations, pause/resume behavior, testing, and handoff while allowing most lifecycle behavior to remain platform-neutral.

The broadly reusable capabilities are:

- approval-triggered tracking-artifact creation
- integration-data definition and ownership
- request readiness and blocker reporting
- desired-state retention and observed-state reconciliation
- deterministic inventory, placement, and variable generation
- provider and OS adapters
- modular Ansible content and repeatable runtimes
- durable evidence and explicit handoffs

A policy platform, catalog portal, writable CMDB, or enterprise workflow redesign is not required to prove these capabilities.

## Core design decisions

### Contract, manifest, workflow, and CMDB are different things

- **Contract** defines stable meaning, ownership, allowed values, gates, and interfaces.
- **Manifest** preserves approved intent and the latest phase projection for one build.
- **Workflow/request system** coordinates active work, concurrency, retries, and human actions.
- **CMDB discovery** records observed operational state after infrastructure becomes discoverable.

The manifest fills the pre-build and handoff-history gap. It should not be presented as a replacement CMDB.

### Windows and Linux should share the lifecycle

Approval, manifest creation, VMware provisioning, readiness, pause/resume, network integration, evidence, reconciliation, and handoff should be common.

Platform-specific content should be limited to supported images, connection behavior, OS configuration, reboot handling, and OS validation. If separate Windows and Linux workflows begin implementing their own status and handoff models, the POC has missed its reuse goal.

### VMware is an adapter, but a primary one

The environment is VMware-first, so placement and provisioning must be represented in the common contract. Vendor-specific module calls should remain behind an adapter role.

The current `vmware.vmware` collection includes VM, content-library deployment, power-state, guest-information, tagging, and inventory capabilities. The POC should select and pin collection versions only when the VMware adapter is implemented and tested against the organization's vCenter version.

### Object storage is an artifact layer, not the state machine

S3-compatible storage is well suited to request snapshots, manifests, event records, generated inputs, provider results, reconciliation, and final evidence.

It is not automatically well suited to:

- coordinating two writers
- querying active builds across many fields
- enforcing a workflow transition graph
- replacing a service catalog or relational report store

Use one active coordinator and a defined concurrency strategy. Build a search index or query service later only if object-prefix and metadata searches are insufficient.

## Problem-to-pattern fit

| Observed problem | Pattern to test | POC evidence |
| --- | --- | --- |
| Approved intent disappears into tickets and CSV | approval-triggered manifest plus snapshot | manifest revision 1 linked to approval |
| CMDB is discovery-only | desired/observed separation and reconciliation | handoff comparison artifact |
| Servers wait after a partial build | stage gates and explicit blocked state | safe state, blockers, owner, resume phase |
| Developers decide inventory and variables | owned mappings and generated inputs | deterministic output from the same manifest |
| Windows/Linux flows drift | common lifecycle with platform adapters | shared tests run against both profiles |
| VMware details leak into orchestration | provider adapter | mock and real provider share an interface |
| Shared folder/CSV tracking is slow | API-driven object artifacts | measured latency, history, and concurrency comparison |
| Automation cannot be shared | focused roles, documented interfaces, then collections | second consumer uses a role without copying it |
| Handoffs are chaotic | final snapshot and named next owner | readable completion/reconciliation record |

## Established practices supporting the direction

### Reusable Ansible content belongs in roles and collections

Ansible collections are the supported packaging boundary for related playbooks, roles, modules, and plugins. Red Hat COP guidance also supports focused roles, simple playbooks, and explicit inventory sources.

Practical interpretation:

- begin with focused repository-local roles
- define common interfaces before duplicating Windows and Linux behavior
- move stable reusable content into a versioned collection
- avoid creating a collection only to satisfy a diagram

### Collection testing has a defined path

The Ansible project documents `ansible-test` sanity, unit, and integration testing, including containerized execution.

Use lint, syntax checks, fixtures, and role assertions immediately. Add `ansible-test` when content becomes a collection and real integration tests when disposable targets exist.

### Execution environments support runtime parity

Execution environments and `ansible-navigator` support a common dependency model for Podman, Dev Spaces, CI, and AAP. Native Windows should not become the Ansible control-node standard.

### S3-compatible access is feasible but must be tested

The `amazon.aws.s3_object` module accepts an alternate `endpoint_url` and documents compatibility with several non-AWS services. Its documentation also warns that alternate S3-compatible services are not all tested by the collection.

The correct position is:

- a provider-neutral artifact-store interface
- local compatible service for development
- explicit compatibility tests against the on-premises endpoint
- no credentials or endpoints in manifests

### Versioning supports provenance

S3 versioning assigns versions to repeated writes of the same object key and can preserve prior variants. This supports a current-manifest projection with recoverable history.

Append-only lifecycle events are still valuable because raw object versions alone do not explain why a transition occurred.

### Mock-first integrations remain appropriate

VMware, Infoblox, object storage, and CMDB discovery should begin as deterministic fixtures or adapter simulations. Move one adapter at a time to a safe non-production system.

## Adopt now

1. One common server-build contract for Windows and Linux.
2. Manifest creation when a request is approved.
3. Request ID plus approval reference as the idempotency key.
4. Synthetic complete, blocked, invalid, retry, and mismatch manifests.
5. Explicit phases, blocked reason, safe state, next owner, and resume phase.
6. VMware placement and template inputs with owned mappings.
7. Desired-state and observed-state separation.
8. Local artifact layout matching an eventual S3 prefix layout.
9. Thin playbooks, focused roles, provider adapters, and OS adapters.
10. A purpose-built execution environment and minimal CI checks.

## Prove next

1. Can the same approved event be delivered twice without creating two builds?
2. Can Windows and Linux pass through one readiness evaluator?
3. Can every blocker report its expected source and owner?
4. Can a build pause and resume without reconstructing variables?
5. Can mappings deterministically select VMware template, cluster, storage policy, inventory, and role inputs?
6. Can manifest versions and append-only events survive retries and partial failures?
7. Can simulated VMware and CMDB values be reconciled with desired state?
8. Can local object storage outperform and out-trace a representative shared-folder/CSV flow?
9. Can the same tests run locally and in CI?

## Defer

- OPA or Conftest policy enforcement
- full ODCS conformance
- Backstage or another catalog portal
- enterprise-wide event-driven orchestration
- CMDB redesign or write integration
- controller configuration as code for every object
- multiple execution-environment families
- universal collection governance
- production promotion

## Realities the POC must not hide

### Approval events are often incomplete

Creating the manifest at approval is useful even when later fields are missing. The contract must distinguish what is mandatory to create the tracking record from what is mandatory to provision or hand off.

### A partial VMware build needs a defined safe state

The organization must decide whether a blocked VM is uncreated, powered off, isolated, attached to a staging network, or partially configured. It must also define access, expiration, cleanup, owner, and resume event.

Automation can otherwise make an unsafe waiting queue faster.

### Idempotence does not replace workflow state

Ansible idempotence helps repeated configuration converge. It does not record which external allocations completed or coordinate concurrent jobs. Manifest/event state and adapter-specific retry behavior are still required.

### Object versioning does not replace concurrency control

Versioning preserves overwritten variants. It does not by itself prevent two jobs from advancing the same build. The POC must test conditional writes or use a single active coordinator.

### Object storage does not remove the need for indexing

Object keys work well when consumers know the request ID. Leadership use cases such as “all blocked production Linux builds older than two days” may eventually require an index, inventory service, or analytics feed.

Do not reintroduce a manually maintained CSV as that index.

### CMDB reconciliation may be delayed

Discovery may lag handoff or omit fields. Reconciliation should distinguish mismatch from not-yet-observed and define which conditions block handoff.

### Windows and Linux testing need disposable targets eventually

Mocks prove lifecycle and adapter behavior. They cannot prove WinRM, SSH, reboots, guest customization, patching, domain/identity behavior, or OS idempotence.

### Extra vars are not governance

AAP surveys and extra vars transport values. Contracts, mappings, provenance, and override records establish authority.

## Provider-specific realities

### VMware

- Template compatibility must be tied to OS profile and vCenter capability.
- Clone completion is not the same as guest readiness.
- VM identity must use durable provider identifiers, not hostname alone.
- Partial clone/customization failures need cleanup or remediation behavior.
- Dynamic inventory can provide observed facts but should not overwrite approved intent.

### Infoblox

- A site and zone may have multiple eligible subnets.
- Allocation plus later metadata update can partially fail.
- Retry needs an atomic operation, compensating cleanup, or durable remediation record.

### S3-compatible storage

- Compatibility differs across vendors and versions.
- Versioning, retention, conditional writes, events, policies, certificates, and performance must be tested.
- Object metadata must not contain secrets or unnecessarily sensitive request data.
- Retention and deletion behavior must cover cancelled and expired builds.

## Organizational gaps to capture

- approved-request event source and payload owner
- system coordinating active lifecycle and concurrency
- owner and authoritative source for every input
- safe blocked state at each phase
- approved VMware placement and OS-template mappings
- manifest/evidence retention and access policy
- search/index requirements
- desired fields that must reconcile with discovery
- non-production VMware, Windows, Linux, IPAM, and S3-compatible targets
- reusable collection maintainers and release expectations
- AAP credential and environment boundaries

## Maturity checkpoints

### 1. Traceable creation

An approved request creates exactly one manifest and approval snapshot.

### 2. Visible readiness

Windows and Linux builds report actionable blockers and resume safely.

### 3. Deterministic VMware inputs

Approved facts and mappings generate repeatable placement, inventory, and variables.

### 4. Durable artifact history

Manifest versions, events, and evidence survive retries and can be retrieved by request ID.

### 5. Tested modular content

Common roles and OS/provider adapters have stable interfaces and expected-failure tests.

### 6. Controlled non-production integration

The same content runs through CI and AAP against disposable targets and the on-premises object service.

### 7. Wider governance

Evaluate policy engines, portals, cross-domain cataloging, and broader release governance based on observed needs.

## Reference sources reviewed

- [Red Hat COP Automation Good Practices](https://redhat-cop.github.io/automation-good-practices/)
- [Red Hat AAP 2.5 developing automation content](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/pdf/developing_automation_content/Red_Hat_Ansible_Automation_Platform-2.5-Developing_automation_content-en-US.pdf)
- [Ansible Navigator documentation](https://docs.ansible.com/projects/navigator/)
- [Developing Ansible collections](https://docs.ansible.com/projects/ansible/latest/dev_guide/developing_collections.html)
- [Testing Ansible collections](https://docs.ansible.com/projects/ansible/latest/dev_guide/developing_collections_testing.html)
- [vmware.vmware collection](https://docs.ansible.com/projects/ansible/latest/collections/vmware/vmware/index.html)
- [amazon.aws.s3_object module](https://docs.ansible.com/projects/ansible/latest/collections/amazon/aws/s3_object_module.html)
- [Amazon S3 versioning concepts](https://docs.aws.amazon.com/AmazonS3/latest/userguide/)
- [Open Data Contract Standard](https://github.com/bitol-io/open-data-contract-standard)
- [Infoblox NIOS modules collection](https://docs.ansible.com/projects/ansible/latest/collections/infoblox/nios_modules/index.html)

## Maintenance rule

Update this document whenever the POC proves, disproves, or qualifies an assumption. Move capabilities between `adopt now`, `prove next`, and `defer` as evidence changes.
