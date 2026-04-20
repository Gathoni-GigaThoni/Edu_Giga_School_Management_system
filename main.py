from fastapi import FastAPI

app = FastAPI(title="School Management System")

@app.get("/")
def read_root():
    return {"message": "Welcome to the School Management System"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}