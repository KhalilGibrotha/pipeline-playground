# Pipeline Playground demo runbook

This runbook supports a short engineering demonstration of the POC. The
leadership overview establishes the why; the engineering walkthrough supplies
the implementation and test model. This runbook supplies the presenter
sequence. The goal is to show working evidence for a contained
automation-development pattern, not to simulate a finished enterprise platform.

## Audience takeaway

Incomplete integration data does not need to produce invisible work, improvised
variables, or long-running automation jobs. A durable build manifest, explicit
readiness checks, tested Ansible roles, and short AAP executions can make the
work traceable and safely resumable.

## Ten-minute sequence

### 1. Establish the operational problem

Use slides 1 and 2 of the leadership overview.

- approved requests can arrive before all downstream data exists
- build intent is fragmented across tickets, CSV files, shares, and inventory
- developers and handoff teams compensate for missing ownership and provenance

### 2. Show the approved request and contract

Use slide 3 of the engineering walkthrough.

Open these synthetic examples:

- `catalog/request-events/examples/windows-request-approved.yaml`
- `catalog/request-events/examples/linux-request-approved.yaml`
- `catalog/contracts/server-build/contract.yaml`
- `catalog/mappings/server-build-defaults.yaml`

Point out the separation between supplied request data, contract rules, and
owned mappings.

### 3. Create a manifest

From the repository root in PowerShell:

```powershell
$repo = (Get-Location).Path
$podman = "$env:LOCALAPPDATA\Programs\Podman\podman.exe"

& $podman run --rm `
  --env ANSIBLE_ROLES_PATH=/workspace/ansible/roles `
  --volume "${repo}:/workspace:Z" `
  --workdir /workspace/ansible `
  localhost/pipeline-playground-ee:dev `
  ansible-playbook playbooks/create-build-manifest.yml
```

Open the generated manifest under
`ansible/generated-vars/server-builds/requests/REQ-DEMO-0001/manifest.yaml`.
Show approval provenance, VMware placement, platform profile, derived inventory,
and the lifecycle status.

### 4. Demonstrate controlled failure and redelivery

Use slides 4 and 5 of the engineering walkthrough.

Run the blocked-to-ready lifecycle regression:

```powershell
& $podman run --rm `
  --env ANSIBLE_ROLES_PATH=/workspace/ansible/roles `
  --volume "${repo}:/workspace:Z" `
  --workdir /workspace/ansible `
  localhost/pipeline-playground-ee:dev `
  ansible-playbook playbooks/test-readiness-lifecycle.yml
```

Call out four results:

- The Windows build reports two network blockers with an accountable owner.
- The Linux build reports three operational blockers through the same role.
- Corrected values advance each manifest while preserving approved intent.
- A stale revision is rejected and a replayed event remains idempotent.

If time permits, run the original creation regression:

```powershell
& $podman run --rm `
  --env ANSIBLE_ROLES_PATH=/workspace/ansible/roles `
  --volume "${repo}:/workspace:Z" `
  --workdir /workspace/ansible `
  localhost/pipeline-playground-ee:dev `
  ansible-playbook playbooks/test-manifest-creation.yml
```

It additionally proves:

- Windows and Linux use the same manifest role.
- A duplicate approved event does not create another logical build.
- An incompatible OS family and version are rejected.

The expected failure is rescued by the test and should not be presented as an
unexpected test error.

### 5. Show the development quality gate

Use slide 7 of the engineering walkthrough.

Run one representative role scenario:

```powershell
& $podman run --rm `
  --volume "${repo}:/workspace:Z" `
  --workdir /workspace/ansible/roles/manifest_create `
  localhost/pipeline-playground-ee:dev `
  molecule test
```

Highlight syntax validation, first converge, zero-change idempotence, artifact
verification, and expected-failure coverage. Every current role has an
equivalent Molecule scenario.

### 6. Connect the evidence to the roadmap

Use leadership overview slides 4 through 8 to reconnect the evidence to the
operating model and pilot decision.

- AAP should execute short phases; it should not remain alive while people
  supply missing data.
- Readiness and pause/resume now work locally for both platform examples.
- Object storage, VMware, Windows, Linux, and Infoblox integrations are promoted
  one adapter at a time.
- The decision request is a focused pilot with one non-production integration
  and an evidence review before expansion.

## Demo prerequisites

- Podman machine running
- local image `localhost/pipeline-playground-ee:dev`
- repository checked out with synthetic fixtures
- PowerPoint brief available under `outputs/`

The preferred presentation assets are:

- `outputs/pipeline-playground-leadership-brief.pptx`
- `outputs/pipeline-playground-engineering-demo.pptx`

Build the local image when needed:

```powershell
& "$env:LOCALAPPDATA\Programs\Podman\podman.exe" build `
  --tag localhost/pipeline-playground-ee:dev `
  execution-environment
```

## No-runtime fallback

If Podman or a presentation environment is unavailable:

1. show the checked-in request and expected manifest examples
2. use `docs/process-views.md` for the lifecycle views
3. show the latest test evidence from the pull request
4. state clearly that the live runtime portion was not executed

## Reusing the pattern for another concept

Keep the same demonstration structure:

1. name one operational problem
2. define a stable input and output contract
3. create synthetic complete, incomplete, duplicate, and invalid examples
4. isolate unavailable systems behind deterministic adapters
5. implement focused Ansible roles with Molecule scenarios
6. run the same checks locally and in CI
7. promote one real non-production integration
8. retain evidence and record what remains unproved

This keeps future exercises comparable without forcing every concept into the
server-build data model.
