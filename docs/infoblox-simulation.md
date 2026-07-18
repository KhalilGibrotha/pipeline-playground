# IPAM simulation

You do not need a real IPAM platform to prove the contract-driven workflow.

For the POC, the goal is to simulate the interaction contract:

1. input fields arrive from the build request
2. contract validation passes or fails
3. a provider-neutral network selector is derived
4. a subnet lookup is performed
5. an IP allocation response is returned
6. a host metadata write payload is produced

## What to simulate

The POC only needs three API-shaped behaviors:

- subnet lookup by network profile, site, environment, and data classification
- next available IP allocation
- host record / EA update

That is enough to validate the automation logic and failure handling.

## Recommended simulation levels

### Level 1: file-backed mock

Fastest path.

Use static JSON files to represent:

- subnet query result
- allocation result
- host update payload

This is enough to prove:

- contract-to-vars transformation
- branching logic
- failure messages

### Level 2: mock HTTP service

More realistic.

Run a tiny local API that returns IPAM-like responses for:

- `GET /api/network`
- `POST /api/network/<ref>/next_available_ip`
- `POST /api/record/host`

This is enough to prove:

- request construction
- response parsing
- error handling
- idempotency strategy

### Level 3: containerized integration harness

Best for later, not first.

Package the mock API and the Ansible content into a local podman-compose or Kubernetes demo so the same harness can run:

- on your workstation
- in Dev Spaces
- in CI

## What not to simulate yet

Skip these in the first pass:

- real DNS behavior
- real source-of-record write-back
- real observability integration
- production authentication and vault wiring
- multi-site IPAM topologies

They add complexity before the core model is proven.

## Suggested contract fields for the provisioning use case

The provisioning contract should carry only the fields needed to make and audit the decision:

- request identifier
- application identifier
- hostname
- site
- network profile
- environment
- data classification
- requested DNS domain
- operating system
- owner

The contract can also define which fields are:

- required inputs
- derived values
- write-back outputs

These fields belong to the network-services address-allocation contract. The
Infoblox adapter maps them to provider external attributes and objects. This
keeps provider vocabulary out of the server-build contract and makes a second
IPAM implementation possible without changing the domain interface.

## Failure cases worth simulating

At minimum, simulate these:

1. missing required field
2. invalid enum
3. no subnet returned
4. multiple candidate subnets returned
5. no available IP
6. host record write failure after allocation

Those cases will expose most of the architectural gaps early.

## POC recommendation

Start with Level 1 and Level 2 only.

That gives you enough realism to review:

- the contract shape
- the automation logic
- the failure model

without waiting for real infrastructure access.
