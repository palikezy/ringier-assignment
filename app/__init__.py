__all__ = ["app"]

from .main import app

# For debugging
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
