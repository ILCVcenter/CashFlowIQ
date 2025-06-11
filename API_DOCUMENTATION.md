# CashFlowIQ API Documentation

## Overview
CashFlowIQ is a financial analysis dashboard built with Streamlit. This document provides detailed API documentation for all modules and functions.

## Table of Contents
1. [Services Module](#services-module)
2. [Utils Module](#utils-module)
3. [UI Components](#ui-components)
4. [Data Loader](#data-loader)
5. [Pages](#pages)

---

## Services Module
`services.py` - Core business logic services

### Functions

#### `extract_text_from_pdf(pdf_file)`
Extracts text content from a PDF file.

**Parameters:**
- `pdf_file`: File object from Streamlit file uploader

**Returns:**
- `str`: Extracted text from the PDF

**Example:**
```python
text = extract_text_from_pdf(uploaded_file)
```

#### `analyze_contract(text, openai_api_key=None, model="gpt-4")`
Analyzes contract text using GPT to extract financial terms.

**Parameters:**
- `text` (str): Contract text to analyze
- `openai_api_key` (str, optional): OpenAI API key
- `model` (str): GPT model to use

**Returns:**
- `str`: JSON string with extracted contract terms

**Example:**
```python
analysis = analyze_contract(contract_text, model="gpt-4")
contract_data = json.loads(analysis)
```

#### `ask_contract_question(contract_text, question, openai_api_key=None, model="gpt-4")`
Answers questions about a contract using GPT.

**Parameters:**
- `contract_text` (str): The contract text
- `question` (str): User's question
- `openai_api_key` (str, optional): OpenAI API key
- `model` (str): GPT model to use

**Returns:**
- `str`: AI-generated answer

#### `get_exchange_rate(base_currency, target_currency)`
Fetches real-time exchange rates with fallback mechanism.

**Parameters:**
- `base_currency` (str): Source currency code (e.g., "USD")
- `target_currency` (str): Target currency code (e.g., "EUR")

**Returns:**
- `float`: Exchange rate or None if failed

**Example:**
```python
rate = get_exchange_rate("USD", "EUR")
# Returns: 0.92
```

#### `forecast_cashflow(df, periods=12)`
Generates cash flow forecast based on historical data.

**Parameters:**
- `df` (DataFrame): Historical data with 'date' and 'amount' columns
- `periods` (int): Number of periods to forecast

**Returns:**
- `DataFrame`: Forecast data with 'date' and 'forecast' columns

---

## Utils Module
`utils.py` - Utility functions

### Functions

#### `nl_to_sql(question, table_schema, sample_data, openai_api_key=None)`
Converts natural language questions to SQL queries.

**Parameters:**
- `question` (str): Natural language question
- `table_schema` (str): Comma-separated column names
- `sample_data` (str): Sample data for context
- `openai_api_key` (str, optional): OpenAI API key

**Returns:**
- `str`: Generated SQL query

**Example:**
```python
sql = nl_to_sql(
    "Show me total income by month",
    "date, amount, category, type",
    sample_data_string
)
# Returns: "SELECT STRFTIME('%Y-%m', CAST(date AS DATE)) AS month, 
#          SUM(amount) AS income FROM data 
#          WHERE category = 'Income' GROUP BY month"
```

#### `execute_sql(df, sql_query)`
Executes SQL query on a DataFrame using DuckDB.

**Parameters:**
- `df` (DataFrame): Data to query
- `sql_query` (str): SQL query to execute

**Returns:**
- `DataFrame`: Query results

---

## UI Components
`ui/components.py` - Reusable UI components

### Functions

#### `display_header()`
Displays the application header with logo.

#### `render_list_of_dicts_table(lst)`
Renders a list of dictionaries as a Streamlit table.

**Parameters:**
- `lst` (list): List of dictionaries to display

#### `render_vertical_table(data)`
Renders a dictionary as a vertical table.

**Parameters:**
- `data` (dict): Dictionary to display

#### `convert_df_to_csv(df)`
Converts DataFrame to CSV for download.

**Parameters:**
- `df` (DataFrame): Data to convert

**Returns:**
- `bytes`: CSV data encoded as UTF-8

---

## Data Loader
`data/data_loader.py` - Data loading and filtering functions

### Functions

#### `load_data()`
Loads sample data from CSV file.

**Returns:**
- `DataFrame`: Loaded data

**Note:** Cached for 60 seconds to allow data refresh.

#### `filter_data_by_date_range(data, date_range)`
Filters data by date range.

**Parameters:**
- `data` (DataFrame): Data to filter
- `date_range` (list): List with start and end dates

**Returns:**
- `DataFrame`: Filtered data

#### `filter_data_by_categories(data, categories)`
Filters data by categories.

**Parameters:**
- `data` (DataFrame): Data to filter
- `categories` (list): List of categories to include

**Returns:**
- `DataFrame`: Filtered data

#### `process_uploaded_csv(uploaded_file, existing_data)`
Processes uploaded CSV and merges with existing data.

**Parameters:**
- `uploaded_file`: Streamlit uploaded file object
- `existing_data` (DataFrame): Current data

**Returns:**
- `DataFrame`: Merged data

---

## Pages

### Cash Flow Page
`pages/cash_flow.py`

#### `render_cash_flow_page(data)`
Main function to render the cash flow analysis page.

**Parameters:**
- `data` (DataFrame): Financial data

**Features:**
- Currency conversion
- Cash flow statement with filtering
- Financial charts and visualizations
- Cash flow forecasting
- Data export/import functionality

### Contract Analysis Page
`pages/contract_analysis.py`

#### `render_contract_analysis_page()`
Renders the contract analysis page.

**Features:**
- PDF upload and text extraction
- Automatic contract analysis using GPT
- Interactive Q&A chat about contracts
- Structured display of extracted terms

### Query Chat Page
`pages/query_chat.py`

#### `render_query_chat_page(data)`
Renders the natural language query interface.

**Parameters:**
- `data` (DataFrame): Data to query

**Features:**
- Natural language to SQL conversion
- Query execution and results display
- Data visualization (bar, line, pie charts)
- Export query results

---

## Data Schema

### Sample Data CSV Format
```csv
date,amount,category,type,description,component,inventory_level
2024-01-01,4448.00,Income,Sale,Product A Sales,,
2024-01-21,-1067.52,Expense,Material,Raw Materials Purchase,Metal,50.00
```

**Columns:**
- `date`: Transaction date (YYYY-MM-DD)
- `amount`: Transaction amount (positive for income, negative for expenses)
- `category`: Main category (Income/Expense/Service/Sale/Investment)
- `type`: Transaction type (Sale/Material/Utility/Service/Salary/Equipment/Logistics/Repair)
- `description`: Transaction description
- `component`: Optional component type
- `inventory_level`: Optional inventory level

---

## Error Handling

All functions include error handling with appropriate error messages displayed to users. Common patterns:

1. **API Failures**: Fallback to cached values or default behavior
2. **Invalid Input**: Clear error messages with suggestions
3. **File Processing**: Graceful handling of corrupted or invalid files
4. **Query Errors**: Detailed SQL error messages for debugging

---

## Environment Variables

Required environment variables (in `.env` file):
```
OPENAI_API_KEY=your_api_key_here
```

---

## Testing

Run tests using:
```bash
python -m pytest tests/
# or
python -m unittest discover tests/
```

Test coverage includes:
- Exchange rate fetching and fallbacks
- Cash flow forecasting
- Data filtering functions
- SQL query execution
- Natural language processing 