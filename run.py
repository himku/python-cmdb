import uvicorn
import logging

# Disable uvicorn access logs
logging.getLogger("uvicorn.access").disabled = True
logging.getLogger("uvicorn.error").disabled = True

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=10001,
        reload=True,
        log_level="error"  # Only show error logs
    ) 