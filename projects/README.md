# Portfolio Projects for the Software Engineer Resume (ECE fresher)

| # | Project | Stack | Tested |
|---|---|---|---|
| 1 | Customer Churn Prediction | Python, Pandas, Scikit-learn | Ran end to end, results in `outputs/` |
| 2 | Task Manager REST API | Python, Flask, SQLAlchemy, MySQL | 5 automated tests pass |
| 3 | Library Management System | Java, JDBC, MySQL | 13 automated checks pass (SQLite); menu smoke-tested |
| 4 | IoT Sensor Data Dashboard | Python, ESP32, MQTT | 8 unit tests + end-to-end run through a real MQTT broker |
| 5 | Job Application Tracker (full-stack web) | React, Vite, Django, DRF, JWT | 5 API tests pass; live end-to-end: login → create → stats → list |

## Read this before you put them on your resume
1. **Understand every line.** Interviewers ask you to explain your code. Read each project, run it, and change something small (a new endpoint, a new feature, a different model) so it becomes yours.
2. **Be honest about data and hardware.** Project 1 uses synthetic data (a real Kaggle dataset can be swapped in). Project 4 was tested with a simulator, not a physical ESP32, so only claim hardware work after you flash and run the sketch yourself.
3. **Use your real numbers.** Project 1 measured about 77% accuracy (Random Forest) and 0.79 ROC-AUC (Logistic Regression) on this data, so use those figures, or your own after any changes.
4. **MySQL:** projects 2 and 3 were tested with SQLite because MySQL was not available here. Run them once against MySQL yourself (steps are in each README) before claiming MySQL experience.
5. **Push each project to its own GitHub repo** with its README. Your resume links to your GitHub.
