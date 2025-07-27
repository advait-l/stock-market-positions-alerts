# Deployment

This document outlines the deployment process for both the frontend and backend of the Stock Market Positions Alerts application.

## Backend Deployment (Python/Flask)

The backend is a Python application, likely using a framework like Flask or FastAPI.

### Prerequisites

- Python 3.8+
- `pip` for package management

### Steps

1.  **Navigate to the backend directory:**

    ```bash
    cd src/backend
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**

    - On macOS and Linux:
      ```bash
      source venv/bin/activate
      ```
    - On Windows:
      ```bash
      venv\Scripts\activate
      ```

4.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the application:**
    The command to run the application will depend on the specific framework and entry point. A common approach for a Flask application would be:
    ```bash
    flask run
    ```
    Or for a production-ready setup using a WSGI server like Gunicorn:
    ```bash
    gunicorn -w 4 'app:create_app()'
    ```
    _Note: The entry point `app:create_app()` might need to be adjusted based on the actual application structure in `src/backend/app`._

### Deployment to a Server (e.g., using Docker)

For a more robust and portable deployment, you can containerize the backend using Docker.

1.  **Create a `Dockerfile` in `src/backend`:**

    ```dockerfile
    # Use an official Python runtime as a parent image
    FROM python:3.9-slim

    # Set the working directory in the container
    WORKDIR /app

    # Copy the requirements file into the container
    COPY requirements.txt .

    # Install any needed packages specified in requirements.txt
    RUN pip install --no-cache-dir -r requirements.txt

    # Copy the rest of the application's code
    COPY app/ ./app

    # Make port 8000 available to the world outside this container
    EXPOSE 8000

    # Define environment variable
    ENV NAME World

    # Run the application
    CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:create_app()"]
    ```

2.  **Build the Docker image:**

    ```bash
    cd src/backend
    docker build -t stock-alerts-backend .
    ```

3.  **Run the Docker container:**
    ```bash
    docker run -p 8000:8000 stock-alerts-backend
    ```

## Frontend Deployment (Next.js)

The frontend is a Next.js application.

### Prerequisites

- Node.js 18.x or later
- `npm` or `yarn`

### Steps

1.  **Navigate to the frontend directory:**

    ```bash
    cd src/frontend
    ```

2.  **Install dependencies:**

    ```bash
    npm install
    ```

3.  **Build the application for production:**

    ```bash
    npm run build
    ```

4.  **Start the production server:**
    ```bash
    npm start
    ```
    The application will typically be available at `http://localhost:3000`.

### Deployment to Vercel

Vercel is the recommended platform for deploying Next.js applications.

1.  **Install the Vercel CLI:**

    ```bash
    npm i -g vercel
    ```

2.  **Login to your Vercel account:**

    ```bash
    vercel login
    ```

3.  **Deploy the application:**
    From the `src/frontend` directory, run:
    ```bash
    vercel --prod
    ```
    Vercel will automatically detect the Next.js project, build it, and deploy it.

### Deployment to a Server (e.g., using Docker)

1.  **Create a `Dockerfile` in `src/frontend`:**

    ```dockerfile
    # Install dependencies only when needed
    FROM node:18-alpine AS deps
    # Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
    RUN apk add --no-cache libc6-compat
    WORKDIR /app

    # Install dependencies based on the preferred package manager
    COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
    RUN \
      if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
      elif [ -f package-lock.json ]; then npm ci; \
      elif [ -f pnpm-lock.yaml ]; then yarn global add pnpm && pnpm i --frozen-lockfile; \
      else echo "Lockfile not found." && exit 1; \
      fi


    # Rebuild the source code only when needed
    FROM node:18-alpine AS builder
    WORKDIR /app
    COPY --from=deps /app/node_modules ./node_modules
    COPY . .

    # Next.js collects completely anonymous telemetry data about general usage.
    # Learn more here: https://nextjs.org/telemetry
    # Uncomment the following line in case you want to disable telemetry during the build.
    # ENV NEXT_TELEMETRY_DISABLED 1

    RUN npm run build

    # Production image, copy all the files and run next
    FROM node:18-alpine AS runner
    WORKDIR /app

    ENV NODE_ENV production
    # Uncomment the following line in case you want to disable telemetry during runtime.
    # ENV NEXT_TELEMETRY_DISABLED 1

    RUN addgroup --system --gid 1001 nodejs
    RUN adduser --system --uid 1001 nextjs

    # You only need to copy next.config.js if you are NOT using the default configuration
    COPY --from=builder /app/public ./public
    COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
    COPY --from=builder /app/node_modules ./node_modules
    COPY --from=builder /app/package.json ./package.json

    USER nextjs

    EXPOSE 3000

    ENV PORT 3000

    CMD ["npm", "start"]
    ```

2.  **Build the Docker image:**

    ```bash
    cd src/frontend
    docker build -t stock-alerts-frontend .
    ```

3.  **Run the Docker container:**
    ```bash
    docker run -p 3000:3000 stock-alerts-frontend
    ```
