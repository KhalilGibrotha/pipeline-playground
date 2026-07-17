# Toolchain

## Development environments

You currently have two practical environments:

1. OpenShift Dev Spaces at work
2. Local Windows workstation with Podman and Kubernetes

Use them for different purposes.

## Recommended split

### OpenShift Dev Spaces

Use this as the primary shared development environment when the work needs:

- parity with container and cluster controls
- collaboration with internal teams
- easier review of containerized automation content
- a path toward cluster-hosted validation or demo workflows

### Local Windows workstation

Use this for:

- editing contracts and docs
- fast local linting
- container build validation with Podman
- lightweight Kubernetes experiments when you want to test packaging patterns

Do not optimize the POC around Windows-native Ansible execution. Optimize around a consistent containerized developer toolchain that happens to be runnable from Windows.

## Recommended development model

### Authoring layer

- YAML contracts
- JSON Schema or OpenAPI-based schema definitions where appropriate
- Markdown architecture and gap documentation

### Validation layer

- YAML lint
- contract schema validation
- custom policy checks
- `ansible-lint`
- collection/playbook syntax checks

### Packaging layer

- execution environment image for repeatable tooling
- versioned generated artifacts
- optional collection packaging for shared automation logic

### Runtime layer

- automation controller project sync
- job template inputs from validated contract-derived artifacts
- workflow execution against non-production targets first

## Suggested repo layout

```text
catalog/
  contracts/
  schemas/
  policies/
ansible/
  playbooks/
  roles/
  collections/
  generated-vars/
execution-environment/
docs/
```

## Tooling baseline

Inside the execution environment and Dev Spaces workspace, install:

- ansible-core
- ansible-dev-tools
- ansible-lint
- yamllint
- jmespath
- jsonschema or an equivalent validator

Optional next additions:

- molecule
- pytest
- pre-commit
- opa or conftest if you want policy-as-code

## CI/CD shape for the POC

1. Pull request opened
2. Contract and schema validation runs
3. Policy checks run
4. Ansible lint and syntax checks run
5. Generated artifacts are built for review
6. Non-production AAP execution is triggered only for approved changes

## Practical recommendation

For the POC, keep one source repository and one execution environment image. That is enough to demonstrate:

- catalog structure
- validation flow
- generated automation inputs
- AAP-oriented development practices

Split repositories only if organizational boundaries require it later.
