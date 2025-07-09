# Aeonis UI

The Aeonis UI is the frontend web application for the Aeonis observability platform. It's built with React and Vite, and it communicates with the `aeonis-server` to visualize trace data and interact with the AI chat.

## Getting Started

These instructions will guide you through setting up and running the UI on your local machine.

### 1. Prerequisites

-   **Node.js and npm:** Make sure you have a recent version of Node.js and npm installed.
-   **Running `aeonis-server`:** The UI application expects the `aeonis-server` to be running at `http://localhost:8000`. Please follow the setup instructions in `apps/aeonis-server/README.md` first.

### 2. Installation

1.  **Navigate to the UI directory:**
    ```bash
    cd apps/aeonis-ui
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

### 3. Running the Development Server

Once the dependencies are installed, you can start the Vite development server.

```bash
npm run dev
```

The UI will be available at `http://localhost:5173` (or another port if 5173 is in use). The console will display the correct address when the server starts.

## How It Works

The UI provides the following features:

-   **Project-based Trace Viewing:** Enter a Project ID to fetch and display all associated traces.
-   **Trace Detail Visualization:** Click on a trace to see a detailed waterfall view of its spans.
-   **AI Chat:** Use the chat interface to ask natural language questions about your project's trace data. The chat is automatically associated with the Project ID you entered.