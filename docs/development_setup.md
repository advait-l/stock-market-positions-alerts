# Development Setup

This document provides instructions for setting up and running the development environments for both the frontend and backend of the application.

## Frontend

The frontend is a Next.js application located in the `src/frontend` directory.

### Prerequisites

- Node.js (v20.x or later)
- npm or yarn

### Running the Frontend

1. **Navigate to the frontend directory:**
   ```bash
   cd src/frontend
   ```
2. **Install dependencies:**
   ```bash
   npm install
   ```
3. **Run the development server:**
   ```bash
   npm run dev
   ```
   The frontend will be available at http://localhost:3000.

## Backend

The backend is a FastAPI application located in the `src/backend` directory.

### Prerequisites

- Python (v3.9 or later)
- pip

### Running the Backend

1. **Navigate to the backend directory:**
   ```bash
   cd src/backend
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the development server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend will be available at http://localhost:8000.
