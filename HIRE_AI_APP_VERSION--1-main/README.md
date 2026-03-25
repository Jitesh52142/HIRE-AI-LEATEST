# Hire AI

Hire AI is a sophisticated, AI-driven recruitment platform built with Flask, designed to help companies streamline their hiring process. It provides a multi-step form for defining job requirements, automates data submission to a webhook for custom workflows, and displays real-time candidate insights pulled from public Google Sheets.

## Features

- **Multi-Step Form**: A clean, user-friendly form wizard for capturing detailed job descriptions.
- **AI Integration**: Submits data to an n8n webhook to trigger external AI-powered candidate searches.
- **Dynamic Dashboards**: Displays real-time candidate data and hiring history fetched directly from public Google Sheets.
- **Secure Authentication**: User registration and login managed with Flask-Login and Bcrypt.
- **Protected Admin Panel**: An administrative view of all database collections, accessible only to an admin user.
- **Modular Design**: Built with Flask Blueprints for a scalable and maintainable codebase.

## Prerequisites

- Python 3.8+
- MongoDB Atlas account (free tier is sufficient)
- A public Google Sheet with a specific format for candidate data.
- An n8n webhook URL to receive form submissions.

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/hire_ai.git](https://github.com/your-username/hire_ai.git)
    cd hire_ai
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**
    Create a `.env` file in the root directory and fill it with your credentials:
    ```


4.  **Run the application:**
    ```bash
    python run.py
    ```

The application will be running at `http://127.0.0.1:5000`.

## Deployment

This application is configured for easy deployment on platforms like Render or Heroku using the provided `Procfile` and `render.yaml` files. Ensure you set your environment variables correctly on the hosting platform.

---

## Contact

For any questions or support, please contact Jitesh Bawaskar at `jiteshbawaskar05@gmail.com`.
