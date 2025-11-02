"""FastMCP logging middleware for request/response logging."""

import time
from typing import Any
from fastmcp.server.middleware import Middleware, MiddlewareContext

from agentic_investor.utils.logger import get_debug_logger

logger = get_debug_logger(__name__)


class RequestLoggingMiddleware(Middleware):
    """Middleware that logs incoming MCP requests with timing information."""

    async def on_message(self, context: MiddlewareContext, call_next) -> Any:
        """Log all incoming MCP messages with timing.
        
        Args:
            context: The middleware context containing request information
            call_next: Function to call the next middleware or handler
            
        Returns:
            The result from the next handler in the chain
        """
        start_time = time.perf_counter()
        method = context.method
        source = getattr(context, 'source', 'unknown')
        
        logger.debug(f"[REQUEST] Method: {method} | Source: {source}")
        
        try:
            result = await call_next(context)
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.debug(f"[RESPONSE] Method: {method} | Duration: {duration_ms:.2f}ms | Status: SUCCESS")
            return result
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.debug(f"[ERROR] Method: {method} | Duration: {duration_ms:.2f}ms | Error: {type(e).__name__}: {str(e)}")
            raise

    async def on_request(self, context: MiddlewareContext, call_next) -> Any:
        """Log specific request details for request-type messages.
        
        Args:
            context: The middleware context containing request information
            call_next: Function to call the next middleware or handler
            
        Returns:
            The result from the next handler in the chain
        """
        method = context.method
        logger.debug(f"[REQUEST_DETAIL] Processing {method} request")
        
        result = await call_next(context)
        
        logger.debug(f"[REQUEST_DETAIL] Completed {method} request")
        return result
