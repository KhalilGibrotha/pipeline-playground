# Server-build automation anti-patterns

This document captures two current-state patterns that the POC is intended to
challenge. The examples are intentionally generic. They describe architecture
risks and transition options without assuming that a particular product,
network, or team is at fault.

## 1. Shadow execution behind `localhost`

### Current pattern

An AAP job targets `localhost` inside its execution environment. The job then
connects to a persistent bastion or utility host and launches a larger
playbook, script, or inventory process there.

The persistent host compensates for the fact that an AAP job's private project
directory is temporary. Over time, the host can become an unofficial control
node that owns libraries, scripts, working files, retry context, and network
reach.

### Why this is risky

- AAP records the outer job but does not fully represent the true execution
  boundary.
- Dependencies and mutable state can drift outside the versioned execution
  environment.
- Inventory, credentials, targeting, and network access become harder to
  review through controller resources.
- A monolithic playbook creates a large retry and failure domain.
- Recovery depends on knowledge and files retained on one persistent host.
- Platform features such as job-template boundaries, workflow branching,
  execution placement, and reusable content provide less value.

### Important distinction

`localhost` is not inherently an anti-pattern. Local execution is appropriate
when an API-oriented module runs inside the execution environment and the job
still uses managed dependencies, controller credentials, explicit inputs, and
durable result artifacts.

The anti-pattern begins when local execution is only a launcher for an
unmanaged persistent execution layer.

### Target pattern

- Package collections, Python libraries, and system dependencies in a
  versioned execution environment.
- Use focused job templates for lifecycle phases rather than one monolithic
  build job.
- Keep inventories, credentials, limits, and execution placement visible in
  AAP.
- Use API modules locally inside the execution environment when that is the
  correct connection model.
- Use automation mesh execution nodes and hop nodes when jobs must run near
  segmented target networks.
- Store build state, blockers, revisions, and evidence in the manifest and
  artifact store instead of on an execution host.
- Return provider results and lifecycle events to the governed job boundary.

Automation mesh is not a reason to preserve the shadow host unchanged. An
execution node is registered, scheduled, and observed by AAP; a hop node
transports mesh traffic. Neither should become an informal state store.

## 2. Provisioning before final placement is ready

### Current pattern

A VM is created in a sandbox or staging cluster with temporary network values.
The build waits for final IP or placement data, then mutates network settings
and relocates the VM into the target VMware cluster.

The temporary path becomes a mandatory part of the production delivery
process. A patch, network change, permission change, or staging-cluster failure
can therefore stop unrelated server builds.

### Why this is risky

- A temporary environment becomes a critical production dependency.
- Readdressing and relocation increase the number of non-atomic operations.
- A partial failure can leave IPAM, DNS, VMware, guest networking, inventory,
  and the manifest describing different states.
- The workflow needs cleanup and recovery behavior for more intermediate
  states.
- The reason a build is waiting can remain hidden inside infrastructure rather
  than represented as owned data.
- Troubleshooting becomes coupled to the historical state of the staging area.

### Preferred target pattern

Create the manifest when the request is approved, but gate VM creation on the
minimum data required for final placement:

```text
approved request
  -> manifest created
  -> placement and network readiness evaluated
     -> blocked: persist missing data, owner, safe state, and resume phase
     -> ready: provision directly in the target cluster and network
  -> configure operating system and integrations
  -> reconcile and hand off
```

The approved request can therefore exist and progress without requiring a
half-built VM to act as the tracking artifact.

### If a holding VM is unavoidable

Treat the holding state as a deliberate product capability, not an incidental
workaround. Define and test:

- isolation and permitted access
- temporary addressing and authoritative ownership
- expiration and automated cleanup
- supported relocation and guest-network reconfiguration
- idempotent retry and compensating actions
- the lifecycle event that resumes the build
- reconciliation across VMware, IPAM, DNS, guest state, and discovery

## Transition sequence

1. Inventory the scripts, libraries, credentials, files, and network paths
   currently owned by the shadow execution host.
2. Split the monolithic playbook into observable lifecycle phases.
3. Move dependencies into an execution environment.
4. Externalize manifest state and evidence to durable storage.
5. Represent targeting, credentials, and execution placement in AAP.
6. Gate provisioning on final placement readiness.
7. Pilot one non-production workflow and compare recovery, traceability, and
   delivery time with the current path.

## Evidence to collect

- percentage of build work visible as AAP job-template nodes
- dependencies removed from the persistent utility host
- number of manual inventory and variable decisions
- blocked builds with a named owner and resume condition
- retries completed without reconstructing state from files or operator memory
- VMs created directly in final placement
- discrepancies detected during VMware, network, guest, and CMDB reconciliation
- mean time to identify the failed phase and accountable owner

## Related authoritative guidance

- [Jobs in automation controller](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/controller-jobs)
- [Job templates](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/controller-job-templates)
- [Execution environments](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/assembly-controller-execution-environments)
- [Automation mesh node types](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/automation_mesh_for_managed_cloud_or_operator_environments/assembly-automation-mesh-operator-aap)
- [Controller credentials](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/controller-credentials)
- [Ansible delegation and local actions](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_delegation.html)
