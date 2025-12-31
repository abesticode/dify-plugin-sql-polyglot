from collections.abc import Generator
from typing import Any

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class AnalyzeSqlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Analyze SQL queries and extract metadata.
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
            
            # Parse the SQL
            parsed = sqlglot.parse_one(sql, dialect=parse_dialect)
            
            if parsed is None:
                yield self.create_text_message("Failed to parse SQL query.")
                return
            
            # Extract tables
            tables = []
            for table in parsed.find_all(exp.Table):
                table_info = {
                    "name": table.name,
                    "alias": table.alias if table.alias else None,
                    "db": table.db if hasattr(table, 'db') and table.db else None,
                    "catalog": table.catalog if hasattr(table, 'catalog') and table.catalog else None
                }
                if table_info not in tables:
                    tables.append(table_info)
            
            # Extract columns
            columns = []
            for column in parsed.find_all(exp.Column):
                column_info = {
                    "name": column.name,
                    "table": column.table if column.table else None,
                    "alias_or_name": column.alias_or_name
                }
                if column_info not in columns:
                    columns.append(column_info)
            
            # Extract aliases (from SELECT expressions)
            aliases = []
            for select in parsed.find_all(exp.Select):
                for projection in select.expressions:
                    if hasattr(projection, 'alias') and projection.alias:
                        aliases.append({
                            "alias": projection.alias,
                            "expression": projection.this.sql() if hasattr(projection, 'this') else str(projection)
                        })
            
            # Extract functions
            functions = []
            for func in parsed.find_all(exp.Func):
                func_name = type(func).__name__
                if func_name not in [f["name"] for f in functions]:
                    functions.append({
                        "name": func_name,
                        "sql": func.sql()
                    })
            
            # Extract joins
            joins = []
            for join in parsed.find_all(exp.Join):
                join_info = {
                    "type": join.kind if hasattr(join, 'kind') and join.kind else "INNER",
                    "table": join.this.name if hasattr(join.this, 'name') else str(join.this),
                    "on_condition": join.args.get("on").sql() if join.args.get("on") else None
                }
                joins.append(join_info)
            
            # Extract subqueries
            subqueries = []
            for subquery in parsed.find_all(exp.Subquery):
                subqueries.append({
                    "alias": subquery.alias if subquery.alias else None,
                    "sql": subquery.this.sql() if hasattr(subquery, 'this') else str(subquery)
                })
            
            # Detect query type
            query_type = type(parsed).__name__
            
            # Extract WHERE conditions
            where_conditions = []
            for where in parsed.find_all(exp.Where):
                where_conditions.append(where.this.sql() if hasattr(where, 'this') else str(where))
            
            # Extract GROUP BY
            group_by = []
            for group in parsed.find_all(exp.Group):
                for expr in group.expressions:
                    group_by.append(expr.sql())
            
            # Extract ORDER BY
            order_by = []
            for order in parsed.find_all(exp.Order):
                for expr in order.expressions:
                    order_by.append({
                        "expression": expr.this.sql() if hasattr(expr, 'this') else str(expr),
                        "desc": expr.args.get("desc", False)
                    })
            
            # Build response
            response = {
                "query_type": query_type,
                "tables": tables,
                "columns": columns,
                "aliases": aliases,
                "functions": functions,
                "joins": joins,
                "subqueries": subqueries,
                "where_conditions": where_conditions,
                "group_by": group_by,
                "order_by": order_by,
                "dialect": dialect if dialect else "auto-detected",
                "original_sql": sql
            }
            
            # Create summary
            summary_parts = [
                f"Query Type: {query_type}",
                f"Tables: {len(tables)}",
                f"Columns: {len(columns)}",
                f"Joins: {len(joins)}",
                f"Functions: {len(functions)}"
            ]
            summary = "SQL Analysis:\n- " + "\n- ".join(summary_parts)
            
            yield self.create_text_message(summary)
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
            yield self.create_text_message(f"Error analyzing SQL: {str(e)}")
            yield self.create_json_message(error_response)
