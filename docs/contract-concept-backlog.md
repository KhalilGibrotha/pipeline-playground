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
| P1 | Discovery-to-AAP inventory supply chain | Removes avoidable report-processing delay while respecting report-only CMDB access | `inventory-source-export`, `inventory-snapshot`, `inventory-publication-result` |
| P1 | Desired/observed configuration-item reconciliation | Directly addresses the gap between approved pre-build intent and discovery-only operational state | `configuration-item-intent`, `configuration-item-observation`, `configuration-item-reconciliation-result` |
| P1 | Linux content and registration | Exercises independent agent registration, content policy, target facts, and Linux handoff evidence | `linux-content-registration-request`, `linux-content-registration-result`, `host-facts-snapshot` |
| P1 | Windows endpoint management | Gives Windows a parallel management-enrollment and observed-inventory pattern | `endpoint-enrollment-request`, `endpoint-enrollment-result`, `endpoint-health-snapshot`, `hardware-inventory-snapshot` |
| P2 | VMware provisioning interface | Replaces direct provider assumptions with explicit desired placement, operation result, and observed VM identity | `virtual-machine-provision-request`, `virtual-machine-provision-result`, `virtual-machine-observation` |
| P2 | F5 application delivery | Demonstrates a more complex multi-resource contract with virtual service, pool, monitor, TLS, ownership, and deployment evidence | `application-delivery-service-intent`, `application-delivery-deployment-result`, F5 AS3 adapter |
| P3 | Common operational capabilities | Tests reusable patterns after Satellite and endpoint management establish the boundary | monitoring, backup, security, certificate, directory, and decommission contracts |

P1 items can be designed in parallel, but the recommended implementation order
is the constrained inventory supply chain, CMDB reconciliation, then one Linux
and one Windows enrollment slice. That first removes avoidable latency inside
the automation boundary, then proves the desired-versus-observed model while
preserving Windows/Linux parity.

## Architecture-alignment milestone

Before adding the next domain example, the POC will align its contract,
validation, policy, identity, and presentation patterns. This milestone keeps
the existing server-build work as a proved baseline while replacing
POC-specific shortcuts with reusable implementation evidence.

| Order | Backlog item | Completion evidence | Dependency |
| --- | --- | --- | --- |
| A1 | Author the generic address-allocation contract in ODCS 3.1 | Valid ODCS source, pinned tool version, synthetic examples, and a short record of any required extensions or standard gaps | server-build POC baseline |
| A2 | Generate structural enforcement artifacts | Reproducible JSON Schema generation, fixture validation, and a CI drift check that fails when generated artifacts are stale | A1 |
| A3 | Correct the zero-trust placement inputs | Separate application lifecycle and network-zone environments, add traffic exposure, and derive `zone_<environment>_<classification>_<exposure>` from synthetic enums | A1 |
| A4 | Separate validation from mapping | Preflight only reads and rejects; a mapping or generation component owns derived values and has success and failure tests | A2, A3 |
| A5 | Flatten generated automation inputs | Ansible and inventory outputs use flat `snake_case` variables while durable manifests and event documents remain structured | A4 |
| A6 | Add one cross-field policy gate | A generic OPA/Rego policy has passing and failing fixtures and runs after structural validation in CI | A2, A3 |
| A7 | Formalize replay, reapproval, and concurrency | Tests cover exact replay, changed-payload identity conflicts, immutable approval evidence, manifest revisions, and conditional concurrent writes | A2 |
| A8 | Make review artifacts reproducible | Core documents have public-safe metadata and purpose statements; Quarto sources generate editable PowerPoint output from a committed reference template | independent after A1 |

The first implementation slice is A1 through A5: one ODCS-authored
address-allocation contract becomes a generated schema, accepts corrected
zero-trust inputs, and emits flat automation variables. A6 and A7 then prove
policy and lifecycle semantics without expanding into another provider or
business domain.

## Candidate 1: discovery-to-AAP inventory supply chain

Do not make the source report an implicit AAP inventory format. Separate:

- **inventory source export** — source/report identity, production time,
  delivery identity, checksum, schema version, and raw artifact reference
- **inventory snapshot** — accepted normalized records, observation times,
  stable identity, freshness, eligibility, and allowlisted targeting metadata
- **inventory publication result** — accepted/rejected counts, current
  projection, last-known-good decision, AAP synchronization result, and
  evidence references

The report adapter can be vendor-specific. The snapshot consumed by AAP should
not be. This permits a scheduled reporting extract today and a supported CMDB
query or changed-CI feed later without redefining every automation consumer.

Suggested POC:

1. Read a synthetic IBI/WebFOCUS-style CSV fixture.
2. Retain the immutable raw report with production and receipt times.
3. Validate schema, source age, identity, duplicates, and completeness.
4. Quarantine invalid input and retain the last-known-good projection.
5. Publish a deterministic Windows/Linux AAP inventory projection.
6. Test replay, partial transfer, stale input, identity collision, and
   inventory-sync failure.

The complete pattern is described in
[Discovery-to-automation awareness](discovery-to-automation-awareness.md).

## Candidate 2: configuration-item reconciliation

Do not create one giant `cmdb` contract. Separate:

- **configuration-item intent** — approved identity and selected desired values
- **configuration-item observation** — source, observed-at time, native
  identity, attributes, and relationships reported by discovery or another
  source
- **reconciliation result** — matches, differences, authority decisions,
  unresolved identities, and handoff disposition
- **CMDB adapter** — transforms the neutral representation to a supported
  source-dataset or identification-and-reconciliation interface
- **BMC Helix adapter** — writes an automation-owned source dataset and relies
  on CMDB identification and reconciliation rather than updating the
  production dataset directly
- **ServiceNow adapter** — transforms the neutral representation to an
  Identification and Reconciliation Engine payload

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

## Candidate 3: Red Hat Satellite and RHSM facts

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

## Candidate 4: Microsoft Configuration Manager

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

## Candidate 5: F5 BIG-IP application delivery

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
