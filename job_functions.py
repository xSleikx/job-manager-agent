import json
import uuid
from pathlib import Path
from typing import Any, Set, Callable
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from fastapi import FastAPI

# Job class with Pydantic
class Job(BaseModel):
    id: str
    job_role: str
    status: str
    summary: str
    source: str

# uvicorn job_functions:app --reload (use cmd and path to project location)
app = FastAPI(title="Job Management API")

# Root message
@app.get("/")
async def root():
    return {"message": "Welcome to the Job Manager API!"}

# Save jobs here
JOB_FILE = Path(__file__).parent / "jobs.json"

if not JOB_FILE.exists():
    JOB_FILE.write_text("[]")  # empty JSON array

# Helper functions
def read_jobs():
    return json.loads(JOB_FILE.read_text())

def write_jobs(jobs):
    JOB_FILE.write_text(json.dumps(jobs, indent=2))

# Api function
@app.post("/add_job")
async def add_job(job: Job) -> dict:
    job_id = str(uuid.uuid4())
    job_item = {
        "id": job_id,
        "job_role": job.job_role,
        "status": "applied",
        "summary": job.summary,
        "source": job.source
    }
    # Load existing jobs
    jobs = read_jobs()
    jobs.append(job_item)

    # Save back
    write_jobs(jobs)
    return job_item

# Agent functions
def create_job(summary: str, source: str, job_role: str) -> dict:
    job_id = str(uuid.uuid4())
    job_item = {
        "id": job_id,
        "job_role": job_role,
        "status": "applied",
        "summary": summary,
        "source": source
    }
    # Load existing jobs
    jobs = read_jobs()
    jobs.append(job_item)   

    # Save back
    write_jobs(jobs)
    return job_item

@app.delete("/with_jobID")
def delete_job_byid(job_id: str)-> dict:
    jobs = read_jobs()
    for job in jobs:
        if job.get("id") == job_id:
            jobs.remove(job)
            write_jobs(jobs)
            return {"message": f"Job '{job_id}' deleted successfully."}
    return {"error": f"Job with id '{job_id}' not found."}
        
@app.delete("/with_jobrole")
def delete_job_byrole(job_role: str)-> dict:
    jobs = read_jobs()
    for job in jobs:
        if job.get("job_role") == job_role:
            jobs.remove(job)
            write_jobs(jobs)
            return {"message": f"Job '{job_role}' deleted successfully."}
    return {"error": f"Job with id '{job_role}' not found."}
        
@app.get("/jobs")
def list_jobs() -> list:
    jobs = read_jobs()
    return jobs

@app.put("/update_job_status_jobID")
def update_status(job_id: str, status: str) -> dict:
    jobs = read_jobs()
    for job in jobs:
        if job["id"] == job_id:
            job["status"] = status
            write_jobs(jobs)
            return job
    return {"error": "Job not found", "id": job_id}

# Fetch job details from the provided URL, Agent summarizes the content, and prepare data for storage in jobs.json
def scrape_job_page(url: str) -> dict:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return {"error": f"Failed to fetch page: {e}"}

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract title
    title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "No title found"

    # Extract job description
    description_container = soup.find("div", class_="job-description")
    if description_container:
        description = description_container.get_text(separator="\n", strip=True)
    else:
        description = soup.get_text(separator="\n", strip=True)

    return {
        "title": title,
        "description": description,  # Limit can be added description[:3000]
        "link": url
    }

# Register all custom functions that the agent can call to assist the user with job management tasks
user_functions: Set[Callable[..., Any]] = {
    create_job,
    list_jobs,
    update_status,
    scrape_job_page,
    delete_job_byid, # maybe one delete is enough
    delete_job_byrole
}
