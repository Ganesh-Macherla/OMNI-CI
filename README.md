# OMNI-CI :- Objective Market Narrative Inference - Competitive Intelligence.

# Competitive Intelligence Signal Engine  
### SNUC Hacks '26 — Problem Statement 2 (Market Intelligence)

An AI-driven market intelligence system that continuously tracks competitor digital surfaces, detects strategic changes over time, and converts them into actionable decision-ready insights.

---

## Problem Statement

Companies constantly need to understand:

- What competitors are launching
- How messaging and positioning are evolving
- Which offers and claims are becoming common
- What customer objections are repeatedly appearing
- Where market whitespace opportunities exist

However, competitor intelligence today is:

- Scattered across multiple platforms
- Manual and time-consuming to track
- Difficult to compare over time
- Lacking strategic interpretation

This leads to delayed decisions and missed opportunities.

---

## Our Solution

We built a **source-grounded time-series competitive intelligence engine** that:

- Continuously monitors competitor web content
- Detects meaningful strategic changes
- Maintains semantic historical memory
- Infers positioning shifts and emerging trends
- Presents insights through a decision-focused dashboard

The system transforms raw competitor signals into **structured strategic awareness**.

---

## System Architecture

### Stage 1 — Intelligent Data Acquisition
A targeted ingestion engine continuously crawls competitor surfaces such as:

- Landing pages
- Product or service pages
- Pricing pages
- Public marketing content

This ensures continuous visibility into competitor positioning.

---

### Stage 2 — Content Normalization & Structuring
Raw HTML is converted into structured Markdown.

This:

- Removes noise (scripts, UI artifacts)
- Preserves semantic hierarchy (headings, tables, lists)
- Improves downstream intelligence extraction

---

### Stage 3 — Section-Level Temporal Change Detection
Instead of comparing full pages, content is split into logical sections.

Each section:

- Is hashed using SHA-256
- Compared across time snapshots
- Triggers analysis only if meaningful change is detected

This enables:

- Efficient change detection
- Reduction of cosmetic update noise
- Precise tracking of strategic signals

---

### Stage 4 — Semantic Competitive Memory Layer
Each structured section is embedded into vector space and stored.

This enables:

- Time-series semantic comparison
- Messaging evolution tracking
- Historical positioning reconstruction

---

### Stage 5 — Strategic Reasoning Engine (RAG)
When a change is detected:

- Previous and current versions are analyzed
- Semantic differences are interpreted
- Strategic implications are inferred

The system generates structured **Signal Cards** describing:

- What changed
- Why it matters
- Possible competitive implications

---

### Stage 6 — Insight Exploration Dashboard
Insights are visualized via an interactive interface that allows teams to:

- Explore competitor changes over time
- Compare positioning across competitors
- Identify emerging market patterns
- Investigate signals with direct source traceability

---

## Intelligence Workflow

- Crawl competitor pages  
- Normalize content into Markdown  
- Detect section-level changes  
- Store embeddings for historical comparison  
- Perform reasoning on detected signals  
- Generate structured insights  
- Display insights in dashboard


---

## Core Innovation

### Time-Series Semantic Change Intelligence
Detects strategic shifts instead of simple content differences.

### Section-Level Signal Filtering
Focuses on meaningful competitor moves rather than cosmetic updates.

### Source-Grounded Strategic Insights
Every insight is traceable back to its exact content origin.

### Inverted Product Understanding
Reconstructs competitor positioning logic from public signals.

---

## Alignment with Problem Statement

This system enables teams to:

- Identify emerging messaging and positioning trends
- Track competitor strategic moves over time
- Discover market whitespace opportunities
- Understand evolving competitive narratives
- Make evidence-backed strategic decisions

---

## Tech Stack

**Data Ingestion**
- Playwright / Selenium

**Processing**
- Python
- Markdown parsers
- Hashing pipelines

**AI Layer**
- Embedding models
- Retrieval-Augmented LLM reasoning

**Storage**
- Vector Database (Chroma / Pinecone)
- Structured metadata store

**Interface**
- React / Next.js
- Data visualization libraries

---

## Repository Structure


