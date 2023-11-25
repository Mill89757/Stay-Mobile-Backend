# Stay-Mobile-Backend

Welcome to the Stay Mobile backend repository! This FastAPI-based backend is designed to power the Stay Mobile application.

## Setup Environment

Follow these steps to set up your development environment:

### 1. Create a Virtual Environment

```bash
python3.10 -m venv venv
```

### 2. Activate the Virtual Environment

On Windows, run the following command in PowerShell:

```bash
.\venv\Scripts\Activate.ps1
```

On Unix or MacOS, use this command:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
python3.10 -m pip install -r requirements.txt
```

Make sure to install uvicorn separately:

```bash
pip install uvicorn
```

### 4. Run the Application

```bash
uvicorn main:app --reload
```
