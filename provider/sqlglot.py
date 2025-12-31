from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class SqlglotProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate provider credentials.
        SQLGlot is a local library that doesn't require external API credentials.
        We validate by testing if SQLGlot can be imported and used successfully.
        """
        try:
            # Test that sqlglot can be imported and used
            import sqlglot
            
            # Perform a simple parse and transpile operation to verify the library works
            test_sql = "SELECT 1"
            result = sqlglot.transpile(test_sql, read="mysql", write="postgres")
            
            if not result:
                raise ToolProviderCredentialValidationError(
                    "SQLGlot library validation failed: unable to transpile test query"
                )
                
        except ImportError as e:
            raise ToolProviderCredentialValidationError(
                f"SQLGlot library is not installed: {str(e)}"
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(
                f"SQLGlot validation failed: {str(e)}"
            )
