# Enterprise SQLite GraphQL Explorer

A Python-based enterprise data access application that exposes selected SQLite database tables through a **GraphQL API** and provides an interactive **Streamlit data explorer**.

The application separates the database layer, GraphQL API layer, and Streamlit UI layer so that users can access approved database data without having direct access to the SQLite database.

# 2. Project Structure

```text
GraphQL API/
│
├── SQLDB.db
├── config.toml
├── database.py
├── graphql_api.py
├── server.py
├── app.py
└── requirements.txt
```

### File Description

| File               | Purpose                                           |
| ------------------ | ------------------------------------------------- |
| `chinook.db`       | SQLite database                                   |
| `config.toml`      | Database configuration and allowed GraphQL tables |
| `database.py`      | SQLite connection and database operations         |
| `graphql_api.py`   | GraphQL schema and queries                        |
| `server.py`        | FastAPI application and GraphQL endpoint          |
| `app.py`           | Streamlit user interface                          |
| `requirements.txt` | Python dependencies                               |

---

# 3. Technology Stack

* Python
* SQLite
* FastAPI
* Strawberry GraphQL
* Streamlit
* Pandas
* TOML configuration

---

# 4. Configuration

The application uses `config.toml` as the central configuration file.

Example:

```toml
[database]
path = "C:/Bhavik/Live_VS_code/GraphQL API/chinook.db"

[graphql]
allowed_tables = [
    "Customer",
    "Employees"
]


## Database Path

The database location is defined under:

```toml
[database]
path = "DB_Name.db"
```

Update this value when using a different SQLite database.

## Allowed Tables

Only tables listed under:

```toml
[graphql]
allowed_tables = [
    "Artist",
    "Album",
    "Customer"
]
```

are exposed through the GraphQL API.

For example:

```toml
[graphql]
allowed_tables = [
    "Artist",
    "Album",
    "Customer",
    "Invoice",
    "InvoiceLine",
    "Track"
]
```

The API will allow only these tables.

Tables that are not listed are rejected by the API.

---

# 5. Python Environment

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

---

# 6. Install Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```text
streamlit
fastapi
uvicorn
strawberry-graphql
requests
pandas
```

### Python Version

Python 3.11 or newer is recommended because `tomllib` is included in Python 3.11+.

For Python versions below 3.11, install:

```bash
pip install tomli
```

and replace:

```python
import tomllib
```

with:

```python
import tomli as tomllib
```

---

# 7. Start the GraphQL API

Open a terminal in the project directory:

```bash
cd "C:\Bhavik\Live_VS_code\GraphQL API"
```

Activate the virtual environment:

```bash
venv\Scripts\activate
```

Start FastAPI:

```bash
uvicorn server:app --reload --port 8000
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# 8. API Health Check

Open:

```text
http://127.0.0.1:8000/
```

Expected response:

```json
{
    "status": "online",
    "service": "SQLite GraphQL API"
}
```

---

# 9. GraphQL Interface

Open:

```text
http://127.0.0.1:8000/graphql
```

This provides the GraphQL interface for testing queries.

---

# 10. Swagger Documentation

FastAPI automatically provides Swagger documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

Swagger can be used to verify that the API is running correctly.

---

# 11. Test Available Tables

Run the following GraphQL query:

```graphql
query {
    tables {
        name
    }
}
```

Example response:

```json
{
    "data": {
        "tables": [
            {
                "name": "Album"
            },
            {
                "name": "Artist"
            },
            {
                "name": "Customer"
            }
        ]
    }
}
```

The result is based on the tables configured in `config.toml`.

---

# 12. Query Table Data

Example:

```graphql
query {
    tableData(
        tableName: "Artist"
        limit: 100
    ) {
        tableName

        columns {
            name
            dataType
        }

        rows
    }
}
```

The API returns:

* Table name
* Column names
* Column data types
* Table records

---

# 13. Table Access Control

The GraphQL API validates every requested table against `config.toml`.

For example, if the configuration contains:

```toml
allowed_tables = [
    "Artist",
    "Album",
    "Customer"
]
```

this query is allowed:

```graphql
query {
    tableData(
        tableName: "Artist"
        limit: 100
    ) {
        tableName
        columns {
            name
            dataType
        }
        rows
    }
}
```

However, this query is rejected:

```graphql
query {
    tableData(
        tableName: "Employee"
        limit: 100
    ) {
        tableName
        columns {
            name
            dataType
        }
        rows
    }
}
```

because `Employee` is not included in the approved table list.

---

# 14. Start Streamlit

Open another terminal.

Activate the virtual environment:

```bash
venv\Scripts\activate
```

Run:

```bash
streamlit run app.py
```

Streamlit will open in the browser.

Typical URL:

```text
http://localhost:8501
```

---

# 15. Streamlit Application

The Streamlit application provides an interactive data explorer.

The user can:

1. Select an approved table.
2. Select the number of records to load.
3. Load the table.
4. Search across columns.
5. Apply column-level filters.
6. View filtered records.
7. Download filtered data as CSV.

---

# 16. Record Limit

The Streamlit application provides predefined options:

```text
100
500
1,000
5,000
10,000
Unlimited
```

The default selection is:

```text
100
```

This prevents unnecessarily loading a large amount of data.

Selecting:

```text
Unlimited
```

requests all available records from the selected table.

For large production databases, server-side pagination and filtering should be implemented before using the Unlimited option.

---

# 17. Dynamic Filters

Filters are generated dynamically based on the selected table.

### Categorical Columns

Categorical columns are presented as multi-select filters.

Example:

```text
Country

☐ Brazil
☐ Canada
☐ Germany
☐ India
☐ USA
```

Multiple values can be selected.

### Numeric Columns

Numeric columns are presented as range sliders.

Example:

```text
CustomerId

1 ───────────────────── 59
```

### Global Search

The application also provides a global search:

```text
Search across all columns...
```

The search is case-insensitive.

---

# 18. Data Grid

The filtered records are displayed in the Streamlit data grid.

Example:

```text
CustomerId | FirstName | LastName | Country
------------------------------------------------
1          | Luís      | Gonçalves| Brazil
2          | Leonie    | Köhler   | Germany
3          | François  | Tremblay | Canada
```

The grid automatically uses the columns returned by GraphQL.

No table-specific columns are hard-coded into the Streamlit application.

---

# 19. Download Data

The filtered dataset can be downloaded using:

```text
Download CSV
```

The downloaded file uses the selected table name.

Example:

```text
Customer.csv
Artist.csv
Album.csv
```

---


# 21. Security Model

The SQLite database is not directly exposed to users.

Users interact with:

```text
GraphQL API
```

rather than:

```text
SQLite database
```

The API controls which tables can be accessed through:

```toml
allowed_tables
```

This provides a basic data-access boundary.

For production deployment, additional controls should be considered:

* API authentication
* Authorization
* HTTPS
* Rate limiting
* Query limits
* Server-side pagination
* Server-side filtering
* Audit logging
* Restricted database permissions
* Environment-based configuration
* Secrets management

# 23. Troubleshooting

## GraphQL API connection error

If Streamlit displays:

```text
Unable to connect to GraphQL API
```

make sure FastAPI is running:

```bash
uvicorn server:app --reload --port 8000
```

---

## Table not found

If you receive:

```text
no such table: Artist
```

verify the database path in:

```toml
[database]
path = "C:/Bhavik/Live_VS_code/GraphQL API/chinook.db"
```

Also verify that the table exists in the SQLite database.

---

## Table not allowed

If you receive:

```text
Table 'Employee' is not allowed.
```

add the table to:

```toml
[graphql]
allowed_tables = [
    "Customer",
    "Employee"
]
```

Restart FastAPI after changing the configuration.

---

## GraphQL field error

If you receive:

```text
Cannot query field 'data' on type 'TableData'
```

make sure the Streamlit GraphQL query matches the current GraphQL schema:

```graphql
tableData {
    tableName
    columns {
        name
        dataType
    }
    rows
}
```

Do not request a field named:

```graphql
data
```

unless that field has been explicitly added to the GraphQL schema.

---

# 24. Running the Complete Application

### Terminal 1 — FastAPI

```bash
venv\Scripts\activate

uvicorn server:app --reload --port 8000
```

### Terminal 2 — Streamlit

```bash
venv\Scripts\activate

streamlit run app.py
```

The application is then available at:

```text
GraphQL API:
http://127.0.0.1:8000/graphql

Swagger:
http://127.0.0.1:8000/docs

Streamlit:
http://localhost:8501
```

---

## 25. Future Enhancements

Recommended next improvements:

1. **Server-side pagination**
2. **Server-side GraphQL filtering**
3. **Column selection**
4. **Sorting**
5. **Date-range filters**
6. **Authentication and authorization**
7. **Role-based table access**
8. **API request logging**
9. **Export to Excel**
10. **KPI/dashboard visualizations**
11. **Caching**
12. **Production deployment**
13. **Environment-specific TOML configuration**
14. **API health monitoring**

The current design intentionally keeps the **SQLite, GraphQL, and Streamlit layers separated**, making these enhancements possible without redesigning the entire application.
