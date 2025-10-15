# HealthCore: Smart Community Health Monitoring and Early Warning System

[](https://www.google.com/search?q=https://github.com/VaibhavUPratap/HealthCore/stargazers)
[](https://www.google.com/search?q=https://github.com/VaibhavUPratap/HealthCore/network/members)
[](https://www.google.com/search?q=https://github.com/VaibhavUPratap/HealthCore/blob/main/LICENSE)

## 🌐 Live Demo

Check out the deployed application:

[healthcore.onrender.com](https://healthcore.onrender.com)

-----

## 💡 Project Overview

**HealthCore** is a Smart Health Surveillance and Early Warning System designed to detect, monitor, and help prevent outbreaks of **water-borne diseases** in vulnerable, remote communities, with a specific focus on the rural Northeastern Region (NER) of India.

Developed as a hackathon project, the system integrates community-level data collection, environmental monitoring, and **Artificial Intelligence** to provide real-time, actionable alerts to health officials.

### Problem Statement

Water-borne diseases such as diarrhea, cholera, typhoid, and hepatitis A are common in rural and tribal areas of the NER, often linked to contaminated water and poor sanitation. The remote terrain and delayed medical response necessitate a proactive, digital solution to monitor and respond to emerging health threats in a timely manner.

## ✨ Key Features

HealthCore delivers a multi-faceted approach to public health monitoring:

1.  **AI-Driven Outbreak Prediction:** Uses **AI/ML models** (developed in Jupyter Notebooks) to detect patterns and **predict potential outbreaks** based on reported symptoms, water quality reports, and seasonal trends.
2.  **Community-Level Data Collection:** A mobile-friendly interface for local clinics, **ASHA workers**, and community volunteers to report health data via mobile apps or SMS.
3.  **Water Quality Integration:** Designed to integrate with low-cost water testing kits or **IoT sensors** to monitor critical water source contamination parameters (e.g., turbidity, pH, bacterial presence).
4.  **Real-Time Alert System:** Provides immediate alerts to district health officials and local governance bodies to mobilize rapid response teams.
5.  **Health Department Dashboard:** Offers comprehensive dashboards for health officials to **visualize hotspots**, track intervention effectiveness, and allocate resources efficiently.
6.  **Accessibility Focus:** Includes a **multilingual mobile interface** with support for offline functionality and tribal languages to maximize adoption in remote areas.

-----

## 💻 Technology Stack

| Category | Technology | Notes |
| :--- | :--- | :--- |
| **Backend** | **Python** (Flask) | Main application logic and routing. |
| **Data Science/AI**| **Jupyter Notebook** | Used for AI/ML model development and analysis. |
| **Frontend** | **HTML, CSS, JavaScript** | User-facing interface and dashboards. |
| **Database** | **SQLite** | Lightweight, file-based database for portability (Migrated from MongoDB). |
| **Deployment**| **Render** | Platform used for the live demo deployment. |

### ⚠️ Database Migration Notice

**The project database has been migrated from MongoDB to SQLite.**

Due to external connection issues, the project now utilizes **SQLite** as its database backend. This provides a lightweight, serverless solution perfect for development and small deployments.

**Configuration:**
The database path is set in the **`.env`** file:

```bash
# .env
SQLITE_DB_PATH=healthcore.db
```

-----

## ⚙️ Local Setup and Installation

Follow these steps to get a local copy of **HealthCore** running on your machine.

### Prerequisites

  * **Python 3.8+**
  * `pip` (Python package installer)

### 1\. Clone the Repository

```bash
git clone https://github.com/VaibhavUPratap/HealthCore.git
cd HealthCore
```

### 2\. Set up the Backend (Python)

Create and activate a virtual environment, then install the required Python packages:

```bash
# Create and activate environment (Linux/macOS)
python3 -m venv venv
source venv/bin/activate

# For Windows (PowerShell/CMD)
# python -m venv venv
# .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3\. Environment Configuration

Create a file named **`.env`** in the project root directory and add the database path configuration:

```bash
# .env
SQLITE_DB_PATH=healthcore.db
```

The `healthcore.db` file will be automatically created when the application is run.

### 4\. Run the Application

Start the application using the runner script:

```bash
# Ensure your virtual environment is active
python run.py
```

The application should now be accessible in your web browser, typically at **`http://127.0.0.1:5000`**.

-----

## 🤝 Contributing

This was a hackathon project, and contributions are welcome to expand its features, improve the AI model, or enhance the UI/UX.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add AmazingFeature details'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](https://www.google.com/search?q=https://github.com/VaibhavUPratap/HealthCore/blob/main/LICENSE) file for details.
