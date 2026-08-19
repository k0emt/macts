# MACTS

**Multi-Agent Control of Traffic Signals** is a legacy MSE project that explores adaptive traffic-signal control with a small multi-agent system built around **SUMO**, **RabbitMQ**, and **Python 2.7**.

> **Project status:** archived. This repository is preserved for reference and historical documentation. It is **not under active development** and should not be expected to run unchanged on a modern environment.

> **Looking for the maintained successor?** See **[`macts-next`](https://github.com/k0emt/macts-next)** for the leaner, modernized follow-on repository.

Legacy project site: <https://k0emt.github.io/macts/>

## Overview

MACTS models two coordinated traffic-light junctions in SUMO:

- **JunctionSS** (St Saviours)
- **JunctionRKLN** (Rose Kiln Lane)

The runtime design is message-driven:

1. A **CommunicationsAgent** launches SUMO, advances the simulation, reads detector data through TraCI, and publishes metrics and sensor events.
2. Two **reactive planning agents** (`JSS_Reactive_Agent.py` and `JRKL_Reactive_Agent.py`) consume junction sensor data and choose the next candidate phase.
3. A **safety agent** per junction validates signal progression and minimum timing before issuing traffic-light commands.
4. A **MetricsAgent** aggregates emissions, fuel, noise, halting vehicles, and mean-speed data, then persists a simulation summary to MongoDB.

The repository also includes design documents, project artifacts, UML diagrams, and earlier spike/prototype work from the original graduate project.

## Repository layout

| Path | Purpose |
| --- | --- |
| `source/macts/` | Primary legacy implementation: agents, SUMO configs, detector/network files, and RabbitMQ helper scripts |
| `source/sumo_networks/` | Additional SUMO network experiments and earlier simulation setups |
| `source/spikes/` | Exploratory prototype code and experiments |
| `docs/` | Published project artifacts and the legacy project website (`docs/index.html`) |
| `portfolio/` | Editable project documents, presentations, plans, and supporting coursework artifacts |
| `uml/` | UML models, diagrams, and sequence/activity illustrations |
| `references/` | Papers, reference material, and archived phase deliverables |

## Key implementation files

Within `source/macts/`:

- `CommunicationsAgent.py` — orchestrates SUMO, TraCI, RabbitMQ messaging, detector reads, and metric publication
- `JSS_Reactive_Agent.py` — reactive planner for St Saviours
- `JRKL_Reactive_Agent.py` — reactive planner for Rose Kiln Lane
- `JSS_SafetyAgent.py` / `JRKL_SafetyAgent.py` — safety validation and traffic-light command publication
- `TrafficLightSignal.py` — signal-state and signal-phase transition rules
- `MetricsAgent.py` — aggregates run metrics and stores them in MongoDB
- `Core.py` — shared agent, exchange, metric, and sensor-state primitives

## Legacy technology assumptions

The codebase reflects its original 2011-2012 environment:

- **Python 2.7**
- **SUMO** with **TraCI**
- **RabbitMQ** (the bundled batch scripts reference RabbitMQ **2.8.1** on Windows)
- **MongoDB**
- Python packages such as **pika** and **pymongo**
- A largely **Windows-oriented** setup (`*.bat` helpers and hard-coded paths)

Important caveats:

- Several scripts use Python 2 syntax and are **not Python 3 compatible** as written.
- Some paths are hard-coded for the original workstation layout, such as `C:\sumo-0.14.0\bin\` and `C:\macts\source\macts\`.
- Parts of the architecture are exploratory or incomplete; for example, collaboration/planning abstractions exist, but the implemented behavior centers on the reactive agents plus safety checks.

## Running the legacy simulation

This project is best treated as a reconstruction target rather than a turnkey application. If you want to run it, start from `source/macts/` and expect to adapt paths, package versions, and broker/database setup.

A likely legacy workflow is:

1. Install a Python 2.7 environment with `pika`, `pymongo`, SUMO, and TraCI bindings.
2. Start RabbitMQ and MongoDB.
3. Update the Windows helper scripts if your SUMO or RabbitMQ installation paths differ:
   - `start-command-line.bat`
   - `rabbitmq_init.bat`
   - `rabbitmq_clean.bat`
4. Create the RabbitMQ virtual host and users with `rabbitmq_init.bat`.
5. Declare exchanges with:

   ```bash
   python rabbitmq_create_exchanges.py
   ```

6. Start the long-running agents in separate terminals:

   ```bash
   python MetricsAgent.py
   python JSS_Reactive_Agent.py
   python JRKL_Reactive_Agent.py
   ```

7. Launch the simulation controller:

   ```bash
   python CommunicationsAgent.py low 300
   ```

The `CommunicationsAgent.py` usage pattern is:

```text
python CommunicationsAgent.py [low|medium|full] MAX_NUMBER_SIMULATION_STEPS
```

Where:

- `low`, `medium`, and `full` select the SUMO route/configuration variant
- the final integer sets the maximum number of simulation iterations

## Tests

The repository includes unit tests for signal progression logic in:

- `source/macts/TrafficLightSignalTests.py`

Most of the system behavior, however, depends on external legacy services and a matching SUMO environment.

## Documentation and historical artifacts

The most useful archival materials are:

- `docs/index.html` — legacy project homepage
- `docs/nehl_implementation_user_manual.pdf` — archived user manual
- `docs/nehl_implementation_architecture_design.pdf` — implementation-phase architecture document
- `docs/nehl_implementation_component_design_document.pdf` — component design details
- `uml/` — system context, sequence, and activity diagrams

## Current expectations

Use this repository for:

- studying the project structure
- reviewing the original code and design documents
- mining SUMO/RabbitMQ multi-agent experiment ideas
- preserving the original MSE project history

Do **not** expect:

- ongoing maintenance
- modern dependency management
- current-version compatibility
- production readiness
