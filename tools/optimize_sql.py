from collections.abc import Generator
from typing import Any
import json

import sqlglot
from sqlglot.optimizer import optimize
from sqlglot.errors import ParseError

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class OptimizeSqlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Optimize SQL queries using SQLGlot's optimizer.
        """
        # Get parameters
        sql = tool_parameters.get("sql", "")
        dialect = tool_parameters.get("dialect", "")
        schema_str = tool_parameters.get("schema", "")
        
        # Validate required parameters
        if not sql:
            yield self.create_text_message("SQL query is required.")
            return
        
        try:
            # Handle empty dialect (auto-detect)
            parse_dialect = dialect if dialect else None
            
            # Parse the SQL
            parsed = sqlglot.parse_one(sql, dialect=parse_dialect)
            
            if parsed is None:
                yield self.create_text_message("Failed to parse SQL query.")
                return
            
            # Parse schema if provided
            schema = None
            if schema_str:
                try:
                    schema = json.loads(schema_str)
                except json.JSONDecodeError as e:
                    yield self.create_text_message(f"Invalid schema JSON: {str(e)}")
                    return
            
            # Optimize the query
            optimization_note = None
            try:
                if schema:
                    optimized = optimize(parsed, schema=schema, dialect=parse_dialect)
                else:
                    optimized = optimize(parsed, dialect=parse_dialect)
            except Exception as opt_error:
                # Some optimizations may fail without schema, try basic optimization
                optimized = parsed
                optimization_note = f"Note: Full optimization requires schema. Basic formatting applied. ({str(opt_error)})"
            
            # Generate optimized SQL
            optimized_sql = optimized.sql(dialect=parse_dialect, pretty=True)
            
            # Build response
            response = {
                "original_sql": sql,
                "optimized_sql": optimized_sql,
                "dialect": dialect if dialect else "auto-detected",
                "schema_provided": bool(schema),
                "optimization_applied": True
            }
            
            if optimization_note:
                response["note"] = optimization_note
            
            summary = "Successfully optimized SQL query"
            if optimization_note:
                summary += f"\n{optimization_note}"
            
            yield self.create_text_message(summary)
            yield self.create_text_message(f"\n**Optimized SQL:**\n```sql\n{optimized_sql}\n```")
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
            yield self.create_text_message(f"Error optimizing SQL: {str(e)}")
            yield self.create_json_message(error_response)
