**Advanced AI-Powered Task Manager Web Application
📌 Project Overview**
A full-stack Task Manager web application built using Python, Flask, SQLite, and session-based user authentication. It integrates the Google Gemini API to provide intelligent features like Natural Language Task Creation and an AI Daily Productivity Coach. Designed for productivity, it also includes a Pomodoro timer, subtask checklists, and a Zen Focus Mode to help users stay organized and focused.

**🚀 Key Features**
1. User Authentication & Security: Secure signup, login, and logout workflows with user-specific session tracking.

2. AI Natural Language Task Creation: Type tasks in plain English (e.g., "Complete Python assignment tomorrow at 4 PM high priority"), and the AI automatically extracts details and saves them to the database.

3. AI Daily Productivity Companion: Analyzes pending tasks and generates a personalized, motivational tip every day.

4. Zen Focus Mode & Violation Tracker: Locks or blurs the screen for deep focus sessions and tracks tab switches as violations to minimize distractions.

5. Pomodoro Focus Timer: Customizable countdown timers (30m, 45m, 60m) with built-in alarm sounds and sound previews.

6. Subtasks & Interactive Checklists: Break down main tasks into manageable micro-steps.

7. Focus Analytics: Tracks focus duration and violation counts to help monitor productivity habits.

**🛠 Technologies Used**
**Backend**: Python, Flask, SQLite, Session Management
**AI Integration**: Google Gemini API (google-genai library)
**Frontend**: HTML5, CSS3, Vanilla JavaScript, FontAwesome
**Utilities**: Canvas Confetti for completion animations, Web Audio API for alerts

**📂 Database Schema**
**users**: Stores user credentials (id, username, password)
**tasks**: Stores task attributes (id, username, title, description, category, priority, recurrence, alarm_sound, due_date, due_time, completed)
**subtasks**: Stores micro-tasks linked to main tasks via foreign keys (id, task_id, title, completed)

**⚙️ Modular Architecture & Workflow**
1.**app.py**: The core Flask server managing HTTP routes, user authentication sessions, SQLite database connections, and Google Gemini AI API requests.
2. **Templates (index.html, login.html, Signup.html)**: Responsive HTML interfaces featuring dynamic themes, modals, and interactive frontend controls.
3. **Execution Workflow**: Users authenticate securely $\rightarrow$ create tasks manually or through AI natural language prompts $\rightarrow$ the Flask backend processes and stores data $\rightarrow$ users manage workflows while AI features assist with smart organization and motivation.

**▶️ How to Run the Project**
**Navigate to the Project Directory**
**Open your terminal or command prompt inside the project folder.**

**Install Required Packages**

**Bash**
pip install flask google-genai
Configure Your Gemini API Key
Open app.py and replace "YOUR_GEMINI_API_KEY" with your actual Google Gemini API key.

**Run the Application**

**Bash**
python app.py
**Open in Browser**
Open your web browser and navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000) to start using the application!
