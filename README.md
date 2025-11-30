# **Azure Job Agent (GPT-4o) for Job Applications**

This project provides a **FastAPI-based Job Management API** combined with an **Azure AI Agent** using GPT-4o for managing job applications.  
It supports creating, listing, updating, and deleting job records stored in a local JSON file, as well as scraping job details from URLs.  

The base tutorial with Azure can be found here:  
https://microsoftlearning.github.io/mslearn-ai-agents/Instructions/03-agent-custom-functions.html.

---

## **Project Structure**
```
.
├── job_functions.py    # FastAPI app with job management endpoints and helper functions
├── main.py             # Azure Agent integration and chat loop
├── jobs.json           # Local storage for job applications
├── requirements.txt    # Python dependencies
├── .env                # Environment variables for Azure configuration
└── README.md           # Project documentation
```

---

## **Features**
- **FastAPI Endpoints**
  - `GET /` – Welcome message
  - `POST /add_job` – Add a new job application
  - `GET /jobs` – List all jobs
  - `DELETE /with_jobID` – Delete job by ID
  - `DELETE /with_jobrole` – Delete job by role
  - `PUT /update_job_status_jobID` – Update job status by ID

- **Azure Agent Integration**
  - Automatically calls local functions for job management
  - Handles user prompts and job-related queries
  - Persists job applications without user confirmation

---

## **Installation**
Azure Cloud Shell can also be used like in the tutorial.  
**Need Azure CLI to login to Azure if you run on Windows.**

1. **Clone the repository**
   ```bash
   git clone https://github.com/xSleikx/job-manager-agent.git
   cd job-manager-agent

   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## **Requirements**
```
python-dotenv
azure-identity
azure-ai-agents
fastapi
uvicorn
requests
beautifulsoup4
pydantic
```

---

## **Environment Variables**
Create a `.env` file with:
```
PROJECT_ENDPOINT=https://<your-azure-endpoint>
MODEL_DEPLOYMENT_NAME=gpt-4o
```

---

## **Run Instructions**
- **Start FastAPI server**:
   ```bash
   uvicorn job_functions:app --reload
   ```
   Access API docs at: http://127.0.0.1:8000/docs

- **Run Azure Agent**:
   ```bash
   python main.py
   ```

---

## **Example Usage (FastAPI)**
Use http://127.0.0.1:8000/docs if you want to try out with **Swagger**.

- **Add a job via API**:
   ```bash
   curl -X POST "http://127.0.0.1:8000/add_job"         -H "Content-Type: application/json"         -d '{"job_role":"Data Scientist","summary":"Analyze data","source":"LinkedIn"}'
   ```

---

## **Agent Instructions**
The agent:
- Extracts job info from text or URLs
- Summarizes job details
- Saves applications directly to `jobs.json`
- Prevents duplicate entries and prompts user if job already exists
