# Reference resources

This is the curated reading list behind Pipeline Playground. It favors Red Hat
Ansible Automation Platform documentation, Red Hat Community of Practice
guidance, and upstream Ansible documentation.

The Red Hat links below use AAP 2.5 because that is the current design baseline
for this POC. Before implementing controller objects, compare the guidance with
the version installed in the target environment.

## Start here

- [Red Hat AAP 2.5 documentation landing page](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5) -
  entry point for automation execution, decisions, content, APIs, and
  development guidance.
- [Developing automation content](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html-single/developing_automation_content/index) -
  Red Hat's create, test, and deploy workflow for playbooks, roles, collections,
  development tools, and execution environments.
- [Good Practices for Ansible](https://redhat-cop.github.io/automation-good-practices/) -
  field-oriented Red Hat Community of Practice guidance for content structure,
  role design, reuse, inventory, testing, and maintainability. Treat these as
  reasoned practices to adapt, not universal rules.

## AAP workflows and job execution

These resources support the logical workflow shown in this repository:
load a manifest, assess readiness, execute one short phase, persist evidence,
and exit. A later event or schedule launches the next short run.

- [Workflows in automation controller](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/controller-workflows) -
  workflow relationships, node behavior, branching, parallel jobs, and sharing
  values through `set_stats`.
- [Workflow job templates](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/controller-workflow-job-templates) -
  creation, surveys, visualizer behavior, scheduling, launching, and approval
  nodes.
- [Job templates](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/controller-job-templates) -
  reusable execution definitions for a playbook, inventory, credentials,
  execution environment, variables, limits, and launch behavior.
- [Schedules](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/controller-schedules) -
  controller scheduling for job templates, workflow templates, project syncs,
  and inventory sources. In this POC, schedules are most relevant to
  reconciliation, expiration, and stuck-build checks.
- [Projects](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/controller-projects) -
  source-control-backed playbook projects and synchronization.
- [Jobs in automation controller](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/controller-jobs) -
  runtime behavior, project copies, branch behavior, results, and job history.
- [Inventories](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/controller-inventories) -
  inventory organization and inventory sources. Pipeline Playground generates
  inventory inputs from approved facts and owned mappings instead of asking
  developers to improvise them.
- [Managing controller credentials](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/controller-credentials) -
  credential injection and delegation. Secrets belong in controller
  credentials, not contracts or manifests.
- [Automation controller best practices](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/assembly-controller-best-practices) -
  source control, project structure, inventory, credentials, and execution
  recommendations.
- [Automation execution API overview](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html-single/automation_execution_api_overview/index) -
  API entry point for launching and inspecting controller resources. This is a
  likely integration surface for an approved request system.

## Event-driven launches

Event-Driven Ansible is an optional maturity step, not a requirement for the
first pilot. A request system can also launch the workflow template directly
through the controller API.

- [Using automation decisions](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_decisions/index) -
  Event-Driven Ansible projects, decision environments, credentials, event
  streams, activations, and audit behavior.
- [Rulebook activations](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_decisions/eda-rulebook-activations) -
  rulebook sources, conditions, and actions, including launching job templates
  and workflow templates. Supported controller event sources include webhook,
  Kafka, queues, and other documented sources.

## Development environments and runtime parity

- [Using Ansible development workspaces](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html-single/using_ansible_development_workspaces_for_automation_content_development/index) -
  Red Hat guidance for Ansible development tools in OpenShift Dev Spaces.
  Verify the support or Technology Preview status for the installed AAP
  release.
- [Creating and using execution environments](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html-single/creating_and_using_execution_environments/index) -
  building, publishing, and using containerized Ansible runtimes.
- [Ansible Navigator](https://docs.ansible.com/projects/navigator/) -
  upstream documentation for running and inspecting automation with execution
  environments.
- [Molecule](https://ansible.readthedocs.io/projects/molecule/) -
  role and collection scenario testing. Every current repository role has a
  Molecule scenario.
- [Testing Ansible and collections](https://docs.ansible.com/projects/ansible/latest/dev_guide/testing_running_locally.html) -
  local sanity, unit, and integration test execution, including container
  environments and Podman.
- [Testing collections](https://docs.ansible.com/projects/ansible-core/devel/dev_guide/developing_collections_testing.html) -
  `ansible-test` guidance for content that has matured into a collection.

## Reusable automation content

- [Ansible collections](https://docs.ansible.com/collections.html) -
  the distribution format for playbooks, roles, modules, and plugins.
- [Developing collections](https://docs.ansible.com/projects/ansible/latest/dev_guide/developing_collections.html) -
  upstream collection layout, development, documentation, and distribution
  guidance.
- [VMware collection](https://docs.ansible.com/projects/ansible/latest/collections/vmware/vmware/index.html) -
  candidate supported modules for the future VMware adapter. Pin versions only
  after testing against the target vCenter version.
- [Infoblox NIOS modules collection](https://docs.ansible.com/projects/ansible/latest/collections/infoblox/nios_modules/index.html) -
  candidate modules for replacing the deterministic IPAM simulation.
- [S3 object module](https://docs.ansible.com/projects/ansible/latest/collections/amazon/aws/s3_object_module.html) -
  one possible implementation for an S3-compatible artifact adapter. Alternate
  endpoints require compatibility testing.

## Contracts, manifests, and artifact storage

- [Open Data Contract Standard](https://github.com/bitol-io/open-data-contract-standard) -
  a useful reference for data-product contracts and catalog interoperability.
  Full ODCS conformance is deferred; this POC uses only the concepts needed for
  automation inputs, ownership, compatibility, and gates.
- [Amazon S3 versioning concepts](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html) -
  background for retaining prior object variants. Versioning complements, but
  does not replace, append-only lifecycle events or concurrency control.
- [Pipeline Playground object-storage design](object-storage-artifacts.md) -
  repository-specific key layout, retention, security, and evaluation guidance.
- [Pipeline Playground reality check](reality-check.md) -
  maintained fit assessment, limitations, gaps, and maturity decisions.

## How the workflow resources map to the POC

| POC responsibility | AAP mechanism | Durable artifact |
| --- | --- | --- |
| Receive an approved request | API launch or optional EDA rulebook action | approved-event snapshot |
| Create or load tracking state | job template | manifest revision |
| Determine whether work can proceed | job template plus workflow branch data | readiness report and blockers |
| Execute one build phase | provider or OS job template | provider result and evidence |
| Record success, block, or retry | workflow success/failure/always path | new manifest revision and lifecycle event |
| Reconcile delayed observed state | scheduled job or workflow template | reconciliation report |
| Resume when data arrives | new API/event launch | retained revision and resume phase |

AAP is the coordinator in this model. The manifest and event artifacts remain
the portable record of approved intent and lifecycle evidence.
