# SQL Polyglot

**Author:** abesticode  
**Version:** 0.0.1  
**Type:** Tool Plugin

## Description

SQL Polyglot is a powerful Dify plugin that provides comprehensive SQL parsing, transpiling, analysis, optimization, and execution capabilities. Built on top of the [SQLGlot](https://github.com/tobymao/sqlglot) library, this plugin enables AI agents to work with SQL across 31+ database dialects.

## Features

| Tool | Description |
|------|-------------|
| 🔄 **SQL Dialect Converter** | Convert SQL between 31+ database dialects |
| 📝 **SQL Beautifier** | Format SQL with proper indentation |
| 🔍 **SQL Metadata Extractor** | Extract tables, columns, joins from SQL |
| ✅ **SQL Syntax Checker** | Validate SQL syntax and detect errors |
| ⚡ **SQL Query Optimizer** | Optimize SQL for better performance |
| 🚀 **SQL on JSON Executor** | Execute SQL queries on JSON data |

## Installation

1. Install the plugin from the Dify Marketplace
2. No credentials required - SQLGlot runs locally

---

## Usage Examples

### 🔄 SQL Dialect Converter

Convert SQL from one dialect to another.

**Parameters:**
- `sql` (required): The SQL query to transpile
- `source_dialect` (optional): Source dialect (mysql, postgres, bigquery, etc.)
- `target_dialect` (required): Target dialect
- `pretty` (optional): Format output with indentation (default: true)

**Example 1: MySQL to PostgreSQL**
```
Input SQL: SELECT DATE_FORMAT(created_at, '%Y-%m-%d') FROM users
Source Dialect: mysql
Target Dialect: postgres

Output: SELECT TO_CHAR(created_at, 'YYYY-MM-DD') FROM users
```

**Example 2: Spark to BigQuery**
```
Input SQL: SELECT CAST(col AS STRING) FROM table
Source Dialect: spark
Target Dialect: bigquery

Output: SELECT CAST(col AS STRING) FROM table
```

---

### 📝 SQL Beautifier

Beautify SQL with proper indentation and styling.

**Parameters:**
- `sql` (required): The SQL query to format
- `dialect` (optional): SQL dialect for parsing
- `identify` (optional): Quote all identifiers (default: false)
- `normalize` (optional): Normalize identifiers to lowercase (default: false)

**Example 1: Basic Formatting**
```
Input SQL: select u.id,u.name,count(o.id) as order_count from users u left join orders o on u.id=o.user_id where u.active=1 group by u.id,u.name order by order_count desc

Output:
SELECT
  u.id,
  u.name,
  COUNT(o.id) AS order_count
FROM users AS u
LEFT JOIN orders AS o
  ON u.id = o.user_id
WHERE
  u.active = 1
GROUP BY
  u.id,
  u.name
ORDER BY
  order_count DESC
```

**Example 2: With Quote Identifiers (identify=true)**
```
Input SQL: SELECT id, name FROM users
identify: true

Output: SELECT "id", "name" FROM "users"
```

---

### 🔍 SQL Metadata Extractor

Extract metadata from SQL queries.

**Parameters:**
- `sql` (required): The SQL query to analyze
- `dialect` (optional): SQL dialect for parsing

**Example:**
```
Input SQL: 
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.active = 1
GROUP BY u.name
ORDER BY order_count DESC

Output:
{
  "query_type": "Select",
  "tables": [
    {"name": "users", "alias": "u"},
    {"name": "orders", "alias": "o"}
  ],
  "columns": [
    {"name": "name", "table": "u"},
    {"name": "id", "table": "o"},
    {"name": "id", "table": "u"},
    {"name": "user_id", "table": "o"},
    {"name": "active", "table": "u"}
  ],
  "joins": [
    {"type": "LEFT", "table": "orders", "on_condition": "u.id = o.user_id"}
  ],
  "functions": [
    {"name": "Count", "sql": "COUNT(o.id)"}
  ],
  "where_conditions": ["u.active = 1"],
  "group_by": ["u.name"],
  "order_by": [{"expression": "order_count", "desc": true}]
}
```

---

### ✅ SQL Syntax Checker

Check SQL syntax for errors.

**Parameters:**
- `sql` (required): The SQL query to validate
- `dialect` (optional): SQL dialect to validate against

**Example 1: Valid SQL**
```
Input SQL: SELECT id, name FROM users WHERE active = 1

Output: ✓ SQL is valid! Found 1 statement(s).
Statement types: Select
```

**Example 2: Invalid SQL (Missing Parenthesis)**
```
Input SQL: SELECT * FROM users WHERE (id = 1 AND name = 'John'

Output: ✗ SQL Validation Failed: Expecting ). Line 1, Col: 45.
  SELECT * FROM users WHERE (id = 1 AND name = 'John'
                                              ~
```

**Note:** Validate SQL checks SYNTAX only (parentheses, keywords, structure), not SEMANTIC (function compatibility with dialect).

---

### ⚡ SQL Query Optimizer

Optimize SQL queries using various techniques.

**Parameters:**
- `sql` (required): The SQL query to optimize
- `dialect` (optional): SQL dialect for parsing
- `schema` (optional): JSON object defining table schemas for type-aware optimization

**Example 1: Boolean Simplification**
```
Input SQL: SELECT * FROM users WHERE active = TRUE OR active = FALSE

Output: SELECT * FROM users
```

**Example 2: Constant Folding**
```
Input SQL: SELECT * FROM users WHERE created_at > '2024-01-01' + INTERVAL '1' MONTH

Output: SELECT * FROM users WHERE created_at > '2024-02-01'
```

**Example 3: With Schema (Advanced)**
```
Input SQL: 
SELECT A OR (B OR (C AND D))
FROM x
WHERE Z = '2024-01-01' + INTERVAL '1' MONTH OR 1 = 0

Schema: {"x": {"A": "BOOLEAN", "B": "BOOLEAN", "C": "BOOLEAN", "D": "BOOLEAN", "Z": "DATE"}}

Output:
SELECT
  A OR B OR (C AND D)
FROM x
WHERE
  Z = CAST('2024-02-01' AS DATE)
```

---

### 🚀 SQL on JSON Executor

Execute SQL queries against JSON data tables.

**Parameters:**
- `sql` (required): The SQL query to execute
- `tables` (required): JSON object containing table data
- `dialect` (optional): SQL dialect for parsing

**Example 1: Simple SELECT**
```
Input SQL: SELECT * FROM users WHERE age > 25

Tables:
{
  "users": [
    {"id": 1, "name": "Alice", "age": 30},
    {"id": 2, "name": "Bob", "age": 22},
    {"id": 3, "name": "Charlie", "age": 28}
  ]
}

Output:
| id | name    | age |
|----|---------|-----|
| 1  | Alice   | 30  |
| 3  | Charlie | 28  |
```

**Example 2: JOIN with Aggregation**
```
Input SQL: 
SELECT u.name, COUNT(o.product) as total_orders, SUM(o.amount) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.name

Tables:
{
  "users": [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Charlie"}
  ],
  "orders": [
    {"user_id": 1, "product": "Laptop", "amount": 1500},
    {"user_id": 1, "product": "Mouse", "amount": 50},
    {"user_id": 2, "product": "Keyboard", "amount": 100}
  ]
}

Output:
| name    | total_orders | total_spent |
|---------|--------------|-------------|
| Alice   | 2            | 1550        |
| Bob     | 1            | 100         |
| Charlie | 0            | NULL        |
```

**Note:** Execute SQL is for small datasets and testing purposes, not for production database queries.

---

## Supported SQL Dialects

| Dialect | Name | Status |
|---------|------|--------|
| `athena` | Amazon Athena | ✅ Official |
| `bigquery` | Google BigQuery | ✅ Official |
| `clickhouse` | ClickHouse | ✅ Official |
| `databricks` | Databricks | ✅ Official |
| `doris` | Apache Doris | ✅ Community |
| `drill` | Apache Drill | ✅ Community |
| `duckdb` | DuckDB | ✅ Official |
| `hive` | Apache Hive | ✅ Official |
| `mysql` | MySQL | ✅ Official |
| `oracle` | Oracle | ✅ Official |
| `postgres` | PostgreSQL | ✅ Official |
| `presto` | Presto | ✅ Official |
| `redshift` | Amazon Redshift | ✅ Official |
| `snowflake` | Snowflake | ✅ Official |
| `spark` | Apache Spark | ✅ Official |
| `sqlite` | SQLite | ✅ Official |
| `starrocks` | StarRocks | ✅ Official |
| `teradata` | Teradata | ✅ Community |
| `trino` | Trino | ✅ Official |
| `tsql` | T-SQL (SQL Server) | ✅ Official |

---

## License

Apache License 2.0

## Acknowledgments

This plugin is powered by [SQLGlot](https://github.com/tobymao/sqlglot), an excellent SQL parser and transpiler library created by Toby Mao.
