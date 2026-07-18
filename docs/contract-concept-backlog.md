# Contract concept priorities and backlog

## Intent

This document separates the contract concepts under discussion, prioritizes
what the POC should prove next, and records what belongs in the backlog. The
examples remain vendor-neutral at the contract boundary and use named
technologies as implementation adapters or authoritative reference points.

## Components parsed from the problem

1. **Catalog foundation** — stable IDs, domains, products, ownership,
   references, versions, and lifecycle status.
2. **Approved demand** — the event and approval evidence that authorize a
   tracking artifact to be created.
3. **Build coordination** — one Windows/Linux lifecycle, readiness gates,
   durable pause/resume state, and handoff.
4. **Desired intent** — the values approved before creation, including their
   source and decision owner.
5. **Provider integration** — request/result contracts independent of one API,
   plus adapters for VMware, Infoblox, or other products.
6. **Observed state** — facts reported by discovery, agents, hypervisors, or
   management systems.
7. **Reconciliation** — explicit comparison of desired intent and observed
   state without assuming either source owns every attribute.
8. **Operational enrollment** — registration and evidence for content,
   endpoint management, monitoring, backup, security, and similar capabilities.
9. **Publication and retention** — versioned manifests, events, results, facts,
   and handoff snapshots in durable storage.
10. **Development assurance** — schema checks, examples, role tests,
    integration simulations, and compatibility gates.

## Priority sequence

| Priority | Concept slice | Why it is next | Candidate contracts |
| --- | --- | --- | --- |
| P0 — implemented | Domain-first catalog foundation | Prevents provider names and aggregate manifests from owning unrelated meaning | domain, product, approved-request, build-lifecycle, build-manifest, address-allocation, Infoblox adapter |
| P1 | Desired/observed configuration-item reconciliation | Directly addresses the gap between approved pre-build intent and discovery-only operational state | `configuration-item-intent`, `configuration-item-observation`, `configuration-item-reconciliation-result` |
| P1 | Linux content and registration | Exercises independent agent registration, content policy, target facts, and Linux handoff evidence | `linux-content-registration-request`, `linux-content-registration-result`, `host-facts-snapshot` |
| P1 | Windows endpoint management | Gives Windows a parallel management-enrollment and observed-inventory pattern | `endpoint-enrollment-request`, `endpoint-enrollment-result`, `endpoint-health-snapshot`, `hardware-inventory-snapshot` |
| P2 | VMware provisioning interface | Replaces direct provider assumptions with explicit desired placement, operation result, and observed VM identity | `virtual-machine-provision-request`, `virtual-machine-provision-result`, `virtual-machine-observation` |
| P2 | F5 application delivery | Demonstrates a more complex multi-resource contract with virtual service, pool, monitor, TLS, ownership, and deployment evidence | `application-delivery-service-intent`, `application-delivery-deployment-result`, F5 AS3 adapter |
| P3 | Common operational capabilities | Tests reusable patterns after Satellite and endpoint management establish the boundary | monitoring, backup, security, certificate, directory, and decommission contracts |

P1 items can be designed in parallel, but the recommended implementation order
is CMDB reconciliation first, then one Linux and one Windows enrollment slice.
That produces an immediately useful desired-versus-observed story while
preserving Windows/Linux parity.

## Candidate 1: configuration-item reconciliation

Do not create one giant `cmdb` contract. Separate:

- **configuration-item intent** — approved identity and selected desired values
- **configuration-item observation** — source, observed-at time, native
  identity, attributes, and relationships reported by discovery or another
  source
- **reconciliation result** — matches, differences, authority decisions,
  unresolved identities, and handoff disposition
- **ServiceNow adapter** — transforms the neutral representation to an
  Identification and Reconciliation Engine payload if write access is later
  permitted

This split reflects a documented CMDB concern: identification determines
whether a CI is new or matches an existing CI, while reconciliation controls
which authoritative sources can update specific attributes. The contract
therefore needs source identity and attribute authority, not merely a flat
server record.

Suggested POC:

1. Read a final server-build manifest.
2. Read a synthetic discovery observation.
3. Match on explicit identity candidates.
4. Compare a small governed attribute set.
5. Emit a reconciliation result without writing a CMDB.
6. Gate handoff on required matches and explain acceptable differences.

## Candidate 2: Red Hat Satellite and RHSM facts

Treat Satellite as the adapter for a Linux content-management capability.
Model at least two boundaries:

- **registration request/result** — organization reference, activation-key
  reference, content-view environment, Capsule/content source where selected,
  target identity, registration status, provider reference, and timestamps
- **host facts snapshot** — host identity, source, collected-at time, fact-set
  version or hash, selected normalized facts, and a reference to the raw fact
  artifact

Red Hat documents activation keys as a registration mechanism that can select
content and content-view environments. Satellite also exposes host facts and
documents how uploaded facts can update host attributes. This means facts are
an observed evidence stream with their own source and collection time.

Answer to the agent question: the RHSM client does not need to become a
top-level domain merely because it is an agent. The Linux profile references a
content-management capability. That capability owns registration and facts
contracts because it has an independent owner, identity, lifecycle, provider
API, and handoff evidence.

## Candidate 3: Microsoft Configuration Manager

Treat Microsoft Configuration Manager as the adapter for a Windows
endpoint-management capability. Candidate boundaries are:

- **enrollment request/result** — target identity, desired site assignment,
  management profile reference, installation method classification, client
  identity, status, and evidence
- **client health snapshot** — client activity, health-evaluation time,
  management point or site identity, and remediation disposition
- **hardware inventory snapshot** — source, collection time, inventory schema
  profile, selected normalized attributes, and raw artifact reference

Microsoft documents multiple client deployment methods, client health/status
monitoring, and scheduled hardware inventory sent by the client. Those are
separate desired, result, and observed boundaries; folding them into the
generic Windows server contract would hide ownership and refresh behavior.

## Candidate 4: F5 BIG-IP application delivery

The domain contract should express an application-delivery service, not an AS3
payload:

- application and environment identity
- virtual service addresses and ports
- protocol and TLS intent
- pool members or a reference to the member source
- health-monitor intent
- DNS and certificate dependencies
- owner, maintenance, and rollback expectations
- deployment result, provider reference, validation result, and observed state

F5 AS3 is a strong adapter target because F5 documents a declarative model,
publishes JSON schemas, and supports schema validation before deployment. AS3
also has tenant and per-application update semantics that must be made explicit
in the adapter to avoid unintended replacement or deletion behavior.

This is a valuable complex example after server and integration identity,
replay, and reconciliation patterns are established.

## Agent and fact decision rule

Use this test for monitoring, backup, endpoint-management, subscription,
security, or other agents:

| Question | If yes |
| --- | --- |
| Does another team own the capability's meaning or lifecycle? | Create a capability-owned contract |
| Is there independent registration, identity, retry, upgrade, or removal? | Create request/result contracts |
| Does it emit observations on its own schedule? | Create a facts or evidence contract |
| Is the capability reused across OS or build products? | Reference it from profiles rather than nesting it |
| Is it only a local package/service choice with no independent interface? | Keep it in the OS profile |

An agent binary is an implementation detail. Its registration and evidence can
still be important contract boundaries.

## Backlog concepts

| Concept | Contract shape to explore | Dependency |
| --- | --- | --- |
| VMware | provision request/result plus observed VM identity and placement | current server lifecycle |
| DNS and certificates | record/certificate intent, issuance result, renewal evidence | address allocation |
| Directory services | domain-join intent/result and computer-object evidence | Windows/Linux configuration |
| Monitoring | enrollment request/result and telemetry-health evidence | agent pattern |
| Backup | protection intent, enrollment result, restore-readiness evidence | agent pattern |
| Security tooling | enrollment and policy-assignment result without embedding sensitive policy | agent pattern and security review |
| Software repositories | repository entitlement intent and observed availability | Satellite slice |
| Patch compliance | desired baseline reference and observed compliance result | Satellite/MECM slices |
| Decommission | revoke integrations, release address, retire CI, and retain final evidence | all provider result contracts |
| Contract registry | schema publication, compatibility, signatures, and discoverability | stable POC contract metadata |

## Definition of ready for a new example

An example is ready to enter the implemented POC when:

- a meaning-owning domain and accountable reviewer are identifiable
- official documentation supports the provider behavior being modeled
- producer, consumer, identity, lifecycle, and failure semantics are bounded
- no production data or internal identifiers are required
- a deterministic success case and at least two meaningful failures can be
  simulated
- the contract can be tested without production connectivity
- the result adds a reusable pattern rather than only another vendor payload

## Authoritative references

The official sources supporting these premises are cataloged in
[Reference resources](resources.md), under **Catalog organization and contract
design** and **Candidate integration contracts**.
