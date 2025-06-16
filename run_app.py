import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
