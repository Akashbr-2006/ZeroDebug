 Autonomous CI/CD Healing Agent

This project is an Autonomous DevOps Agent designed to detect, repair, and verify code issues within GitHub repositories. By utilizing a sandboxed Docker environment and a multi-agent architecture, the system autonomously iterates through code failures until the CI/CD pipeline passes.

 Architecture & Workflow
The agent follows a sophisticated "Self-Healing" pipeline to ensure code integrity:


Ingestion: The user provides a GitHub Repository URL via the React Dashboard.
+1


Containerized Isolation: The backend spins up a Docker container to clone the repository, providing a secure sandbox for execution.


Analysis & Execution: The agent discovers and runs all test files automatically. It identifies various bug types including LINTING, SYNTAX, LOGIC, and TYPE_ERRORS.


Autonomous Healing: * Targeted fixes are generated for identified failures.

The agent applies repairs locally within the Docker environment and re-runs tests.


Recursive Verification: * Fixes are committed with an [AI-AGENT] prefix and pushed to a new branch.


The system monitors the pipeline and repeats the healing process (up to a configurable retry limit) until all tests pass.



Reporting: Final results, including a score breakdown and fix history, are pushed to the live dashboard.

src="assets/image_a9939d.jpg".

 Key Features

Multi-Agent Intelligence: Uses a multi-agent framework (e.g., LangGraph/CrewAI) for complex problem-solving.



Sandboxed Execution: All code runs in isolated Docker containers to protect the host system.


Automated Branching: Creates structured branches using the required format: TEAM_NAME_LEADER_NAME_AI_Fix.


Real-time Dashboard: A responsive React interface featuring a CI/CD status timeline and failure analytics.


 Tech Stack

Frontend: React (Functional Components + Hooks), Tailwind CSS.


Backend: Python/Node.js with a Multi-Agent Architecture.



Infrastructure: Docker for sandboxing.


Deployment: Vercel (Frontend) and Railway/AWS (Backend/Agent).


 Installation & Setup
Prerequisites
Docker installed and running.

Node.js (v18+) and Python (v3.10+).
