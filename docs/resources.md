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

## Execution ownership and network placement

These references support the distinction between legitimate local API work and
using a local job to launch an unmanaged persistent control layer.

- [Jobs in automation controller](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/controller-jobs) -
  each job receives a private project directory that is temporary and removed
  at the end of the run. Durable build state therefore belongs outside the job
  filesystem.
- [Execution environments](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/assembly-controller-execution-environments) -
  container images for the system-level dependencies and collection content
  required by a job.
- [Automation mesh node types](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/automation_mesh_for_managed_cloud_or_operator_environments/assembly-automation-mesh-operator-aap) -
  registered execution nodes run jobs and hop nodes transport traffic to
  otherwise unreachable execution nodes.
- [Instance and container groups](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/controller-instance-and-container-groups) -
  controller placement mechanisms for associating execution capacity with job
  templates, inventories, and organizations.
- [Controller credentials](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/controller-credentials) -
  managed credential injection, including documented jump-host patterns.
- [Delegation and local actions](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_delegation.html) -
  upstream guidance showing that local and delegated tasks are valid Ansible
  techniques. The architecture concern is where the true execution and state
  boundaries reside.

## Discovery, CMDB reconciliation, and inventory supply chains

These sources support the three-horizon pattern in
[Discovery-to-automation awareness](discovery-to-automation-awareness.md):
make the report-only path observable, publish a governed AAP inventory
projection, and later add automation as a reconciled CMDB source.

- [OpenText Universal Discovery and CMDB architecture](https://docs.microfocus.com/doc/UCMDB/24.4/Architecture) -
  the relationship between Universal Discovery, probes, infrastructure
  observations, and UCMDB.
- [OpenText Universal Discovery and CMDB glossary](https://docs.microfocus.com/doc/UCMDB/24.2/GlossaryCMS) -
  agent-based inventory collection and the distinction between discovery and
  CMDB capabilities.
- [TIBCO WebFOCUS ReportCaster guide](https://docs.tibco.com/pub/wf-wf/9.3.6/doc/pdf/IBI_wf-wf_9.3.6_reportcaster_guide.pdf?id=6) -
  scheduled report distribution options including FTP and SFTP. This supports
  a managed landing-zone pattern; it does not prove direct S3 delivery.
- [BMC Helix CMDB datasets](https://docs.bmc.com/xwiki/bin/view/Service-Management/IT-Service-Management/BMC-Helix-CMDB/ac254/Getting-started/Key-concepts/Datasets-to-partition-data/) -
  source-specific and staging datasets, production `BMC.ASSET`, and the
  explicit warning not to update the production dataset directly.
- [BMC Helix CMDB dataset best practices](https://docs.bmc.com/xwiki/bin/view/Service-Management/IT-Service-Management/BMC-Helix-CMDB/ac252/Administering/Managing-data-sources-and-datasets-in-BMC-Helix-CMDB/Best-practices-for-managing-datasets/) -
  one source per writable dataset and reconciliation into the production
  dataset.
- [BMC Helix CMDB reconciliation planning](https://docs.bmc.com/xwiki/bin/view/Service-Management/IT-Service-Management/BMC-Helix-CMDB/ac252/Planning/Planning-data-reconciliation/) -
  identification, merge, and source or attribute precedence across datasets.
- [BMC Helix CMDB REST API overview](https://docs.bmc.com/xwiki/bin/view/Service-Management/IT-Service-Management/BMC-Helix-CMDB/ac251/Developing/Using-BMC-Helix-CMDB-functions-in-an-external-application-with-the-REST-API/Learning-about-the-REST-API/Overview-of-the-REST-API/) -
  supported external create, search, update, retrieval, notification, and
  changed-CI capabilities. Permissions and reconciliation design remain local
  governance decisions.
- [AAP 2.5 inventories](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/controller-inventories) -
  inventory sources, schedules, `Update on launch`, and cache timeout behavior.
- [Automation controller best practices](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/using_automation_execution/assembly-controller-best-practices) -
  recommends a defined dynamic inventory synchronization process when an
  external CMDB is the source of truth.
- [Ansible dynamic inventory](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_dynamic_inventory.html) -
  inventory plugins and scripts for external sources.
- [Developing Ansible inventory plugins](https://docs.ansible.com/projects/ansible/latest/dev_guide/developing_inventory.html) -
  the plugin interface and optional inventory caching for a reusable adapter.
- [Ansible cache plugins](https://docs.ansible.com/projects/ansible/latest/plugins/cache.html) -
  caching mechanisms for inventory and facts when external retrieval is
  expensive.

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

## Catalog organization and contract design

These sources inform the repository's catalog model. Pipeline Playground does
not claim conformance with ODCS, Backstage, CloudEvents, or data mesh.

- [ODCS 3.1 fundamentals](https://bitol-io.github.io/open-data-contract-standard/v3.1.0/fundamentals/) -
  stable contract identity, version, status, logical domain, purpose, and
  authoritative definitions.
- [ODCS 3.1 definition](https://bitol-io.github.io/open-data-contract-standard/v3.1.0/) -
  the wider standard sections and its guidance that a contract should remain
  platform agnostic.
- [Backstage Software Catalog](https://backstage.io/docs/features/software-catalog/) -
  source-controlled YAML metadata, discoverable ownership, and owner-managed
  updates.
- [Backstage system model](https://backstage.io/docs/features/software-catalog/system-model/) -
  domains, systems, components, APIs, and resources as distinct catalog
  concepts.
- [Backstage entity references](https://backstage.io/docs/features/software-catalog/references/) -
  stable, fully qualified references between catalog entities.
- [Data Mesh Principles and Logical Architecture](https://martinfowler.com/articles/data-mesh-principles.html) -
  the original author's domain-ownership framing. This informs the heuristic
  "organize by who owns the meaning"; adopting data mesh is not a POC
  requirement.
- [CloudEvents specification](https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md) -
  event identity, source, type, time, duplicate handling, and interoperable
  event context. CloudEvents conformance is a possible later enhancement.
- [JSON Schema specification](https://json-schema.org/specification) -
  authoritative schema specification for a future machine-validation layer.

## Candidate integration contracts

These product sources support the premises and boundaries in
[Contract concept priorities and backlog](contract-concept-backlog.md).

### CMDB identification and reconciliation

- [BMC Helix CMDB datasets](https://docs.bmc.com/xwiki/bin/view/Service-Management/IT-Service-Management/BMC-Helix-CMDB/ac254/Getting-started/Key-concepts/Datasets-to-partition-data/) -
  source-owned datasets and reconciliation into the production dataset.
- [BMC Helix CMDB reconciliation planning](https://docs.bmc.com/xwiki/bin/view/Service-Management/IT-Service-Management/BMC-Helix-CMDB/ac252/Planning/Planning-data-reconciliation/) -
  identification, merge, and precedence across multiple providers.
- [ServiceNow IRE components and process](https://www.servicenow.com/docs/r/servicenow-platform/configuration-management-database-cmdb/c_CompsandProcessIDandReconcil.html) -
  identification, reconciliation, authoritative sources, duplicate handling,
  and the centralized API path.
- [ServiceNow Identification and Reconciliation API](https://www.servicenow.com/docs/r/api-reference/rest-apis/c_IdentifyReconcileAPI.html) -
  create/update and query endpoints that apply identification and
  reconciliation rules instead of bypassing them.

### F5 BIG-IP application delivery

- [F5 BIG-IP AS3 user guide](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/userguide/) -
  the declarative AS3 model and REST API.
- [Validating an AS3 declaration](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/userguide/validate.html) -
  published JSON Schema and pre-deployment validation.
- [AS3 per-application declarations](https://clouddocs.f5.com/products/extensions/f5-appsvcs-extension/latest/userguide/per-app-declarations.html) -
  tenant/application source-of-truth and update-scope behavior that an adapter
  must handle explicitly.

### Red Hat Satellite and target facts

- [Registering hosts to Satellite 6.18](https://docs.redhat.com/en/documentation/red_hat_satellite/6.18/html/managing_hosts/registering-hosts-to-satellite) -
  registration prerequisites, activation keys, host groups, content sources,
  and lifecycle/content-view selection.
- [Satellite 6.18 facts settings](https://docs.redhat.com/en/documentation/red_hat_satellite/6.18/html/administering_red_hat_satellite/administration_settings_admin#facts-settings) -
  how Satellite processes Puppet, Ansible, and RHSM facts and which host
  attributes facts can update.
- [Satellite 6.18 REST API](https://docs.redhat.com/en/documentation/red_hat_satellite/6.18/html-single/using_the_satellite_rest_api/index) -
  supported API version, host operations, and host-facts retrieval.

### Microsoft Configuration Manager

- [Deploy Configuration Manager clients to Windows](https://learn.microsoft.com/en-us/intune/configmgr/core/clients/deploy/deploy-clients-to-windows-computers) -
  supported client installation paths, site assignment, retries, and evidence
  sources.
- [Monitor Configuration Manager clients](https://learn.microsoft.com/en-us/intune/configmgr/core/clients/manage/monitor-clients) -
  client health and activity as a separately observed management state.
- [Configure hardware inventory](https://learn.microsoft.com/en-us/intune/configmgr/core/clients/manage/inventory/configure-hardware-inventory) -
  hardware-inventory profiles and scheduled client reporting.

### Synthetic networking data

- [RFC 5737 IPv4 address blocks for documentation](https://www.rfc-editor.org/rfc/rfc5737) -
  reserved example ranges used by the Infoblox simulation.

## Contracts, manifests, and artifact storage

- [Pipeline Playground data contract catalog solution](data-contract-catalog-solution.md) -
  domain-first hierarchy, ownership, artifact, adapter, and agent/facts
  boundaries used by this POC.
- [Pipeline Playground contract concept backlog](contract-concept-backlog.md) -
  prioritized CMDB, Satellite, Configuration Manager, VMware, F5, and
  operational-capability examples.
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
