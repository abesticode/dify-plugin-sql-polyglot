from collections.abc import Generator
from typing import Any

import sqlglot
from sqlglot.errors import ParseError

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class ValidateSqlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Validate SQL syntax and detect errors.
        """
        # Get parameters
        sql = tool_parameters.get("sql", "")
        dialect = tool_parameters.get("dialect", "")
        
        # Validate required parameters
        if not sql:
            yield self.create_text_message("SQL query is required.")
            return
        
        try:
            # Handle empty dialect (auto-detect)
            parse_dialect = dialect if dialect else None
            
            # Attempt to parse the SQL - this will raise ParseError if invalid
            parsed = sqlglot.parse(sql, dialect=parse_dialect)
            
            # Check if any statements were parsed
            valid_statements = [stmt for stmt in parsed if stmt is not None]
            
            if not valid_statements:
                yield self.create_text_message("No valid SQL statements found in the query.")
                yield self.create_json_message({
                    "valid": False,
                    "error": "No valid SQL statements found",
                    "original_sql": sql
                })
                return
            
            # Check for any warnings or issues with each statement
            warnings = []
            statement_info = []
            
            for i, stmt in enumerate(valid_statements):
                stmt_type = type(stmt).__name__
                statement_info.append({
                    "index": i + 1,
                    "type": stmt_type,
                    "sql": stmt.sql(pretty=True)
                })
            
            # Build successful response
            response = {
                "valid": True,
                "dialect": dialect if dialect else "auto-detected",
                "statement_count": len(valid_statements),
                "statements": statement_info,
                "warnings": warnings,
                "original_sql": sql
            }
            
            summary = f"✓ SQL is valid! Found {len(valid_statements)} statement(s)."
            if warnings:
                summary += f" ({len(warnings)} warning(s))"
            
            yield self.create_text_message(summary)
            
            # List statement types
            stmt_types = [s["type"] for s in statement_info]
            yield self.create_text_message(f"Statement types: {', '.join(stmt_types)}")
            
            yield self.create_json_message(response)
            
        except ParseError as e:
            # Extract detailed error information
            error_info = {
                "valid": False,
                "error_type": "ParseError",
                "error_message": str(e),
                "original_sql": sql,
                "dialect": dialect if dialect else "auto-detected"
            }
            
            # Try to extract structured error details if available
            if hasattr(e, 'errors') and e.errors:
                error_details = []
                for err in e.errors:
                    if isinstance(err, dict):
                        error_details.append({
                            "description": err.get("description", "Unknown error"),
                            "line": err.get("line"),
                            "col": err.get("col"),
                            "start_context": err.get("start_context", ""),
                            "highlight": err.get("highlight", ""),
                            "end_context": err.get("end_context", "")
                        })
                error_info["error_details"] = error_details
            
            error_message = f"✗ SQL Validation Failed: {str(e)}"
            yield self.create_text_message(error_message)
            yield self.create_json_message(error_info)
            
        except Exception as e:
            error_response = {
                "valid": False,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "original_sql": sql
            }
            yield self.create_text_message(f"Error validating SQL: {str(e)}")
            yield self.create_json_message(error_response)
