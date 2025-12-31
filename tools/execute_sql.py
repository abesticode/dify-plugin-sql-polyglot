from collections.abc import Generator
from typing import Any
import json

from sqlglot.executor import execute
from sqlglot.errors import ParseError

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class ExecuteSqlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Execute SQL queries against provided data tables.
        """
        # Get parameters
        sql = tool_parameters.get("sql", "")
        tables_str = tool_parameters.get("tables", "")
        dialect = tool_parameters.get("dialect", "")
        
        # Validate required parameters
        if not sql:
            yield self.create_text_message("SQL query is required.")
            return
            
        if not tables_str:
            yield self.create_text_message("Data tables are required.")
            return
        
        try:
            # Parse tables JSON
            try:
                tables = json.loads(tables_str)
            except json.JSONDecodeError as e:
                yield self.create_text_message(f"Invalid tables JSON: {str(e)}")
                return
            
            if not isinstance(tables, dict):
                yield self.create_text_message("Tables must be a JSON object with table names as keys.")
                return
            
            # Validate table structure
            for table_name, table_data in tables.items():
                if not isinstance(table_data, list):
                    yield self.create_text_message(f"Table '{table_name}' must be an array of row objects.")
                    return
                for row in table_data:
                    if not isinstance(row, dict):
                        yield self.create_text_message(f"Each row in table '{table_name}' must be an object.")
                        return
            
            # Handle empty dialect
            parse_dialect = dialect if dialect else None
            
            # Execute the query
            try:
                result = execute(sql, tables=tables, dialect=parse_dialect)
            except Exception as exec_error:
                yield self.create_text_message(f"Query execution failed: {str(exec_error)}")
                yield self.create_json_message({
                    "success": False,
                    "error": str(exec_error),
                    "original_sql": sql
                })
                return
            
            # Convert result to list of dictionaries
            # SQLGlot executor returns a Table object with columns and rows
            result_data = []
            columns = []
            
            if result is not None:
                # Get column names from the result Table
                if hasattr(result, 'columns'):
                    columns = list(result.columns)
                
                # Get rows from the result Table
                if hasattr(result, 'rows'):
                    # result.rows is a list of tuples
                    for row in result.rows:
                        if isinstance(row, tuple):
                            row_dict = {}
                            for i, col in enumerate(columns):
                                # Convert value to JSON-serializable format
                                val = row[i] if i < len(row) else None
                                row_dict[col] = self._serialize_value(val)
                            result_data.append(row_dict)
                        else:
                            result_data.append({"value": self._serialize_value(row)})
                else:
                    # Fallback: iterate over result directly
                    try:
                        for row in result:
                            if isinstance(row, tuple) and columns:
                                row_dict = {}
                                for i, col in enumerate(columns):
                                    val = row[i] if i < len(row) else None
                                    row_dict[col] = self._serialize_value(val)
                                result_data.append(row_dict)
                            elif hasattr(row, '__iter__') and not isinstance(row, str):
                                row_dict = {}
                                row_list = list(row)
                                for i, col in enumerate(columns):
                                    val = row_list[i] if i < len(row_list) else None
                                    row_dict[col] = self._serialize_value(val)
                                result_data.append(row_dict)
                            else:
                                result_data.append({"value": self._serialize_value(row)})
                    except TypeError:
                        # Result is not iterable
                        pass
            
            # Build response
            response = {
                "success": True,
                "row_count": len(result_data),
                "columns": columns,
                "data": result_data,
                "original_sql": sql,
                "dialect": dialect if dialect else "auto-detected"
            }
            
            # Create summary
            summary = f"Query executed successfully. Returned {len(result_data)} row(s)."
            yield self.create_text_message(summary)
            
            # Format result as table if data exists
            if result_data and columns:
                # Create markdown table
                header = "| " + " | ".join(str(col) for col in columns) + " |"
                separator = "| " + " | ".join("---" for _ in columns) + " |"
                rows = []
                for row in result_data[:50]:  # Limit to 50 rows for display
                    row_str = "| " + " | ".join(str(row.get(col, "")) for col in columns) + " |"
                    rows.append(row_str)
                
                table_str = "\n".join([header, separator] + rows)
                if len(result_data) > 50:
                    table_str += f"\n... and {len(result_data) - 50} more rows"
                
                yield self.create_text_message(f"\n**Results:**\n{table_str}")
            
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
            yield self.create_text_message(f"Error executing SQL: {str(e)}")
            yield self.create_json_message(error_response)
    
    def _serialize_value(self, val: Any) -> Any:
        """
        Convert a value to a JSON-serializable format.
        """
        if val is None:
            return None
        elif isinstance(val, (str, int, float, bool)):
            return val
        elif isinstance(val, (list, tuple)):
            return [self._serialize_value(v) for v in val]
        elif isinstance(val, dict):
            return {k: self._serialize_value(v) for k, v in val.items()}
        else:
            # Convert any other type to string
            return str(val)
