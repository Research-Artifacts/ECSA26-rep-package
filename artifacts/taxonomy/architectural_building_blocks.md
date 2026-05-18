# Synthesized Practical Capability Sub-families for RQ3

This artifact provides a synthesized view of the practical capability sub-families identified across the analyzed 
open-source repositories. It was derived from the ISO/IEC 30141-based capability classification combined with 
qualitative content analysis of repository artifacts, and is intended to support the interpretation of recurring 
architectural arrangements discussed in RQ3.

This document consolidates recurring architectural building blocks that repeatedly emerged across the corpus. Therefore 
it, should be read as an auxiliary traceability artifact linking the higher-level architectural interpretation presented 
in the paper to the underlying classified repositories evidence.


### 1. Data Processing capabilities

| ISO Family      | Sub‑Family (friendly name)          | Examples of technologies / projects                                                                           |
|-----------------|-------------------------------------|---------------------------------------------------------------------------------------------------------------|
| Data processing | Local Runtime & Inference           | TFLite / LiteRT, ExecuTorch, MindSpore Lite, OpenVINO, Vitis AI, DeepStack, NanoLLM, Edgen, OVMS              |
| Data processing | TinyML / MCU Inference              | emlearn, microflow‑rs, Piccolo AI, MaixPy, AI‑on‑the‑edge‑device, EdgeInfer                                   |
| Data processing | Stream & Event Processing           | eKuiper, Fledge filters/notifications, Flogo flows, FogFlow operators, Simple IoT rules                       |
| Data processing | Model Training / Federated Learning | FEDn, MindSpore FL, RL‑based RF localization, local training pipelines                                        |
| Data processing | Model Compilation & Optimization    | nn‑comp, Vitis AI toolchain, ExecuTorch AOT, MindSpore graph opt, SenseCraft/SSCMA, TinyML QAT/PTQ toolchains |
| Data processing | Vision / Video / Audio Analytics    | Motion‑AI, Viseron, JeVois, OpenVINO Test Drive, Auritus, AiCSD, smart‑social‑distancing                      |

---

### 2. Data transferring (communication, network interface) capabilities

| ISO Family                            | Sub‑Family                              | Examples                                                                                                                                 |
|---------------------------------------|-----------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| Data transferring / network interface | MQTT Messaging Broker                   | NanoMQ, thin‑edge.io, Magistrala, SuperMQ, IoT Edge Hub (MQTT/AMQP), Home Assistant add‑ons                                              |
| Data transferring / network interface | Kafka / Event Streaming                 | Zilla (Kafka gateway), Redpanda Edge Agent, OVMS gRPC/REST, OpenVINO Test Drive (remoto)                                                 |
| Data transferring / network interface | Protocol Bridging & Gateways            | LoRaWAN IoT Edge gateway, macchina.io EDGE, Trusted Connector, Magistrala, thin‑edge.io, Zilla (HTTP/MQTT↔Kafka), LoRaWAN Network Server |
| Data transferring / network interface | Service Mesh / Proxies / Load Balancers | Pipy, loxilb, FabEdge, Nabto, EVIO overlay, FabEdge CNI, Zilla, P2P secure gateways                                                      |
| Data transferring / network interface | P2P & NAT Traversal                     | Nabto Edge, FabEdge (Libp2p), Trusted Connector (IDSCP2), EVIO, Nabto hole‑punching                                                      |
| Data transferring / network interface | Store‑and‑Forward / Buffering           | IoT Edge Hub, AWS FleetWise Edge Agent, Redpanda Edge Agent, thin‑edge.io buffering                                                      |

---

### 3. Supporting capabilities (management, orchestration, lifecycle)

| ISO Family              | Sub‑Family                                           | Examples                                                                                                                                  |
|-------------------------|------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| Management / Supporting | Orchestration & Scheduling (Cloud/Edge/Fog)          | Kubernetes, MicroShift, EFLOW+IoT Edge, EVE, FogFlow, FogBus2, Home Edge Orchestrator, Azure Arc, Open Data Hub AI Edge                   |
| Management / Supporting | Provisioning & Configuration (Infra‑as‑Code, GitOps) | RHEL Edge (Ansible/Image Builder), SaltStack, Azure Arc, RHEL Edge Manager, IaC + GitOps (Argo CD, Ansible, Edge ML kits)                 |
| Management / Supporting | OTA Updates & Fleet Management                       | Edgehog, thin‑edge.io, RHEL Edge, IoT Hub device management, OTA pipelines (Mcumgr/RAUC/OSTree)                                           |
| Management / Supporting | Model / Application Lifecycle                        | OpenVINO Model Server, SenseCraft/SSCMA, MindSpore (device‑edge‑cloud), ExecuTorch pipeline, AI Edge (Open Data Hub), Olares, Solo Server |
| Management / Supporting | Dev Tooling & Codegen Pipelines                      | nn‑comp, TinyML exporters (emlearn, microflow‑rs, Piccolo), DEM, diagram‑to‑code generators, AutoML toolchains                            |
| Management / Supporting | Monitoring / Observability                           | LeapfrogAI observability, OVMS metrics (Prometheus), Simple IoT graphs, SaltStack audit, Arc/Monitor, OpenTelemetry stacks                |
| Management / Supporting | Edge Runtime Hosting / Virtualization                | EFLOW, EVE, container runtimes (IoT Edge runtime, MicroShift single‑node), WasmEdge runtime, OpenShift Edge                               |

---

### 4. Interface capabilities (APIs, UIs, SDKs)

| ISO Family                  | Sub‑Family                     | Examples                                                                                                                      |
|-----------------------------|--------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| Application interface / API | OpenAI‑Compatible / LLM APIs   | Edgen, NanoLLM, LeapfrogAI, xsAI SDK, HAL‑9100, OVMS, Solo Server, Edge‑first LLM servers                                     |
| Application interface / API | REST/gRPC/GraphQL Service APIs | OVMS, DeepStack, AI‑on‑the‑edge‑device (REST), Zilla gateway, Nabto CoAP/TCP tunneling, SAF messaging, Azure IoT Edge modules |
| User interface / HMI        | Dashboards & Web UIs           | Simple IoT UI, Home Assistant dashboards, OpenVINO Test Drive GUI, Edge mgmt UIs, situational awareness dashboards            |
| SDK / Client Libraries      | Lightweight SDKs/clients       | xsAI, Nabto C SDK, various Python/C++ SDKs for runtimes (ExecuTorch, MindSpore, Vitis AI, WasmEdge AI, MaixPy)                |

---

### 5. Trustworthiness / Security & Compliance capabilities

| ISO Family                              | Sub‑Family                                  | Examples                                                                                                                |
|-----------------------------------------|---------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| Security (identity, auth, secure comms) | Identity & Auth (mTLS, JWT, IAM)            | Magistrala IAM, SuperMQ IAM, Azure IoT Hub + IoT Edge identities, Nabto, Trusted Connector DAPS, LeapfrogAI zero‑trust  |
| Security (secure comms)                 | Secure Channels (TLS/mTLS, VPN, SD‑WAN)     | FabEdge mTLS VPN, EVIO overlay, Nabto DTLS, Zilla mTLS termination, Edge VPNs em FogBus2, RHEL Edge secure channels     |
| Compliance & Governance                 | Data Sovereignty & Usage Control            | Trusted Connector (LUCON, IDS), GAIA‑X/IDS‑ready connectors, LeapfrogAI auditability, Arc/ SaltStack compliance as code |
| Privacy‑preserving ML                   | Federated Learning + Privacy (DP, SMPC, HE) | MindSpore FL, FEDn (com políticas), privacy em FL/edge AI pipelines                                                     |

---

### 6. Other implied families (transducer / physical integration)

| ISO Family                     | Sub‑Family                      | Examples                                                                                                                                  |
|--------------------------------|---------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| Transducer (sensing/actuating) | Sensor & Peripheral Integration | MaixPy (camera, LCD, GPIO, UART/I2C/SPI, Wi‑Fi/BLE), Fledge (Modbus/OPC‑UA/PLC), macchina.io EDGE (GPIO, USB, serial), jomjol (ESP32‑CAM) |
| Transducer (control)           | Closed‑Loop Control at Edge     | Fledge notifications/control dispatcher, Edge‑based energy management, industrial control loops with feedback commands to actuators       |

---
