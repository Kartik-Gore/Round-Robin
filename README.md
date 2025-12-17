****🌀 Round Robin(python)****
An interactive Python-based GUI application to simulate and visualize the Round Robin CPU Scheduling Algorithm.
This project is designed for educational purposes, helping students understand how time quantum affects scheduling performance using tables, graphs, and Gantt charts.

**📌 Features**
  ✅ Round Robin Scheduling Simulation
  ✅ Tkinter-based GUI (User-friendly & interactive)
  ✅ Gantt Chart Visualization (with context switches)
  ✅ Performance Metrics Calculation

    Average Waiting Time (AWT)
    Average Turnaround Time (ATAT)
    Response Time
    CPU Utilization
    Throughput
    Context Switch Count

  ✅ Quantum Analysis
    Effect of different time quanta on performance
  ✅ Compare Two Time Quanta Side-by-Side
  ✅ Random Process Data Generator
  ✅ Informative Panel explaining Round Robin concepts

**🛠️ Technologies Used**
  Python 3
  Tkinter – GUI
  Matplotlib – Graphs & Gantt charts
  PIL (Pillow) – Image handling
  Statistics module – Average calculations


**📦 Requirements**
Make sure Python 3 is installed.
Install required libraries using:

pip install matplotlib pillow

**▶️ How to Run**
Clone the repository:
git clone https://github.com/Kartik-Gore/Round-Robin.git
Navigate to the project folder:
cd round-robin-scheduling
Run the application:
python round_robin_gui.py

**🧠 How It Works**
Enter the number of processes
Enter arrival time and burst time for each process
Set the time quantum
Click Run Scheduler
View:
Process table
Gantt chart
Performance metrics
Use:
Analyze Quantum Effect → performance vs quantum graph
Compare Quanta → side-by-side scheduling comparison

**📊 Metrics Explained**
Turnaround Time (TAT) = Completion Time − Arrival Time
Waiting Time (WT) = Turnaround Time − Burst Time
Response Time (RT) = First CPU allocation − Arrival Time
CPU Utilization = (Total Burst Time / Total Time) × 100
Throughput = Number of processes / Total Time
Context Switches = Number of CPU switches between processes

**🎯 Educational Use Case**
Operating Systems Lab
CPU Scheduling Visualization
Understanding Time Quantum Trade-offs
Exam & Viva Preparation

**📸 Screenshots**

<img width="1920" height="1080" alt="Screenshot (313)" src="https://github.com/user-attachments/assets/7480bcbb-247f-4b4d-b3a6-7096b2df08c7" />
<img width="1920" height="1080" alt="Screenshot (315)" src="https://github.com/user-attachments/assets/e41150f6-5efa-4e56-9926-796d93bbdc2e" />
<img width="1920" height="1080" alt="Screenshot (316)" src="https://github.com/user-attachments/assets/475d55c6-0ce6-4d66-990c-62ab84d36403" />
<img width="1920" height="1080" alt="Screenshot (314)" src="https://github.com/user-attachments/assets/5139df89-06b9-4c5d-884e-6a4e4f348231" />

**🚀 Future Enhancements**
Add other scheduling algorithms (FCFS, SJF, Priority)
Export results as CSV or PDF
Dark mode UI
Web-based version

**👨‍🎓 Author**
Kartik Gore
Student 
📚 Operating Systems Project

📄 License
This project is open-source and available for educational use.
