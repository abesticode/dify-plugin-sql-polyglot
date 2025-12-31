# Privacy Policy

## SQL Polyglot Plugin

**Last Updated:** January 1, 2026

### Overview

The SQL Polyglot plugin is designed with privacy as a priority. This plugin processes SQL queries locally and does not transmit data to external services.

### Data Collection

This plugin **does not collect** any personal data or user information. Specifically:

- **No SQL queries are stored** - All SQL processing is done in-memory and discarded after execution
- **No usage tracking** - We do not track how you use the plugin
- **No analytics** - No analytics or telemetry data is collected
- **No external API calls** - All processing is done locally using the SQLGlot library

### Data Processing

When you use this plugin:

1. **SQL Transpiling** - Your SQL query is parsed and converted to another dialect entirely in-memory
2. **SQL Formatting** - Your SQL is reformatted locally without any external transmission
3. **SQL Analysis** - Metadata is extracted from your SQL locally
4. **SQL Validation** - Syntax checking is performed locally
5. **SQL Optimization** - Query optimization is performed locally
6. **SQL Execution** - Queries are executed against provided JSON data locally

### Third-Party Services

This plugin does **not** use any third-party services. All functionality is provided by the open-source [SQLGlot](https://github.com/tobymao/sqlglot) library, which runs entirely locally.

### Data Retention

No data is retained. All SQL queries and results are:
- Processed in-memory only
- Not logged or stored
- Discarded immediately after processing

### Security

- All processing occurs within the Dify plugin runtime environment
- No credentials are required to use this plugin
- No network connections are made to external services

### Changes to This Policy

We may update this privacy policy from time to time. Any changes will be reflected in the "Last Updated" date above.

### Contact

For any privacy-related questions or concerns, please contact:

- **Author:** abesticode
- **GitHub:** [https://github.com/abesticode](https://github.com/abesticode)

### Open Source

This plugin is open source and its code can be audited at any time. The complete source code is available in the plugin package.