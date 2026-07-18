# Server-build process views

These views describe the same POC from different stakeholder perspectives. Each diagram answers a distinct question.

## 1. Executive view: from approval to accountable handoff

This view shows the outcome of the process without implementation detail.

```mermaid
flowchart LR
    A["Server request approved"] --> B["Tracking manifest created"]
    B --> C["Readiness evaluated"]
    C -->|Ready| D["VMware infrastructure provisioned"]
    C -->|Blocked| X["Missing data, owner, safe state, and resume phase recorded"]
    X --> C
    D --> E["Windows or Linux configured"]
    E --> F["Network and operational integrations completed"]
    F --> G["Desired and observed state reconciled"]
    G --> H["Handoff evidence retained"]
    H --> I["Operational ownership accepted"]
```

The important change is that waiting becomes an explicit, owned state instead of an informal queue hidden across tickets and CSV files.

## 2. Responsibility view: which system owns which part

This view prevents the manifest, object store, workflow engine, and CMDB from becoming competing sources of truth.

```mermaid
flowchart LR
    subgraph Intake["Request and approval"]
        A["Request system<br/>request + approval authority"]
    end

    subgraph Design["Versioned design-time sources"]
        B["Contract catalog<br/>fields + gates + interfaces"]
        C["Owned mappings<br/>profiles + placement + inventory"]
    end

    subgraph Coordination["Automation coordination"]
        D["AAP / workflow<br/>phase execution + retries + credentials"]
        E["Build manifest<br/>desired state + current projection"]
    end

    subgraph Providers["Provisioning and integration"]
        F["VMware adapter"]
        G["Windows adapter"]
        H["Linux adapter"]
        I["IPAM and operations adapters"]
    end

    subgraph Evidence["Observed state and history"]
        J["S3-compatible storage<br/>versions + events + evidence"]
        K["Discovery CMDB<br/>observed operational state"]
        L["Reconciliation and handoff"]
    end

    A --> D
    B --> D
    C --> D
    D <--> E
    D --> F
    F --> G
    F --> H
    G --> I
    H --> I
    E --> J
    F --> J
    I --> J
    E --> L
    K --> L
    J --> L
```

## 3. Artifact-lineage view: how intent survives the build

This view explains why the manifest and object-storage layer add value when the CMDB is discovery-only.

```mermaid
flowchart TD
    A["Approved request event"] --> B["Approval snapshot"]
    A --> C["Manifest revision 1<br/>approved intent"]
    D["Contract version"] --> C
    E["Mapping version"] --> C

    C --> F["Readiness report"]
    C --> G["Normalized inventory and variables"]
    C --> H["VMware result<br/>VM identity + placement"]
    C --> I["OS and integration results"]

    F --> J["Lifecycle events<br/>blocked + resumed + completed"]
    H --> K["Observed-state reconciliation"]
    I --> K
    L["CMDB discovery result"] --> K
    C --> K

    B --> M["Final handoff snapshot"]
    C --> M
    J --> M
    K --> M
    M --> N["Retained origin, outcome, discrepancies, and ownership transfer"]
```

The final snapshot is evidence of what was approved, what automation derived, what providers returned, and whether handoff succeeded.

## 4. Reuse view: one lifecycle, two operating-system adapters

This view shows where Windows and Linux should remain common and where divergence is legitimate.

```mermaid
flowchart TB
    A["Approved request"] --> B["Common manifest creation"]
    B --> C["Common readiness and blocker reporting"]
    C --> D["Common VMware placement and provisioning"]
    D --> E{"OS family"}

    E -->|Windows| F["Windows adapter<br/>WinRM + Windows baseline + reboot handling"]
    E -->|Linux| G["Linux adapter<br/>SSH + Linux baseline + reboot handling"]

    F --> H["Common integration orchestration"]
    G --> H
    H --> I["Common evidence and reconciliation"]
    I --> J["Common handoff contract"]
```

The reusable interface is the common outcome of each phase, not identical task implementation inside each operating system.

## 5. Development view: how content moves toward AAP

```mermaid
flowchart LR
    A["Developer<br/>WSL/Linux workstation or Dev Spaces"] --> B["Git branch and pull request"]
    B --> C["Fast checks<br/>YAML + fixtures + Ansible lint"]
    C --> D["Behavior tests<br/>Podman execution environment"]
    D --> E["Versioned role or collection artifact"]
    E --> F["Published execution environment"]
    F --> G["Non-production AAP"]
    G --> H["Disposable providers and targets"]
    H --> I["Promotion evidence"]
    I --> J["Controlled production release"]
```

Local Podman, CI, and AAP should consume the same dependency and content definitions even when credentials and target access differ.

## 6. AAP workflow view: one short build phase

This is the logical controller-level shape for a single phase. Job templates
remain small and reusable. The workflow branches on readiness, persists a
durable artifact, and exits rather than waiting for a human input.

```mermaid
flowchart LR
    T["Request API, EDA event, or schedule"] --> A["JT: load manifest"]
    A --> B["JT: assess readiness"]
    B -->|ready| C["JT: execute current adapter"]
    C --> D["JT: persist revision, event, and evidence"]
    B -->|blocked| E["JT: record blocker, owner, and resume phase"]
    E --> F["Controlled successful exit"]
    D --> G["Short workflow completes"]
    G -. "next event or reconciliation schedule" .-> A
```

Workflow success, failure, and always paths coordinate the jobs. They do not
replace the manifest and lifecycle events as the portable record of state.

## 7. Current-state execution view: the hidden control boundary

This view isolates the concern with `localhost`. Local API work is legitimate;
the problem is using the execution environment as a relay to an unmanaged
persistent execution layer.

```mermaid
flowchart LR
    A["AAP workflow and job template"] --> B["Execution environment<br/>play targets localhost"]
    B --> C["Persistent bastion or utility host<br/>scripts + libraries + working state"]
    C --> D["Monolithic playbook"]
    D --> E["VMware, inventory, and server targets"]

    C -. "state and retry context outside AAP" .-> F["Hidden execution boundary"]
    D -. "large failure domain" .-> F
```

## 8. Target execution view: governed placement and durable state

This view shows the two legitimate execution paths. API modules can run locally
inside the execution environment. Work that must run near segmented networks
can use registered automation mesh execution and hop nodes.

```mermaid
flowchart LR
    A["Approved event or resume trigger"] --> B["AAP workflow"]
    B --> C["Focused job template"]
    C --> D["Versioned execution environment"]
    D -->|API-oriented local work| E["VMware, IPAM, or service API"]
    D -->|segmented target work| F["Automation mesh<br/>hop + execution node"]
    F --> G["Windows or Linux target"]

    B <--> H["Manifest projection"]
    C --> I["Lifecycle event and evidence"]
    H --> J["S3-compatible artifact storage"]
    I --> J
```

The target is not that every play must name a remote host. The target is that
dependencies, credentials, targeting, execution placement, state, and evidence
have explicit owners and governed homes.

## 9. Provisioning decision view: wait as data or wait as infrastructure

This comparison explains why the manifest should be created before the VM while
VM creation normally waits for final network and placement readiness.

```mermaid
flowchart TB
    subgraph Current["Current temporary-infrastructure path"]
        A1["Request approved"] --> B1["Assign temporary IP"]
        B1 --> C1["Build VM in staging cluster"]
        C1 --> D1["Wait for final network and placement"]
        D1 --> E1["Readdress and relocate VM"]
        E1 --> F1["Configure and hand off"]
    end

    subgraph Target["Target readiness-gated path"]
        A2["Request approved"] --> B2["Create manifest"]
        B2 --> C2{"Final network and placement ready?"}
        C2 -->|No| D2["Persist blocker, owner, safe state, and resume phase"]
        D2 --> C2
        C2 -->|Yes| E2["Provision directly in target placement"]
        E2 --> F2["Configure, reconcile, and hand off"]
    end
```

If the organization requires a holding VM, model it as an explicit state with
isolation, expiry, cleanup, relocation testing, and reconciliation rather than
allowing the staging area to remain an accidental production dependency.
