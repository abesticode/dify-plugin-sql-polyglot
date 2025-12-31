from collections.abc import Generator
from typing import Any

import sqlglot
from sqlglot.errors import ParseError

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class TranspileSqlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Transpile SQL from one dialect to another.
        """
        # Get parameters
        sql = tool_parameters.get("sql", "")
        source_dialect = tool_parameters.get("source_dialect", "")
        target_dialect = tool_parameters.get("target_dialect", "")
        pretty = tool_parameters.get("pretty", True)
        
        # Validate required parameters
        if not sql:
            yield self.create_text_message("SQL query is required.")
            return
            
        if not target_dialect:
            yield self.create_text_message("Target dialect is required.")
            return
        
        try:
            # Handle empty source dialect (auto-detect)
            read_dialect = source_dialect if source_dialect else None
            
            # Transpile the SQL
            transpiled = sqlglot.transpile(
                sql,
                read=read_dialect,
                write=target_dialect,
                pretty=pretty
            )
            
            if not transpiled:
                yield self.create_text_message("Failed to transpile SQL query.")
                return
            
            # Join multiple statements if present
            result_sql = ";\n\n".join(transpiled) if len(transpiled) > 1 else transpiled[0]
            
            # Create response
            response = {
                "original_sql": sql,
                "transpiled_sql": result_sql,
                "source_dialect": source_dialect if source_dialect else "auto-detected",
                "target_dialect": target_dialect,
                "statement_count": len(transpiled)
            }
            
            summary = f"Successfully transpiled SQL from {response['source_dialect']} to {target_dialect}"
            yield self.create_text_message(summary)
            yield self.create_text_message(f"\n**Transpiled SQL:**\n```sql\n{result_sql}\n```")
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
            yield self.create_text_message(f"Error transpiling SQL: {str(e)}")
            yield self.create_json_message(error_response)
