
# Elevator Crowd Management System

## Project Overview

The **Elevator Crowd Management System** aims to solve the issue of overcrowding in elevators, particularly in university campuses. By using real-time monitoring with cameras and predictive analytics, the system helps users and admins manage elevator crowd density and optimize usage.

## Problem Statement
Overcrowding in university elevators leads to inefficiency and discomfort. This system provides real-time monitoring, prediction, and alerts for crowd density to enhance elevator operations.

## Features
1. **Real-Time Monitoring**: 
   - Cameras capture real-time footage.
   - The system processes this to detect crowd density.

2. **Crowd Detection (OpenVINO)**: 
   - Detects individuals in queues using AI and OpenVINO.

3. **Real-Time Alerts**: 
   - Alerts users and admins through the web interface regarding the current elevator status.

4. **Predictive Modeling**: 
   - Uses historical data to predict crowd density and future usage patterns.

## System Architecture
- **Frontend**:
  - Displays real-time crowd status for users.
  - **Tech**: Next.js, TailwindCSS
  - **Location**: `/ecm/app`, `/ecm/public`

- **Backend**:
  - Manages data processing and admin functionalities.
  - **Tech**: Python, Firebase, OpenVINO
  - **Location**: `/server`

- **Firebase Integration**:
  - Stores real-time crowd data and performs backend calculations.

- **Dashboard**:
  - **User Dashboard**: Shows crowd density and suggests optimal times for elevator usage.
  - **Admin Dashboard**: Allows control over camera systems and sends alerts.
  - Access the live system: [Elevator Crowd Management Dashboard](https://elevator-crowd-management.vercel.app/)

## Code Structure
```
ElevatorCrowdManagement/
│
├── ecm/
│   ├── app/                # Next.js app for user interface
│   ├── public/             # Static files and UI assets
│   ├── README.md           # Frontend-specific README
│   ├── package.json        # Dependencies for frontend
│   ├── tailwind.config.js  # Tailwind CSS configuration
│   ├── next.config.js      # Next.js configuration
│
├── server/                 
│   ├── admin_api.py        # Backend logic for admin operations
│   ├── backend.py          # Core backend logic
│   ├── multicam_server.py  # Handles multiple camera feeds
│   ├── templates/          # HTML templates for the backend
│   ├── requirements.txt    # Python dependencies
│
├── LICENSE                 # License information
├── README.md               # Main README file
```

## Key Benefits
- **Time Optimization**: Users can avoid crowded elevators by checking real-time data.
- **Safety**: Prevents overcrowding, enhancing safety and user experience.
- **Efficiency**: Optimizes elevator operations based on usage patterns.

## Tech Stack
- **Frontend**: Next.js, TailwindCSS
- **Backend**: Python, Firebase, OpenVINO
- **Database**: Firebase Realtime Database

## How to Run the Project Locally

### Frontend (Next.js)
1. Navigate to the `ecm` directory:
   ```bash
   cd ecm
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the frontend server:
   ```bash
   npm run dev
   ```

4. Open the app in your browser:
   ```
   http://localhost:3000
   ```

### Backend (Python)
1. Navigate to the `server` directory:
   ```bash
   cd server
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the backend server:
   ```bash
   python backend.py
   ```

4. The backend will be available at:
   ```
   http://localhost:8000
   ```

## Deployment
The project is deployed on Vercel. You can access the live version here:  
[Elevator Crowd Management System](https://elevator-crowd-management.vercel.app/)

## License
This project is licensed under the MIT License.
