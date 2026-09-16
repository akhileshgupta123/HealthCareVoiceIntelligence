# Product Requirements Document (PRD): Real-Time Healthcare Operations Assistant

## 1. Executive Summary
The Real-Time Healthcare Operations Assistant is a voice-first, AI-driven platform designed to streamline clinical and administrative workflows. By leveraging high-speed context retrieval and multi-agent orchestration, the system allows healthcare staff to query claim statuses, retrieve operational policies, and escalate issues through natural voice interactions. The system is built for sub-10ms context retrieval to ensure a seamless, human-like conversational experience.

## 2. Problem Statement
Healthcare providers and administrative staff are often bogged down by manual data entry and complex navigation within Electronic Health Records (EHR) and operational systems. Existing voice assistants often suffer from high latency, making them impractical for fast-paced clinical environments. There is a critical need for a low-latency, "eyes-busy, hands-busy" solution that can provide instant answers and perform actions across disparate healthcare systems.

## 3. Goals & Objectives
*   **Ultra-Low Latency:** Achieve sub-10ms retrieval for immediate context and knowledge access using Moss.
*   **Voice-First Experience:** Provide a seamless WebRTC-based voice interface with minimal "dead air."
*   **Modular Intelligence:** Implement a Supervisor-Worker agent pattern to handle specialized tasks (Claims, Knowledge, Escalation).
*   **Vendor Agnostic:** Ensure the system can interface with any healthcare backend via standardized (Mock) APIs.
*   **Operational Efficiency:** Reduce the time spent by staff on administrative lookups and ticketing.

## 4. Target Users / Stakeholders
*   **Clinical Staff:** Doctors and nurses needing quick patient info or protocol guidance.
*   **Administrative Staff:** Billing and coding specialists checking claim/check statuses.
*   **Operations Managers:** Staff overseeing facility workflows and ticket escalations.
*   **IT/DevOps Teams:** Responsible for maintaining the scalable infrastructure and security.

## 5. Functional Requirements

### 5.1 Voice Interaction & Processing
*   **Real-time Streaming:** Support full-duplex audio streaming via WebRTC.
*   **Voice Activity Detection (VAD):** Accurately detect when a user starts and stops speaking.
*   **Speech-to-Text (STT):** Convert spoken healthcare terminology into text with high accuracy.
*   **Text-to-Speech (TTS):** Stream synthesized responses back to the user in real-time.

### 5.2 Orchestration & Intelligence
*   **Intent Classification:** The Supervisor Agent must accurately route requests to the appropriate sub-agent.
*   **Context Management:** Maintain conversation state across multiple turns.
*   **Specialized Task Handling:**
    *   **Claims/Check Agent:** Query status of financial transactions.
    *   **Knowledge Agent:** Retrieve policy and "next-step" procedural information.
    *   **Escalation Agent:** Programmatically create and update support tickets.

### 5.3 Knowledge & Data Retrieval
*   **Instant Recall:** Use Moss to store and retrieve session context and frequently used operational knowledge.
*   **RAG Synthesis:** Combine retrieved data with LLM capabilities to provide natural, concise answers.

## 6. Non-Functional Requirements
*   **Performance:** Moss retrieval must be <10ms; end-to-end voice round-trip latency should feel instantaneous.
*   **Scalability:** System must support concurrent voice sessions via Kubernetes orchestration.
*   **Reliability:** High availability for the LiveKit gateway and Agent services.
*   **Security:** All data in transit must be encrypted; strict RBAC for healthcare data access.

## 7. System Architecture Overview
The system follows a hierarchical multi-agent architecture:
1.  **Frontend Layer:** React/TypeScript client using LiveKit SDK for WebRTC audio.
2.  **Voice Gateway:** LiveKit server handling STT/TTS/VAD.
3.  **Orchestration Layer:** A Python-based Supervisor Agent (LangGraph) managing state and routing.
4.  **Worker Layer:** Specialized agents (Claims, Knowledge, Escalation) performing targeted logic.
5.  **Speed Layer:** Moss Context Engine providing sub-10ms retrieval for the agents.
6.  **Integration Layer:** FastAPI-based Mock Healthcare APIs simulating EHR and Ticketing systems.

## 8. Tech Stack
*   **Frontend:** React, TypeScript, LiveKit SDK, WebRTC.
*   **Real-time Voice:** LiveKit Agent SDK, STT/TTS/VAD.
*   **AI Frameworks:** Python, LangGraph, LangChain, LLMs.
*   **Retrieval/Cache:** Moss (Context Engine, Session Index, Long-term KB).
*   **Backend APIs:** FastAPI (Python).
*   **Database:** PostgreSQL.
*   **Infrastructure:** Docker, Kubernetes (EKS).
*   **Security:** OAuth2, JWT, RBAC.
*   **Observability:** OpenSearch, Grafana.

## 9. Data Requirements
*   **Session Data:** Temporary storage of current conversation state in Moss.
*   **Knowledge Base:** Operational policies and medical guidelines indexed in Moss for RAG.
*   **Persistent Data:** User profiles, audit logs, and system configurations stored in PostgreSQL.
*   **Mock Healthcare Data:** Standardized schemas for Patients, Claims, Eligibility, and Tickets.

## 10. API Specifications (Mock)
*   **GET /claims/{id}:** Retrieve status and details of a specific claim.
*   **GET /checks/{id}:** Retrieve status of insurance checks.
*   **POST /tickets:** Create a new escalation ticket with conversation context.
*   **GET /eligibility/{patient_id}:** Check insurance eligibility status.
*   **GET /knowledge/search:** Query the Moss-backed knowledge base for protocols.

## 11. Security Requirements
*   **Authentication:** Identity verification via OAuth2.
*   **Authorization:** Role-Based Access Control (RBAC) to ensure staff only access permitted data.
*   **Data Protection:** JWT-based token validation for all internal API calls.
*   **Audit Logging:** Comprehensive logging of all data access and voice interactions for compliance.

## 12. Deployment & Infrastructure
*   **Containerization:** All services (Agents, APIs, Frontend) packaged as Docker images.
*   **Orchestration:** Deployment on Kubernetes (EKS) for auto-scaling and self-healing.
*   **CI/CD:** Automated pipelines for testing and deploying agent logic.
*   **Monitoring:** Real-time latency tracking and error reporting via OpenSearch and Grafana.

## 13. Success Metrics
*   **Retrieval Latency:** % of Moss queries completed in <10ms.
*   **Intent Accuracy:** % of requests correctly routed by the Supervisor Agent.
*   **Task Completion:** % of user requests resolved without human intervention.
*   **User Satisfaction:** Qualitative feedback from healthcare staff on voice responsiveness.

## 14. Timeline & Milestones
*   **Phase 1 (Week 1):** Setup LiveKit infrastructure and basic React voice client.
*   **Phase 2 (Week 2):** Implement Supervisor Agent and Moss integration for sub-10ms retrieval.
*   **Phase 3 (Week 3):** Develop specialized worker agents and FastAPI Mock Healthcare services.
*   **Phase 4 (Week 4):** End-to-end integration, security hardening, and observability setup.

## 15. Open Questions & Risks
*   **Risk:** Latency spikes in LLM inference could overshadow the speed gains from Moss.
*   **Risk:** Handling complex medical terminology in STT may require specialized acoustic models.
*   **Question:** Should the Escalation Agent support direct "Human-in-the-loop" voice transfers in the future?
*   **Question:** What specific FHIR versions should the Mock APIs prioritize for future real-world EHR compatibility?