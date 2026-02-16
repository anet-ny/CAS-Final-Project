# chat-room.ch 2.0 Visual Workflow Diagrams

## Gantt Chart (4.5 Month Timeline)

```mermaid
gantt
    title chat-room.ch 2.0 Project Timeline (18 Weeks)
    dateFormat  YYYY-MM-DD
    
    section Foundation
    Project Setup           :done, setup, 2026-03-01, 2w
    UX Wireframes          :done, ux1, 2026-03-01, 4w
    Core Architecture      :active, arch, 2026-03-15, 2w
    
    section Development
    Real-time Infrastructure :dev1, 2026-03-29, 4w
    Sensor Integration      :dev2, 2026-03-29, 4w
    Multimodal Translation  :dev3, 2026-04-19, 3w
    Integration Test 1      :crit, test1, 2026-05-10, 1w
    
    section AI & Features
    AI Moderator            :ai1, 2026-05-10, 4w
    Spatial Audio           :audio, 2026-05-24, 2w
    Mode-Constrained Tables :modes, 2026-06-07, 1w
    Privacy Architecture    :privacy, 2026-06-07, 1w
    
    section Polish & Testing
    Accessibility Hardening :access, 2026-06-14, 1w
    User Testing Round 1    :crit, testing, 2026-06-21, 2w
    Bug Fixes              :fixes, 2026-06-28, 1w
    
    section Launch & Paper
    Public Soft Launch      :crit, launch, 2026-07-05, 1w
    Data Analysis          :analysis, 2026-07-05, 2w
    Paper Completion       :paper, 2026-07-12, 1w
    
    section Paper (Parallel)
    Theory Framework       :done, paper1, 2026-03-01, 4w
    Design Challenges      :done, paper2, 2026-03-22, 2w
    Implementation Docs    :paper3, 2026-04-26, 4w
    Evaluation Methodology :paper4, 2026-05-31, 2w
    Results & Analysis     :paper5, 2026-06-21, 3w
    Final Writing          :paper6, 2026-07-12, 1w
```

## Workflow & Dependency Diagram

```mermaid
graph TB
    subgraph "PHASE 1: Foundation (Weeks 1-4)"
        A[Project Setup] --> B[UX Wireframes]
        B --> C[Design System v1]
        B --> D[Core Architecture]
        A --> E[Paper: Theory Framework ✓]
        A --> F[Sensor Prototype]
    end
    
    subgraph "PHASE 2: Development (Weeks 5-9)"
        C --> G[Web App: Real-time]
        D --> G
        F --> H[Sensor Integration]
        G --> I[Multimodal Translation]
        H --> I
        I --> J[Integration Test 1]
        E --> K[Paper: Design Challenges ✓]
    end
    
    subgraph "PHASE 3: AI & Advanced (Weeks 10-13)"
        J --> L[AI Moderator]
        J --> M[Spatial Audio]
        J --> N[Visual Features]
        L --> O[Mode Tables & Privacy]
        M --> O
        N --> O
        K --> P[Paper: Implementation Docs]
    end
    
    subgraph "PHASE 4: Testing (Weeks 14-16)"
        O --> Q[Accessibility Testing]
        Q --> R[User Testing Round 1]
        R --> S[Bug Fixes & Iteration]
        P --> T[Paper: Evaluation Methodology]
    end
    
    subgraph "PHASE 5: Launch & Analysis (Weeks 17-18)"
        S --> U[Public Soft Launch]
        U --> V[Data Collection]
        V --> W[Analysis & Writing]
        T --> W
        W --> X[Paper Complete ✓]
    end
    
    style A fill:#366092,stroke:#fff,color:#fff
    style J fill:#ff6b6b,stroke:#fff,color:#fff
    style O fill:#ff6b6b,stroke:#fff,color:#fff
    style R fill:#ff6b6b,stroke:#fff,color:#fff
    style U fill:#ff6b6b,stroke:#fff,color:#fff
    style X fill:#4ecdc4,stroke:#fff,color:#fff
    style E fill:#4ecdc4,stroke:#fff,color:#fff
    style K fill:#4ecdc4,stroke:#fff,color:#fff
```

## Work Package Ownership Map

```mermaid
graph LR
    subgraph "Core Team"
        PM[Project Manager<br/>Anet Nyffeler<br/>40h/wk]
        WD[Web Developer<br/>20h/wk]
        UX[UX Designer<br/>15h/wk]
        AI[AI Engineer<br/>10h/wk]
        IT[Installation Tech<br/>10h/wk]
    end
    
    subgraph "Specialists"
        ACC[Accessibility<br/>Consultant<br/>20h total]
        PART[Test Participants<br/>10-15 people]
    end
    
    PM --> WP1[1. Web Application]
    PM --> WP2[2. Physical Space]
    PM --> WP3[3. AI Moderator]
    PM --> WP4[4. Sensor Layer]
    PM --> WP5[5. UX Design]
    PM --> WP6[6. Journey Design]
    PM --> WP7[7. Scientific Paper]
    
    WD --> WP1
    WD --> WP4
    UX --> WP5
    UX --> WP6
    AI --> WP3
    IT --> WP2
    ACC --> WP5
    PART --> WP6
    
    style PM fill:#366092,stroke:#fff,color:#fff
    style WP1 fill:#D9E1F2
    style WP2 fill:#D9E1F2
    style WP3 fill:#D9E1F2
    style WP4 fill:#D9E1F2
    style WP5 fill:#D9E1F2
    style WP6 fill:#D9E1F2
    style WP7 fill:#4ecdc4,stroke:#fff,color:#fff
```

## Critical Path Analysis

```mermaid
graph TD
    START([Week 1<br/>Project Start]) --> CP1[UX Wireframes<br/>Weeks 1-4]
    CP1 --> CP2[Web App Core<br/>Weeks 3-6]
    CP2 --> CP3[Sensor Integration<br/>Weeks 5-8]
    CP3 --> CP4[Integration Test<br/>Week 9]
    
    CP4 --> CP5[AI Development<br/>Weeks 10-13]
    CP5 --> CP6[Feature Complete<br/>Week 13]
    CP6 --> CP7[User Testing<br/>Weeks 15-16]
    CP7 --> CP8[Soft Launch<br/>Week 17]
    CP8 --> END([Week 18<br/>Project Complete])
    
    %% Parallel paths
    START --> PP1[Paper Theory<br/>Weeks 1-4]
    PP1 --> PP2[Paper Challenges<br/>Weeks 3-4]
    PP2 --> PP3[Paper Implementation<br/>Weeks 9-13]
    PP3 --> PP4[Paper Evaluation<br/>Weeks 13-15]
    PP4 --> PP5[Paper Results<br/>Weeks 16-18]
    PP5 --> END
    
    START --> PH1[Physical Design<br/>Weeks 3-8]
    PH1 --> PH2[Equipment Setup<br/>Weeks 9-14]
    PH2 --> CP7
    
    style START fill:#366092,stroke:#fff,color:#fff
    style CP4 fill:#ff6b6b,stroke:#fff,color:#fff
    style CP6 fill:#ff6b6b,stroke:#fff,color:#fff
    style CP7 fill:#ff6b6b,stroke:#fff,color:#fff
    style CP8 fill:#ff6b6b,stroke:#fff,color:#fff
    style END fill:#4ecdc4,stroke:#fff,color:#fff
    style PP5 fill:#4ecdc4,stroke:#fff,color:#fff
```

## Risk Heat Map

```mermaid
quadrantChart
    title Risk Assessment Matrix
    x-axis Low Impact --> High Impact
    y-axis Low Probability --> High Probability
    quadrant-1 Monitor Closely
    quadrant-2 HIGH PRIORITY
    quadrant-3 Low Priority
    quadrant-4 Manage Carefully
    
    Browser Incompatibility: [0.65, 0.55]
    AI Latency: [0.45, 0.55]
    Accessibility Delays: [0.8, 0.75]
    Sensor Reliability: [0.5, 0.55]
    Recruitment Issues: [0.55, 0.55]
    Venue Availability: [0.85, 0.25]
    Paper Deadline Pressure: [0.75, 0.8]
```

## Weekly Sprint Cycle

```mermaid
graph LR
    A[Monday<br/>Standup] --> B[Development<br/>Tue-Thu]
    B --> C[Friday<br/>Demo & Review]
    C --> D[Weekend<br/>Planning]
    D --> A
    
    A -.-> E[Update Backlog]
    C -.-> F[Test & Document]
    D -.-> G[Prepare Sprint Goals]
    
    style A fill:#366092,stroke:#fff,color:#fff
    style C fill:#4ecdc4,stroke:#fff,color:#fff
```
