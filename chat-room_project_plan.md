# chat-room.ch 2.0 Project Plan
## 4.5 Month Timeline (March – Mid-July 2026)

---

## Work Breakdown Structure (WBS)

### 1. Web Application (Real-time Platform)
**Owner:** Web Developer + Designer  
**Deliverables:**
- Real-time communication infrastructure (WebRTC, WebSocket)
- Table management system (join/leave, user tracking)
- Configuration panel UI
- Modality labeling system
- Screen reader accessibility layer
- Spatial audio API integration (binaural rendering)

**Key Technologies:** Node.js/Express, Socket.io, Web Audio API, React/Vue

---

### 2. Physical Installation (Pop-up Space)
**Owner:** Installation Designer + Technical Support  
**Deliverables:**
- Spatial audio setup (4-6 speakers positioned by table)
- Display screens for remote participant traces
- Physical table layout design
- Lighting and ambient atmosphere
- Power and network infrastructure
- Accessibility considerations (wheelchair access, clear pathways)

**Key Technologies:** Multi-channel audio interface, projectors/screens, spatial audio processing

---

### 3. AI Moderator & Interpreter
**Owner:** AI/ML Engineer + Interaction Designer  
**Deliverables:**
- Conversation monitoring logic (silence, domination detection)
- Modality-neutral intervention system
- Meta-conversational prompt generation
- Real-time translation summaries
- Tutorial AI for practice table
- Integration with web app via API

**Key Technologies:** Python (Claude API, GPT-4), custom monitoring algorithms, WebSocket integration

---

### 4. Sensor & Input Layer
**Owner:** Mobile/Sensor Developer  
**Deliverables:**
- Smartphone sensor access (gyroscope, accelerometer, mic)
- Tap/rhythm detection
- Motion-to-sound mapping
- Breath/sustained input detection (mic-based)
- Text and voice input normalization
- Cross-browser/device compatibility testing

**Key Technologies:** JavaScript Device APIs, Web Audio API, getUserMedia API

---

### 5. UX/UI Design (Cross-Modal Flows)
**Owner:** UX Designer + Accessibility Specialist  
**Deliverables:**
- User flow diagrams (onboarding → participation → exit)
- Wireframes and prototypes
- Modality labeling visual language (icons, colors)
- Configuration panel design
- Tutorial/practice table flow
- Screen reader navigation structure
- Visual overlap map (Venn-style)

**Key Tools:** Figma/Sketch, accessibility testing tools (NVDA, JAWS)

---

### 6. Participant Journey Design
**Owner:** Experience Designer + Community Manager  
**Deliverables:**
- Pre-session: Marketing materials, consent forms, preparation guide
- During session: Onboarding tutorial, helper system, AI prompts
- Post-session: Reflection prompts, optional data export, feedback collection
- Privacy policy and data handling documentation
- Peer mentorship framework

**Key Outputs:** Journey map, participant-facing documents, feedback mechanisms

---

### 7. Scientific Paper & Evaluation
**Owner:** Researcher (You) + Academic Advisor  
**Deliverables:**
- Completed theoretical framework (Sections 1-2) ✓ [DONE]
- Design challenges & solutions (Section 4) ✓ [DONE]
- Implementation documentation (Section 5)
- Evaluation methodology (Section 6)
- User testing results (Section 7)
- Discussion and conclusions (Section 8)
- Bibliography and formatting

**Key Activities:** User studies, qualitative interviews, data analysis, writing, peer review

---

## 4.5-Month Timeline (18 Weeks)

### **PHASE 1: Foundation & Design (Weeks 1-4, March)**

**Week 1-2: Project Setup & Requirements**
- [ ] Project kickoff meeting
- [ ] Finalize work packages and assign owners
- [ ] Set up development environment (repos, servers, tools)
- [ ] **UX:** Create initial wireframes for core flows
- [ ] **Paper:** Finalize theoretical framework (Sections 2-3)

**Week 3-4: Core Architecture & Design**
- [ ] **Web App:** Build basic table structure (static, no real-time yet)
- [ ] **Sensor Layer:** Prototype tap detection and motion mapping
- [ ] **UX:** Complete wireframes, begin visual design system
- [ ] **AI:** Design conversation monitoring logic (pseudocode)
- [ ] **Paper:** Write Section 4.1-4.4 (Challenges 1-3)

**Milestone 1 (End of Week 4):**  
✓ Static prototype with table UI  
✓ Sensor input proof-of-concept  
✓ Design system v1  
✓ Paper Section 4 drafted (Challenges 1-6)

---

### **PHASE 2: Core Development (Weeks 5-9, April)**

**Week 5-6: Real-time Infrastructure**
- [ ] **Web App:** Implement WebSocket/real-time communication
- [ ] **Web App:** User join/leave table mechanics
- [ ] **Sensor Layer:** Integrate sensor inputs into web app
- [ ] **UX:** Refine configuration panel based on prototypes
- [ ] **Physical:** Design spatial audio setup (speaker positions)

**Week 7-8: Multimodal Translation**
- [ ] **Web App:** Audio synthesis for sensor inputs (taps → sound)
- [ ] **Web App:** Text-to-speech for screen readers
- [ ] **Sensor Layer:** Motion and breath sensor mappings
- [ ] **AI:** Build basic monitoring (detect silence/domination)
- [ ] **UX:** Design modality labeling system (icons, indicators)

**Week 9: Integration & Testing Round 1**
- [ ] **Integration:** Connect web app + sensor layer + AI monitoring
- [ ] **Testing:** Internal testing with team (text + tap modalities)
- [ ] **Physical:** Procure equipment (speakers, audio interface)
- [ ] **Paper:** Draft Section 5 (Implementation documentation)

**Milestone 2 (End of Week 9):**  
✓ Working prototype: 2 modalities (text + tap), basic AI monitoring  
✓ Real-time communication functional  
✓ First integration test complete

---

### **PHASE 3: Advanced Features & AI (Weeks 10-13, May)**

**Week 10-11: AI Moderator Development**
- [ ] **AI:** Neutral prompting system (modality-agnostic)
- [ ] **AI:** Meta-conversational prompts (optional mode)
- [ ] **AI:** Tutorial AI for practice table
- [ ] **Web App:** Display AI prompts in UI (text + TTS)
- [ ] **Sensor Layer:** Add voice input (speech recognition)

**Week 11-12: Spatial Audio & Visual Features**
- [ ] **Web App:** Binaural audio for remote users (Web Audio API)
- [ ] **Physical:** Set up spatial audio in test space
- [ ] **UX:** Design overlap visualization (Venn map)
- [ ] **Web App:** Build overlap metrics panel
- [ ] **Journey:** Create onboarding tutorial (progressive disclosure)

**Week 13: Mode-Constrained Tables & Privacy**
- [ ] **Web App:** Implement "Silent Table", "Movement Table" features
- [ ] **Web App:** Default ephemerality + opt-in recording
- [ ] **Web App:** Transparent logging interface
- [ ] **Journey:** Draft privacy policy and consent forms
- [ ] **Paper:** Begin Section 6 (Evaluation methodology)

**Milestone 3 (End of Week 13):**  
✓ All 4 core modalities working (text, tap, motion, voice)  
✓ AI moderator functional  
✓ Spatial audio operational  
✓ Privacy architecture implemented

---

### **PHASE 4: Polish, Accessibility & Testing (Weeks 14-16, June)**

**Week 14: Accessibility Hardening**
- [ ] **Web App:** Full screen reader testing (NVDA, JAWS, VoiceOver)
- [ ] **Web App:** Keyboard navigation audit
- [ ] **UX:** Test with accessibility specialists
- [ ] **Journey:** Finalize onboarding tutorial
- [ ] **Physical:** Test spatial audio in final venue

**Week 15-16: User Testing Round 1**
- [ ] **Journey:** Recruit 10-15 participants (mixed abilities)
- [ ] **Testing:** Facilitate 3-5 test sessions
- [ ] **Observation:** Record conversational dynamics, usability issues
- [ ] **Data:** Collect qualitative feedback (interviews, surveys)
- [ ] **Iteration:** Fix critical bugs and UX issues
- [ ] **Paper:** Draft Section 7.1 (User testing setup and results)

**Milestone 4 (End of Week 16):**  
✓ First round user testing complete  
✓ Critical accessibility issues resolved  
✓ System ready for public soft launch

---

### **PHASE 5: Refinement & Evaluation (Weeks 17-18, Early July)**

**Week 17: Public Soft Launch**
- [ ] **Journey:** Invite 20-30 participants for soft launch event
- [ ] **Physical:** Set up final installation in pop-up space
- [ ] **Observation:** Facilitate sessions, observe patterns
- [ ] **Data:** Collect detailed feedback and metrics
- [ ] **Troubleshooting:** Real-time bug fixes and adjustments

**Week 18: Final Analysis & Paper Completion**
- [ ] **Paper:** Analyze qualitative and quantitative data
- [ ] **Paper:** Write Section 7.2 (Analysis and findings)
- [ ] **Paper:** Write Section 8 (Discussion and conclusions)
- [ ] **Paper:** Complete bibliography and formatting
- [ ] **Documentation:** Create final technical documentation
- [ ] **Presentation:** Prepare final presentation for defense

**Milestone 5 (End of Week 18):**  
✓ Paper complete and submitted  
✓ Public installation documented  
✓ All deliverables finalized

---

## Dependency Map

```
┌─────────────────────────────────────────────────────────────────┐
│                      CRITICAL PATH                              │
└─────────────────────────────────────────────────────────────────┘

UX Design ─────────────► Web App ─────────► Integration ─────────► Testing
    │                        │                    │                     │
    │                        │                    │                     │
    └──► Sensor Layer ───────┘                    │                     │
                                                   │                     │
AI Design ─────────────────────────────────────────┘                     │
                                                                         │
Physical Space ──────────────────────────────────────────────────────────┘
                                                                         │
Journey Design ──────────────────────────────────────────────────────────┘
                                                                         │
Paper Writing (parallel throughout) ─────────────────────────────────────┘


KEY DEPENDENCIES:
1. UX wireframes → Web app development (Week 2 → Week 3)
2. Sensor prototypes → Web app integration (Week 4 → Week 5)
3. Basic web app → AI integration (Week 9 → Week 10)
4. Working prototype → Physical setup (Week 9 → Week 14)
5. All features complete → User testing (Week 13 → Week 15)
6. User testing → Paper evaluation section (Week 16 → Week 17)
```

---

## Resource Allocation

| Role | Time Commitment | Critical Weeks |
|------|-----------------|----------------|
| **You (Researcher/PM)** | Full-time (40h/wk) | All weeks (coordination + paper) |
| **Web Developer** | Part-time (20h/wk) | Weeks 3-13 (core dev) |
| **UX Designer** | Part-time (15h/wk) | Weeks 1-8, 14 (design + accessibility) |
| **AI Engineer** | Part-time (10h/wk) | Weeks 7-13 (AI moderator) |
| **Installation Tech** | Part-time (10h/wk) | Weeks 9-14, 17 (setup + testing) |
| **Accessibility Specialist** | Consultant (20h total) | Weeks 6, 14 (audit + testing) |
| **Test Participants** | 10-15 people | Weeks 15-16 (testing) |
| **Soft Launch Participants** | 20-30 people | Week 17 (public session) |

**Total Budget Estimate (rough):**
- Personnel: CHF 25,000-35,000 (part-time contractors)
- Equipment: CHF 3,000-5,000 (speakers, audio interface, displays)
- Venue: CHF 1,000-2,000 (pop-up space rental for 2 weeks)
- Participant compensation: CHF 1,000-2,000 (test sessions)
- **Total: CHF 30,000-44,000**

---

## Risk Management

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Web Audio API browser incompatibility** | Medium | High | Early cross-browser testing; fallback to simpler audio |
| **AI latency issues** | Medium | Medium | Use fast Claude API; pre-generate prompt templates |
| **Accessibility compliance delays** | High | High | Involve specialist from Week 1; build accessibility in from start |
| **Sensor reliability (motion, tap)** | Medium | Medium | Extensive device testing; graceful degradation if sensors fail |
| **Participant recruitment difficulties** | Medium | Medium | Start recruitment Week 10; offer compensation; diverse channels |
| **Physical space availability** | Low | High | Secure venue by Week 4; have backup location |
| **Paper deadline pressure** | High | High | Write incrementally throughout; buffer Week 18 for final polish |

---

## Weekly Standup Structure

**Frequency:** Every Monday, 1 hour  
**Attendees:** All work package owners + PM (you)

**Agenda:**
1. Last week accomplishments (5 min per person)
2. This week goals (5 min per person)
3. Blockers and dependencies (10 min)
4. Milestone check-in (5 min)
5. Schedule adjustments if needed (5 min)

**Communication Tools:**
- Slack/Discord: Daily async updates
- GitHub/GitLab: Code and documentation
- Miro/FigJam: Collaborative diagrams and journey maps
- Google Drive: Shared documents and paper drafts

---

## Success Criteria

### Technical Success:
- [ ] All 4 modalities (text, tap, motion, voice) functional
- [ ] AI moderator operates modality-neutrally
- [ ] Spatial audio works for both in-room and remote users
- [ ] Full screen reader compatibility
- [ ] Privacy-by-default architecture implemented
- [ ] No critical bugs during soft launch

### User Experience Success:
- [ ] 80%+ participants successfully onboard within 2 minutes
- [ ] All participants able to contribute using preferred modality
- [ ] Positive feedback on intelligibility and legibility
- [ ] No reports of modality hierarchy (speech dominance)
- [ ] Helper system used effectively

### Academic Success:
- [ ] Paper accepted/submitted on time
- [ ] Novel contribution to accessibility + IMP literature
- [ ] Empirical data from 30+ participants
- [ ] Clear demonstration of theory-to-practice bridge

---

## Deliverables Checklist

### By End of Project:
- [ ] Functional web application (deployed + documented)
- [ ] Physical installation (documented with photos/video)
- [ ] AI moderator system (code + documentation)
- [ ] User testing report (qualitative + quantitative)
- [ ] Academic paper (submitted)
- [ ] Project portfolio (website showcasing work)
- [ ] Open-source components (GitHub repos with READMEs)
- [ ] Final presentation (slides + demo)

---

**Document prepared:** February 2026  
**Project timeline:** March 1 – July 15, 2026 (4.5 months)  
**Next step:** Finalize team, kickoff meeting Week 1
