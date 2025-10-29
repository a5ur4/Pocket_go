import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from typing import Callable

from database.engine_db import SessionLocal
from services.logs_service import createLog
from database.schemas.logs_schema import LogsCreate

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically log all API requests and responses"""
    
    def __init__(self, app, log_requests: bool = True, log_errors: bool = True):
        super().__init__(app)
        self.log_requests = log_requests
        self.log_errors = log_errors

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Extract request information
        method = request.method
        url = str(request.url)
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Get request body if it's a POST/PUT/PATCH
        request_body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                # Store the body for logging but restore it for the actual request
                body = await request.body()
                request._body = body
                if body:
                    request_body = body.decode('utf-8')[:1000]  # Limit to 1000 chars
            except Exception as e:
                logger.warning(f"Could not read request body: {e}")
        
        response = None
        error_details = None
        
        try:
            # Process the request
            response = await call_next(request)
            status_code = response.status_code
            
        except Exception as e:
            # Log the error
            status_code = 500
            error_details = str(e)
            logger.error(f"Error processing request {method} {path}: {e}")
            
            # Create a 500 response
            from fastapi.responses import JSONResponse
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log to database if enabled
        if self.log_requests or (self.log_errors and (status_code >= 400 or error_details)):
            await self._log_to_database(
                method=method,
                path=path,
                url=url,
                status_code=status_code,
                process_time=process_time,
                client_ip=client_ip,
                user_agent=user_agent,
                request_body=request_body,
                error_details=error_details
            )
        
        # Add processing time to response headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    async def _log_to_database(
        self,
        method: str,
        path: str,
        url: str,
        status_code: int,
        process_time: float,
        client_ip: str,
        user_agent: str,
        request_body: str = None,
        error_details: str = None
    ):
        """Save log entry to database"""
        db: Session = SessionLocal()
        try:
            # Determine log action based on status code
            if error_details:
                action = "API_ERROR"
            elif status_code >= 400:
                action = "API_CLIENT_ERROR"
            else:
                action = "API_REQUEST"
            
            # Create log details
            details = {
                "method": method,
                "path": path,
                "url": url,
                "status_code": status_code,
                "process_time_seconds": round(process_time, 4),
                "client_ip": client_ip,
                "user_agent": user_agent
            }
            
            # Add request body if available
            if request_body:
                details["request_body"] = request_body
            
            # Add error details if available
            if error_details:
                details["error"] = error_details
            
            # Create log entry
            log_create = LogsCreate(
                action=action,
                details=details
            )
            
            createLog(db, log_create)
            
        except Exception as e:
            logger.error(f"Failed to save log to database: {e}")
        finally:
            db.close()