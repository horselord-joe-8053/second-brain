---
type: source
title: Hermes Web Search Architecture
created: 2026-10-06
updated: 2026-10-06
tags: [web search, architecture, managed platform]
related: [managed-platforms, web-scraping]
sources: ["personal/hermes_web_search_architecture.md"]
---
# How Hermes Agent Provides Web Search

This document explains the architecture that enables seamless, seemingly "free" web search and scraping capabilities within the Hermes desktop application.

## Overview

Hermes operates as a **managed platform**, not just an API client. When you use built-in tools like `web_search` or `web_extract`, you are interacting with a pre-configured backend infrastructure provided by Nous Research. The user experience is designed to be frictionless, hiding the complexity of credential management, API cost accounting, and infrastructure maintenance behind a unified agentic runtime.

## The Architectural Breakdown

Hermes achieves this via a three-layered approach:

### 1. Bundled Backend Infrastructure
Rather than forcing individual users to acquire their own API keys for services like Firecrawl, SerpApi, or Brave Search, the Hermes platform:
*   **Aggregates Demand:** The platform provider (Nous Research) manages high-volume enterprise agreements with these search/scraping providers.
*   **Subsidizes Costs:** During the current development phase, operational costs are subsidized by the platform provider to lower barriers to entry and drive ecosystem adoption.

### 2. Hybrid Execution Model
Not every search or scrape requires a high-cost cloud API call. Hermes intelligently distributes tasks:
*   **Local Execution (Desktop App):** When possible, the Hermes desktop app utilizes the local machine's resources to run headless browsers (via its internal `browser_exec` capabilities), perform parsing, or handle lightweight extraction tasks. This significantly reduces server-side infrastructure costs.
*   **Cloud Backend:** Only when local execution is insufficient (due to complex site protection, rate limits, or required scale) does Hermes route the request to a cloud-based backend provider, utilizing the platform’s managed API pools.

### 3. Tiered Resource Allocation
The platform utilizes internal logic to manage costs:
*   **Free Tiers:** Tools are configured to consume the generous "free tier" allocations offered by backend providers (e.g., Firecrawl’s free 1,000 credits/month) before accessing platform-paid quotas.
*   **Caching:** Common search queries or frequently visited pages are cached within the Hermes infrastructure to prevent redundant, billable API calls for the same data.

## Why it feels "free"

*   **Managed Credentials:** All authentication happens via the platform layer. The user is authenticated into Hermes, and Hermes is authenticated into its backend providers.
*   **Abstraction:** You are interacting with an agent that understands "how to find info," not an API client that requires you to manage rate limits and credit balances for three different search providers.

## Future Outlook

As the platform matures, this model will likely transition to support user-managed authentication. The "Billing" settings currently present in the Hermes desktop app are placeholders for future functionality, which will allow users to connect their own API keys (BYOK - Bring Your Own Key) for higher-volume usage or to pay for premium features directly, moving beyond the platform-subsidized model.