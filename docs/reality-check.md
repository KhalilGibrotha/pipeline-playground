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
- **Discovery source** records observed operational state after infrastructure becomes discoverable.
- **CMDB reconciliation** identifies and merges governed source records into the production CI.
- **AAP inventory** is a consumer-specific targeting projection, not a replacement CMDB.

The manifest fills the pre-build and handoff-history gap. It should not be presented as a replacement CMDB.

An ideal CMDB integration does not require automation to overwrite discovered
facts or update a production dataset directly. Build automation can own an
approved-intent and handoff source dataset while discovery owns runtime
observations. Identification and reconciliation rules decide how those sources
contribute to the production CI.

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

### AAP should own the visible execution boundary

Running API-oriented tasks against `localhost` inside an execution environment
is valid. The anti-pattern is using that local job only to launch a persistent
host that owns the real scripts, dependencies, state, targeting, and retry
context.

Dependencies belong in a versioned execution environment. Inventory,
credentials, limits, job history, and execution placement should remain visible
through AAP resources. When network segmentation requires execution closer to
targets, evaluate registered automation mesh execution and hop nodes rather
than preserving an unmanaged shadow control node.

### Inventory should be synchronized as a governed projection

Red Hat documents project-backed and custom inventory sources, scheduled
synchronization, `Update on launch`, and cache timeout behavior. It also
recommends a defined dynamic inventory synchronization process when an external
CMDB is the source of truth.

If CMDB access is restricted to a scheduled reporting extract, modernize the
adapter behind that boundary: land the report once, retain the raw snapshot,
validate identity and freshness, publish a versioned inventory projection, and
synchronize it through an AAP inventory source. Server-automation jobs should
not parse the report.

This removes avoidable post-report delay. It does not improve the source
observation, CMDB reconciliation, or report-production cadence.

### CMDB writes should use source datasets and reconciliation

BMC Helix CMDB documents source-specific datasets and warns against direct
updates to the production dataset. Its Reconciliation Engine identifies and
merges records according to source and attribute precedence.

The ideal pattern is therefore an automation-owned source or staging dataset
for approved intent, build completion, and handoff evidence. Discovery remains
authoritative for observed runtime facts. Production CI changes flow through
the supported identification and reconciliation boundary.

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
| CMDB data reaches AAP through a delayed report chain | immutable report landing, validation, versioned inventory projection, and controller inventory sync | post-report latency, source age, rejection, and AAP sync measures |
| AAP launches a persistent shadow control node | versioned EE, focused job templates, governed execution placement, durable artifacts | dependencies removed from utility host and phase results visible in AAP |
| VM is built with temporary IP and placement, then moved | gate creation on final network and placement readiness | blocked request remains durable without requiring a half-built VM |
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

The POC now runs a Molecule scenario for every repository-local role. The
artifact-processing scenarios use a delegated Linux instance and prove syntax,
expected behavior, expected failures, deterministic artifacts, and idempotence
inside the Podman execution environment. This is meaningful coverage for the
current roles, but it does not substitute for disposable VMware, Windows, or
Linux targets when provider and operating-system roles are added.

### Execution environments support runtime parity

Execution environments and `ansible-navigator` support a common dependency model for Podman, Dev Spaces, CI, and AAP. Native Windows should not become the Ansible control-node standard.

AAP job project directories are temporary and removed after the job. That is a
reason to package dependencies in the execution environment and retain
business state in durable artifacts; it is not a reason to create an
unmanaged persistent control node.

### Automation mesh supports governed network placement

AAP can schedule work on registered execution nodes and use hop nodes to reach
otherwise inaccessible execution nodes. This provides an explicit platform
boundary for segmented networks. A hop node transports mesh traffic, while an
execution node runs jobs; neither should become an informal store for build
state or unversioned automation content.

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

### Domain-first cataloging is useful but does not create ownership

The repository now follows the rule: **Organize by who owns the meaning;
classify by how it is implemented.** Approved demand, server-build lifecycle,
and address allocation are separate domain contracts. Infoblox is an adapter
for the provider-neutral address-allocation contract.

This structure improves discoverability and prevents provider payloads from
becoming accidental enterprise interfaces. It does not decide who the real
organizational owners are. A production pilot still needs named reviewers,
change expectations, support boundaries, and an authoritative source for each
field.

### Readiness and pause/resume are now proved locally

The POC now demonstrates one common evaluator for Windows and Linux. It reports
all missing values with source and decision owner, records a safe blocked state,
retains the manifest `spec`, and resumes from a corrected revision.

The lifecycle role also rejects a stale revision and treats a replayed event ID
as idempotent. This proves the local artifact semantics; it does not yet prove
distributed concurrency or object-store conditional writes.

## Adopt now

1. Domain-first catalog organization with one accountable meaning owner per contract.
2. Manifest creation when a request is approved.
3. Request ID plus approval reference as the idempotency key.
4. Synthetic complete, blocked, invalid, retry, and mismatch manifests.
5. Explicit phases, blocked reason, safe state, next owner, and resume phase.
6. VMware placement and template inputs with owned mappings.
7. Desired-state and observed-state separation.
8. Local artifact layout matching an eventual S3 prefix layout.
9. Thin playbooks, focused roles, provider adapters, and OS adapters.
10. A purpose-built execution environment, mandatory role-level Molecule scenarios, and minimal CI checks.
11. Explicit criteria for legitimate local API work versus managed remote execution.
12. Final-placement readiness before VM creation unless a governed holding state is intentionally approved.
13. Provider-neutral integration contracts with named implementation adapters.
14. AAP inventory as a freshness-governed projection of an external source, not a report-processing side effect.
15. Separate source-observation, report-production, ingestion, publication, and inventory-sync timestamps.

## Prove next

1. Can a synthetic reporting extract be landed once, validated, versioned, and synchronized into AAP without a shadow host or shared-folder working state?
2. Can manifest versions and append-only events survive object-store retries, conditional writes, and partial failures?
3. Can a provider-neutral VMware request/result interface retain durable VM identity and placement evidence?
4. Can synthetic CMDB observations be reconciled with approved intent and attribute authority?
5. Can Satellite/RHSM and Configuration Manager prove parallel Linux/Windows enrollment and facts patterns?
6. Can local object storage outperform and out-trace a representative shared-folder/CSV flow?
7. Can one monolithic shadow-host path be split into observable AAP workflow phases?
8. Can a build remain blocked as a manifest without creating a temporary VM?
9. Can contract changes be checked for consumer compatibility before promotion?

## Defer

- OPA or Conftest policy enforcement
- full ODCS conformance
- Backstage or another catalog portal
- enterprise-wide event-driven orchestration
- production CMDB write integration before source ownership, identity, and reconciliation rules are approved
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

The preferred default is to create the manifest at approval and wait to create
the VM until final placement and network data are ready. If a staging VM is
unavoidable, relocation and readdressing become supported lifecycle
transitions that require compatibility tests, reconciliation, expiry, and
cleanup behavior.

### Ephemeral jobs do not justify a shadow control node

AAP intentionally gives each job a temporary private project directory.
Durable request state, generated inputs, and evidence must therefore live in
an artifact service. Runtime dependencies should live in the execution
environment. Moving both concerns to a persistent utility host hides them from
the platform rather than solving them.

### Idempotence does not replace workflow state

Ansible idempotence helps repeated configuration converge. It does not record which external allocations completed or coordinate concurrent jobs. Manifest/event state and adapter-specific retry behavior are still required.

### Object versioning does not replace concurrency control

Versioning preserves overwritten variants. It does not by itself prevent two jobs from advancing the same build. The POC must test conditional writes or use a single active coordinator.

### Object storage does not remove the need for indexing

Object keys work well when consumers know the request ID. Leadership use cases such as “all blocked production Linux builds older than two days” may eventually require an index, inventory service, or analytics feed.

Do not reintroduce a manually maintained CSV as that index.

### CMDB reconciliation may be delayed

Discovery may lag handoff or omit fields. Reconciliation should distinguish mismatch from not-yet-observed and define which conditions block handoff.

### A faster adapter cannot outrun a delayed report

A report-only inventory adapter can remove downstream file-copying and parsing
delay, but it cannot make the source report fresher. The POC must measure
observation age, report age, ingestion time, and AAP publication time
separately. “Near real time” is not a valid claim unless the upstream
production cadence changes.

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
- The provider adapter must not redefine network-profile, site, environment, or data-classification meaning.

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
- approved uses of local execution and delegation
- automation mesh execution-node and hop-node requirements
- dependencies and state currently retained on bastion or utility hosts
- minimum network and placement facts required before VM creation
- reporting-extract schema owner, delivery cadence, completion signal, and support boundary
- stable identity carried across discovery, CMDB, reporting, VMware, and AAP
- inventory freshness objectives and fail-open/fail-closed rules by automation class
- source-dataset ownership and attribute precedence for any future CMDB write path

## Maturity checkpoints

### 1. Traceable creation

An approved request creates exactly one manifest and approval snapshot.

### 2. Visible readiness

Proved locally with synthetic Windows network and Linux operations blockers.
Non-production provider safe states still require organizational validation.

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
- [Jobs in automation controller](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/controller-jobs)
- [Job templates](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/controller-job-templates)
- [Execution environments](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/assembly-controller-execution-environments)
- [Automation mesh node types](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/automation_mesh_for_managed_cloud_or_operator_environments/assembly-automation-mesh-operator-aap)
- [Ansible delegation and local actions](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_delegation.html)
- [Ansible Navigator documentation](https://docs.ansible.com/projects/navigator/)
- [Developing Ansible collections](https://docs.ansible.com/projects/ansible/latest/dev_guide/developing_collections.html)
- [Testing Ansible collections](https://docs.ansible.com/projects/ansible/latest/dev_guide/developing_collections_testing.html)
- [vmware.vmware collection](https://docs.ansible.com/projects/ansible/latest/collections/vmware/vmware/index.html)
- [amazon.aws.s3_object module](https://docs.ansible.com/projects/ansible/latest/collections/amazon/aws/s3_object_module.html)
- [Amazon S3 versioning concepts](https://docs.aws.amazon.com/AmazonS3/latest/userguide/)
- [Open Data Contract Standard](https://github.com/bitol-io/open-data-contract-standard)
- [Infoblox NIOS modules collection](https://docs.ansible.com/projects/ansible/latest/collections/infoblox/nios_modules/index.html)
- [OpenText Universal Discovery and CMDB architecture](https://docs.microfocus.com/doc/UCMDB/24.4/Architecture)
- [TIBCO WebFOCUS ReportCaster guide](https://docs.tibco.com/pub/wf-wf/9.3.6/doc/pdf/IBI_wf-wf_9.3.6_reportcaster_guide.pdf?id=6)
- [BMC Helix CMDB dataset best practices](https://docs.bmc.com/xwiki/bin/view/Service-Management/IT-Service-Management/BMC-Helix-CMDB/ac252/Administering/Managing-data-sources-and-datasets-in-BMC-Helix-CMDB/Best-practices-for-managing-datasets/)
- [BMC Helix CMDB reconciliation planning](https://docs.bmc.com/xwiki/bin/view/Service-Management/IT-Service-Management/BMC-Helix-CMDB/ac252/Planning/Planning-data-reconciliation/)
- [AAP 2.5 inventories](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/controller-inventories)
- [Developing Ansible inventory plugins](https://docs.ansible.com/projects/ansible/latest/dev_guide/developing_inventory.html)
- [Pipeline Playground catalog and integration references](resources.md#catalog-organization-and-contract-design)

## Maintenance rule

Update this document whenever the POC proves, disproves, or qualifies an assumption. Move capabilities between `adopt now`, `prove next`, and `defer` as evidence changes.
