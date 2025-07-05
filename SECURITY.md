# Security Policy

## Introduction

The security of The Amy Project is a top priority. We appreciate the efforts of security researchers and the community to help us maintain a secure environment for our users. This document outlines the process for reporting security vulnerabilities.

We are committed to addressing security issues responsibly and in a timely manner.

## Reporting a Vulnerability

If you discover a security vulnerability, please report it to us privately. **Do not disclose the issue publicly** in issue trackers, forums, or other public channels until we have had a chance to address it.

Please send a detailed report to a private contact point. As this is an open-source project without a dedicated security team, please direct reports to the project maintainers. You can create a "Security Advisory" on GitHub for private reporting.

Your report should include:

*   A clear and descriptive title.
*   A detailed description of the vulnerability.
*   Step-by-step instructions to reproduce the issue.
*   The potential impact of the vulnerability (e.g., data exposure, denial of service).
*   Any proof-of-concept code, scripts, or screenshots.

We will do our best to acknowledge your report within 72 hours and provide an estimated timeline for a fix.

## Supported Versions

Security updates are provided for the latest stable version of the application available in the `main` branch. We encourage all users to run the most recent version to ensure they have the latest security patches.

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < 1.0   | :x:                |


## Scope

This security policy applies to the following components and areas of The Amy Project:

*   The core agent logic in `app/core/amy_agent/`
*   The Telegram bot integration and its command handling in `app/integrations/telegram/`
*   The web UI and its backend configuration (`run_web.py`, `start_web.sh`)
*   Database interactions and the memory management system (`init_db.py`, `app/features/memory/`)
*   Scripts managing application state (`reset_amy_memory.py`, `manage_memory.py`)

This policy **does not** cover:

*   Vulnerabilities in third-party dependencies (please report those to the respective upstream projects).
*   Issues related to the underlying infrastructure, operating system, or network configuration where the application is deployed.
*   Security of the `venv/` directory, which is user-managed.
*   Example files or configurations not intended for production use (e.g., `.env.example`).

## Disclosure Policy

Once a vulnerability is reported, our process is as follows:

1.  **Triage**: We will confirm the vulnerability and determine its severity (Critical, High, Medium, Low).
2.  **Remediation**: We will work on developing a patch to address the issue.
3.  **Communication**: We will keep the reporter updated on our progress.
4.  **Disclosure**: After the patch is released, we will publish a security advisory, giving credit to the reporter (unless they wish to remain anonymous).

We aim to resolve critical vulnerabilities as quickly as possible. We kindly request that you adhere to a standard 90-day disclosure period, providing us adequate time to address the issue before you disclose it publicly.

Thank you for helping keep The Amy Project secure.
