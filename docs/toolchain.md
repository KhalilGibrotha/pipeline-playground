# Development toolchain

## Goal

Give an automation developer the same repeatable path from workstation to CI to AAP while keeping the first POC small enough to adopt.

The toolchain should prove that content is reviewable, testable, reusable, and packaged consistently. It does not need every enterprise control on day one.

## Development environments

### Windows workstation

Use the workstation for editing, Git, documentation, fixture development, and Podman-backed execution environments. Avoid making native Windows the Ansible control-node standard.

The intended local loop is:

1. edit a contract, manifest, role, or test
2. run fast lint and fixture tests
3. execute the playbook through the same execution-environment dependency set
4. inspect generated readiness and evidence artifacts
5. commit and open a pull request

Kubernetes is optional for this POC. It becomes useful only if a component genuinely needs a service or cluster deployment.

A local S3-compatible service is a valid first container experiment because it tests manifest keys, versions, events, and retries. It does not validate the enterprise endpoint's performance or compatibility.

### OpenShift Dev Spaces

Use Dev Spaces as the shared development environment when internal access and team collaboration are needed. The checked-in devfile should make the repository reproducible and give developers the same commands and dependencies.

Dev Spaces is especially useful for:

- access to internal registries and test systems
- consistent onboarding
- containerized Ansible development
- reviewing the workflow with other teams

It is not itself the CI system or the production AAP runtime.

## Toolchain layers

### Authoring

- Git and pull requests
- YAML and Markdown
- contract and build-manifest fixtures
- Visual Studio Code or the Dev Spaces editor

### Fast validation

- `yamllint`
- schema or purpose-built manifest validation
- `ansible-lint`
- `ansible-playbook --syntax-check`
- deterministic comparison of generated artifacts

Basic readiness validation belongs here. A general policy engine is deferred until real cross-contract policy needs appear.

### Behavior testing

- good, incomplete, and invalid build manifests
- duplicate approved-request events and manifest idempotency
- common Windows/Linux readiness scenarios
- mocked VMware, Infoblox, object-storage, and CMDB responses and failures
- role-level assertions for normalized inputs and readiness results
- artifact version, event, retry, and reconciliation checks
- idempotence checks when disposable Windows and Linux targets become available
- `ansible-test` sanity, unit, and integration tests after reusable content is packaged as a collection

Molecule can be evaluated for role scenarios, but it should not be introduced until it simplifies an actual test boundary.

### Packaging

- a small purpose-built execution environment
- pinned collection and Python dependencies
- versioned collection artifacts once shared content exists
- release notes and compatibility metadata for reusable content

Provider collections such as `vmware.vmware`, `amazon.aws`, `infoblox.nios_modules`, and the Windows/Linux content dependencies should be added only to the execution environment that implements those adapters, with versions pinned and tested together.

### Runtime and promotion

- local execution against mocks
- CI execution against fixtures
- non-production integration targets
- non-production AAP project and job template
- controlled promotion only after prior stages produce evidence

## Minimum pull-request checks

The first useful pipeline should run:

1. public-content and secret scan
2. YAML lint
3. contract/build-manifest validation
4. Ansible lint
5. syntax check
6. good-path fixture test
7. expected-failure fixture tests
8. generated-artifact comparison

Add execution-environment build validation after the content loop works. Add real VMware, object-storage, Windows, Linux, and other integration tests only when disposable non-production targets and credentials are available.

## Reuse progression

Do not require every role to begin in a separately released collection.

```text
repo-local role -> documented stable role -> collection content -> versioned shared release
```

Promotion to the next boundary should require:

- more than one credible consumer
- documented inputs and outputs
- tests for supported behavior
- a named maintainer
- compatibility and release expectations

This makes sharing achievable without turning the POC into a collection-governance program.

## Suggested first commands

```bash
yamllint .
python scripts/validate_manifest_fixtures.py
ansible-lint ansible/
cd ansible
ansible-playbook playbooks/test-manifest-creation.yml
ansible-playbook playbooks/mock-infoblox-provision.yml -e @vars/request-good.yml
```

Once an execution-environment image is available:

```bash
cd ansible
ansible-navigator run playbooks/mock-infoblox-provision.yml \
  -e @vars/request-good.yml \
  --mode stdout
```

## Adoption sequence

1. Make one POC developer path reproducible.
2. Add checks that protect the common server-build contract and mock flow.
3. Run the same checks in the organization's CI platform.
4. Demonstrate one non-production AAP execution.
5. Extract the first genuinely reusable role into a collection.
6. Standardize reusable pipeline templates only after the first repository exposes what is actually common.
