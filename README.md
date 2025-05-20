
# CashFlowIQ

## Goal
To build an interactive Proof of Concept (POC) system that integrates AI capabilities into financial workflows. The system demonstrates technological skill, financial understanding, and integration of LLMs, data, and business tools. Features include cash flow forecasting, contract analysis, automated reporting, and visual insights.

## Business Objectives
- Forecast cash flow by category, type, and period.
- Extract key financial terms from unstructured contracts.
- Predict financial behavior using historical data.
- Automate financial reports and detect anomalies.
- Allow natural language queries over SQL data and return visual summaries.
- Incorporate live external data (e.g., currency exchange rates) through third-party APIs to enhance financial calculations.

## Implementation Strategy
- API-based access for real-time LLM-driven analysis.
- Modular system design.
- Unified interface with Streamlit.
- Optional integration with MCP servers.
- Natural language to SQL translation and result visualization.
- Fetch real-time data from external APIs (e.g., exchangerate.host or similar) and integrate with the analytical engine.

## Technology Stack
| Component        | Purpose                     | Tools                          |
|------------------|-----------------------------|--------------------------------|
| CSV Files        | Data input                  | Pandas, DuckDB, MCP server-fs  |
| PDF Contracts    | Extract terms               | PyPDF2 / GPT / MCP-docs        |
| Forecasting      | Time-series modeling        | Prophet, scikit-learn          |
| UI Dashboard     | User interaction layer      | Streamlit                      |
| LLM Integration  | Reasoning and SQL parsing   | OpenAI GPT API / Claude        |
| SQL Engine       | Data querying and analysis  | DuckDB / SQLite + MCP          |
| Currency API     | Real-time financial input   | exchangerate.host / requests   |

## Functional Workflow
1. Define schema and load CSVs to DuckDB.
2. Upload and analyze contract using GPT.
3. Forecast results and visualize in dashboard.
4. Ask questions in English → GPT generates SQL → executes and shows results.
5. Connect to live API for exchange rates → Adjust monetary calculations.
6. Optional: connect MCP servers.
7. Finalize with screenshots, README, and deployable package.

## UI Overview
- Default screen: interactive cash flow dashboard.
- Tabs: Cash Flow, Contract Analysis, Query Chat, Admin Panel.
- English-only interface. Mobile-responsive.
- Export functions (Excel/PDF), real-time visual updates.

## Deliverables
- Streamlit-based application
- Integrated GPT queries
- Contract parser
- Local DuckDB instance
- External API integration for real-time currency conversion
- Complete project README and structure
