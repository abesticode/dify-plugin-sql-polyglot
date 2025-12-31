from collections.abc import Generator
from typing import Any

import sqlglot
from sqlglot.errors import ParseError

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class FormatSqlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Format and prettify SQL queries.
        """
        # Get parameters
        sql = tool_parameters.get("sql", "")
        dialect = tool_parameters.get("dialect", "")
        identify = tool_parameters.get("identify", False)
        normalize = tool_parameters.get("normalize", False)
        
        # Validate required parameters
        if not sql:
            yield self.create_text_message("SQL query is required.")
            return
        
        try:
            # Handle empty dialect (auto-detect)
            parse_dialect = dialect if dialect else None
            
            # Parse and format the SQL
            parsed = sqlglot.parse(sql, dialect=parse_dialect)
            
            if not parsed:
                yield self.create_text_message("Failed to parse SQL query.")
                return
            
            # Format each statement with pretty printing
            formatted_statements = []
            for statement in parsed:
                if statement is not None:
                    formatted_sql = statement.sql(
                        dialect=parse_dialect,
                        pretty=True,
                        identify=identify,
                        normalize=normalize
                    )
                    formatted_statements.append(formatted_sql)
            
            if not formatted_statements:
                yield self.create_text_message("No valid SQL statements found.")
                return
            
            # Join multiple statements
            result_sql = ";\n\n".join(formatted_statements)
            
            # Create response
            response = {
                "original_sql": sql,
                "formatted_sql": result_sql,
                "dialect": dialect if dialect else "auto-detected",
                "options": {
                    "identify": identify,
                    "normalize": normalize
                },
                "statement_count": len(formatted_statements)
            }
            
            summary = f"Successfully formatted {len(formatted_statements)} SQL statement(s)"
            yield self.create_text_message(summary)
            yield self.create_text_message(f"\n**Formatted SQL:**\n```sql\n{result_sql}\n```")
            yield self.create_json_message(response)
            
        except ParseError as e:
            error_response = {
                "success": False,
                "error_type": "ParseError",
                "error_message": str(e),
                "original_sql": sql
            }
            yield self.create_text_message(f"SQL Parse Error: {str(e)}")
            yield self.create_json_message(error_response)
            
        except Exception as e:
            error_response = {
                "success": False,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "original_sql": sql
            }
            yield self.create_text_message(f"Error formatting SQL: {str(e)}")
            yield self.create_json_message(error_response)
