from lightspun.config import get_config

if __name__ == "__main__":
    import uvicorn
    
    # Load configuration (logging setup is automatic)
    config = get_config()
    
    # Import app after configuration and logging are loaded
    from lightspun.app import app
    
    # Run with configuration settings
    uvicorn.run(
        app,
        host=config.server.host,
        port=config.server.port,
        reload=config.server.reload,
        workers=config.server.workers if not config.server.reload else 1
    )