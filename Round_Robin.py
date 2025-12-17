#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from statistics import mean
from PIL import Image, ImageTk
import urllib.request
import io
import random

# ---------------------
# Core simulation (unchanged)
# ---------------------
def round_robin(processes, quantum):
    processes = sorted(processes, key=lambda x: x[1])
    n = len(processes)
    remaining = [bt for _, _, bt in processes]
    completion = [0] * n
    first_response = [-1] * n
    time = 0
    queue = []
    visited = [False] * n
    gantt = []

    if processes and processes[0][1] > 0:
        time = processes[0][1]

    for idx in range(n):
        if processes[idx][1] <= time and not visited[idx]:
            queue.append(idx)
            visited[idx] = True

    if not queue:
        for idx in range(n):
            if not visited[idx]:
                time = processes[idx][1]
                queue.append(idx)
                visited[idx] = True
                break

    while queue:
        i = queue.pop(0)
        if first_response[i] == -1:
            first_response[i] = time - processes[i][1]

        run_time = min(remaining[i], quantum)
        start = time
        end = time + run_time
        gantt.append((processes[i][0], start, end))

        time = end
        remaining[i] -= run_time

        for j in range(n):
            if processes[j][1] <= time and not visited[j] and remaining[j] > 0:
                queue.append(j)
                visited[j] = True

        if remaining[i] > 0:
            queue.append(i)
        else:
            completion[i] = time

        if not queue:
            for k in range(n):
                if remaining[k] > 0 and not visited[k]:
                    time = processes[k][1]
                    queue.append(k)
                    visited[k] = True
                    break

    tat = [completion[i] - processes[i][1] for i in range(n)]
    wt = [tat[i] - processes[i][2] for i in range(n)]
    rt = [first_response[i] for i in range(n)]

    cs = 0
    for idx in range(1, len(gantt)):
        if gantt[idx][0] != gantt[idx - 1][0]:
            cs += 1

    return processes, completion, tat, wt, rt, gantt, cs

def compute_extra_metrics(processes, completion, tat, wt, rt, gantt):
    n = len(processes)
    total_burst = sum(p[2] for p in processes)
    total_time = gantt[-1][2] if gantt else 0
    cpu_util = (total_burst / total_time * 100) if total_time > 0 else 0
    throughput = (n / total_time) if total_time > 0 else 0
    response_ratios = [(tat[i] / processes[i][2]) if processes[i][2] > 0 else float('inf') for i in range(n)]
    avg_rr = mean(response_ratios) if response_ratios else 0
    return {
        "total_time": total_time,
        "total_burst": total_burst,
        "cpu_util": cpu_util,
        "throughput": throughput,
        "response_ratios": response_ratios,
        "avg_response_ratio": avg_rr
    }

# ---------------------
# GUI actions
# ---------------------
def display_results_in_tree(procs, comp, tat, wt, rt):
    # Clear old rows
    for row in tree.get_children():
        tree.delete(row)

    # Insert rows with formatting
    for i in range(len(procs)):
        proc_id = procs[i][0]
        at = procs[i][1]
        bt = procs[i][2]
        ct = comp[i]
        tat_i = tat[i]
        wt_i = wt[i]
        rt_i = rt[i] if rt[i] >= 0 else 0  # display 0 instead of -1

        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        # Format everything as strings so columns align nicely
        tree.insert("", "end", values=(
            str(proc_id),
            str(at),
            str(bt),
            str(ct),
            str(tat_i),
            str(wt_i),
            str(rt_i)
        ), tags=(tag,))

def run_scheduler():
    try:
        # verify inputs and existence of process entries
        try:
            n = int(entry_n.get())
            if n <= 0:
                raise ValueError
        except:
            raise ValueError("Enter a valid positive integer for 'Number of Processes' and click 'Create Table Inputs'.")

        # if entries not created, create them automatically
        if len(entries_at) < n or len(entries_bt) < n:
            create_process_inputs()

        q = int(entry_quantum.get())
        if q <= 0:
            raise ValueError("Time quantum must be a positive integer.")

        processes = []
        for i in range(n):
            at_raw = entries_at[i].get().strip()
            bt_raw = entries_bt[i].get().strip()
            if at_raw == "" or bt_raw == "":
                raise ValueError(f"Arrival/Burst time missing for process P{i+1}.")
            at = int(at_raw)
            bt = int(bt_raw)
            if at < 0 or bt <= 0:
                raise ValueError(f"Invalid values for P{i+1}: AT must be >=0 and BT must be >0.")
            processes.append(("P" + str(i + 1), at, bt))

        procs, comp, tat, wt, rt, gantt, cs = round_robin(processes, q)
        extras = compute_extra_metrics(procs, comp, tat, wt, rt, gantt)

        display_results_in_tree(procs, comp, tat, wt, rt)

        avg_wt = mean(wt) if wt else 0
        avg_tat = mean(tat) if tat else 0

        lbl_avg.config(text=f"ATAT: {avg_tat:.2f}   |   AWT: {avg_wt:.2f}   |   CS: {cs}")
        lbl_extras.config(text=f"Total Time: {extras['total_time']}   CPU Util: {extras['cpu_util']:.2f}%   "
                               f"Throughput: {extras['throughput']:.3f}/unit   Avg RespRatio: {extras['avg_response_ratio']:.2f}")

        # Build RR text with one proc per line (wrap via label width)
        rr_lines = []
        for i in range(len(procs)):
            rr_val = extras['response_ratios'][i]
            rr_lines.append(f"{procs[i][0]}: {rr_val:.2f}")
        rr_text = "   |   ".join(rr_lines)
        lbl_rr.config(text=f"Response Ratios (per proc): {rr_text}")

        show_gantt(gantt, title=f"Gantt (Quantum={q})", show_cs_lines=True)

    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_gantt(gantt, title="Gantt Chart", show_cs_lines=True):
    if not gantt:
        messagebox.showinfo("Info", "No Gantt data to plot.")
        return
    plt.figure(figsize=(10, 2.8))
    colors = ["#FF6F61", "#6B5B95", "#88B04B", "#F7CAC9", "#92A8D1", "#955251", "#F4A460"]
    for idx, (pid, s, e) in enumerate(gantt):
        plt.barh(y=0, width=e - s, left=s, color=colors[idx % len(colors)], edgecolor="black")
        plt.text((s + e) / 2, 0, pid, ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        if show_cs_lines and idx > 0:
            plt.axvline(x=s, color="red", linestyle="--", linewidth=1)
    start_time = gantt[0][1]
    end_time = gantt[-1][2]
    plt.title(title, fontsize=12, fontweight="bold")
    plt.xlabel("Time")
    plt.yticks([])
    plt.xlim(left=max(0, start_time - 1), right=end_time + 1)
    plt.grid(axis="x", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.show()

def analyze_quantum():
    try:
        n = int(entry_n.get())
        processes = []
        for i in range(n):
            at = int(entries_at[i].get())
            bt = int(entries_bt[i].get())
            processes.append(("P" + str(i + 1), at, bt))

        max_q = max((p[2] for p in processes), default=1) + 3
        q_values = list(range(1, max_q))
        avg_wt_list, avg_tat_list, cs_list = [], [], []

        for q in q_values:
            _, _, tat, wt, _, _, cs = round_robin(processes, q)
            avg_wt_list.append(mean(wt) if wt else 0)
            avg_tat_list.append(mean(tat) if tat else 0)
            cs_list.append(cs)

        plt.figure(figsize=(10, 5))
        plt.plot(q_values, avg_wt_list, marker="o", label="Avg Waiting Time")
        plt.plot(q_values, avg_tat_list, marker="s", label="Avg Turnaround Time")
        plt.plot(q_values, cs_list, marker="^", label="Context Switches")
        plt.title("Effect of Time Quantum on Performance", fontsize=13, fontweight="bold")
        plt.xlabel("Time Quantum")
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", str(e))

def compare_quanta():
    try:
        n = int(entry_n.get())
        q1 = int(entry_q1.get())
        q2 = int(entry_q2.get())
        if q1 <= 0 or q2 <= 0:
            raise ValueError("Quantum values must be positive integers")
        processes = []
        for i in range(n):
            at = int(entries_at[i].get())
            bt = int(entries_bt[i].get())
            processes.append(("P" + str(i + 1), at, bt))

        p1, comp1, tat1, wt1, rt1, gantt1, cs1 = round_robin(processes, q1)
        p2, comp2, tat2, wt2, rt2, gantt2, cs2 = round_robin(processes, q2)

        extras1 = compute_extra_metrics(p1, comp1, tat1, wt1, rt1, gantt1)
        extras2 = compute_extra_metrics(p2, comp2, tat2, wt2, rt2, gantt2)

        fig, axes = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
        colors = ["#FF6F61", "#6B5B95", "#88B04B", "#F7CAC9", "#92A8D1", "#955251"]
        ax = axes[0]
        for idx, (pid, s, e) in enumerate(gantt1):
            ax.barh(y=0, width=e - s, left=s, color=colors[idx % len(colors)], edgecolor="black")
            ax.text((s + e) / 2, 0, pid, ha="center", va="center", color="white", fontsize=8, fontweight="bold")
            if idx > 0 and gantt1[idx][0] != gantt1[idx - 1][0]:
                ax.axvline(x=s, color="red", linestyle="--", linewidth=1)
        ax.set_title(f"Gantt (Q={q1}) -- CS:{cs1}  ATAT:{mean(tat1):.2f}  AWT:{mean(wt1):.2f}", fontsize=10)

        ax = axes[1]
        for idx, (pid, s, e) in enumerate(gantt2):
            ax.barh(y=0, width=e - s, left=s, color=colors[idx % len(colors)], edgecolor="black")
            ax.text((s + e) / 2, 0, pid, ha="center", va="center", color="white", fontsize=8, fontweight="bold")
            if idx > 0 and gantt2[idx][0] != gantt2[idx - 1][0]:
                ax.axvline(x=s, color="red", linestyle="--", linewidth=1)
        ax.set_title(f"Gantt (Q={q2}) -- CS:{cs2}  ATAT:{mean(tat2):.2f}  AWT:{mean(wt2):.2f}", fontsize=10)

        for ax in axes:
            ax.set_yticks([])
            ax.grid(axis="x", linestyle="--", alpha=0.4)

        plt.tight_layout()
        plt.show()

        comp_msg = (
            f"Quantum {q1} -> ATAT: {mean(tat1):.2f}, AWT: {mean(wt1):.2f}, CS: {cs1}, CPU Util: {extras1['cpu_util']:.2f}%\n"
            f"Quantum {q2} -> ATAT: {mean(tat2):.2f}, AWT: {mean(wt2):.2f}, CS: {cs2}, CPU Util: {extras2['cpu_util']:.2f}%\n"
        )
        messagebox.showinfo("Comparison Results", comp_msg)

    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_info():
    info_win = tk.Toplevel(root)
    info_win.title("About Round Robin - Info Panel")
    info_win.geometry("650x450")
    info_win.configure(bg="#F7FBFF")

    txt = tk.Text(info_win, wrap="word", padx=12, pady=12, bg="#F7FBFF")
    
    # Define fonts
    heading_font = ("Helvetica", 14, "bold")
    subheading_font = ("Helvetica", 12, "bold", "italic")
    normal_font = ("Helvetica", 11)
    
    # Insert content with tags
    txt.insert("1.0", "Round Robin (RR) Scheduling - Educational Info\n\n", "heading")
    txt.insert("end", "1) What is Round Robin?\n", "subheading")
    txt.insert("end", "   - RR is a CPU scheduling algorithm that assigns each process a fixed time slice (quantum).\n"
                      "   - Processes are placed in a ready queue and given CPU for 'quantum' time in FIFO order.\n\n", "normal")
    txt.insert("end", "2) How quantum affects performance:\n", "subheading")
    txt.insert("end", "   - Small quantum -> improved responsiveness (lower response time) but MORE context switches (higher overhead).\n"
                      "   - Large quantum -> fewer context switches but can increase waiting/turnaround time (worse responsiveness).\n\n", "normal")
    txt.insert("end", "3) Real-life examples:\n", "subheading")
    txt.insert("end", "   - Time-sharing systems and interactive OS schedulers use RR-like strategies to ensure fairness.\n\n", "normal")
    txt.insert("end", "4) Use the 'Analyze Quantum Effect' button to plot Avg Waiting Time, Avg Turnaround Time, and Context Switches\n", "subheading")
    txt.insert("end", "   across a range of quantum values. Use 'Compare Quanta' to view two quanta side-by-side.\n\n", "normal")
    txt.insert("end", "5) Metrics explained:\n", "subheading")
    txt.insert("end", "   - ATAT: Average Turnaround Time = avg of (CT - AT)\n"
                      "   - AWT: Average Waiting Time = avg of (TAT - BT)\n"
                      "   - Context Switches: number of times CPU switches from one process to another (visualized as red dashed lines)\n", "normal")

    # Configure tags
    txt.tag_configure("heading", font=heading_font, foreground="#2E8BFF")
    txt.tag_configure("subheading", font=subheading_font, foreground="#FF4500")
    txt.tag_configure("normal", font=normal_font, foreground="#000000")
    
    txt.config(state="disabled")
    txt.pack(fill="both", expand=True)


# ---------------------
# Build GUI
# ---------------------
root = tk.Tk()
root.title("Round Robin Scheduling Visualizer (Educational)")
root.geometry("1050x800")
root.configure(bg="#F7FBFF")

# ---------------------
# Logo + Title
# ---------------------
url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcST0id_eprqxCoi1b9Eh6HQDuITVzdcBmyqMA&s"
with urllib.request.urlopen(url) as u:
    raw_data = u.read()
img = Image.open(io.BytesIO(raw_data))
img = img.resize((60, 60))
logo_img = ImageTk.PhotoImage(img)

frame_title = tk.Frame(root, bg="#F7FBFF")
frame_title.pack(fill="x", pady=(8, 0))

lbl_logo = tk.Label(frame_title, image=logo_img, bg="#F7FBFF")
lbl_logo.pack(side="left", padx=10)
lbl_title = tk.Label(frame_title, text="Round Robin Scheduling Visualizer (Educational)",
                     font=("Arial", 18, "bold"), bg="#F7FBFF", fg="#2E8BFF")
lbl_title.pack(side="left")

# ---------------------
# Styles
# ---------------------
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", font=("Arial", 11, "bold"),
                foreground="white", background="#2E8BFF")
style.map("Treeview.Heading",
          background=[('active', '#1E90FF')])  # slight active color change
style.configure("Treeview", font=("Arial", 10), rowheight=26)

# Top frame for scheduler settings
frame_top = tk.LabelFrame(root, text="Scheduler Settings", bg="#EAF6FF", font=("Arial", 12, "bold"), padx=8, pady=8)
frame_top.pack(fill="x", padx=14, pady=10)

tk.Label(frame_top, text="Number of Processes:", bg="#EAF6FF", font=("Arial", 11)).grid(row=0, column=0, sticky="w", padx=6, pady=6)
entry_n = tk.Entry(frame_top, width=6, font=("Arial", 11))
entry_n.grid(row=0, column=1, padx=6)
tk.Label(frame_top, text="Time Quantum:", bg="#EAF6FF", font=("Arial", 11)).grid(row=0, column=2, sticky="w", padx=6, pady=6)
entry_quantum = tk.Entry(frame_top, width=6, font=("Arial", 11))
entry_quantum.grid(row=0, column=3, padx=6)

btn_info = tk.Button(frame_top, text="Info Panel", command=show_info, bg="#256B9A", fg="white", font=("Arial", 10, "bold"))
btn_info.grid(row=0, column=4, padx=8)
btn_run_main = tk.Button(frame_top, text="Run Scheduler", command=run_scheduler, bg="#256B9A", fg="white", font=("Arial", 10, "bold"))
btn_run_main.grid(row=0, column=5, padx=8)
btn_analyze = tk.Button(frame_top, text="Analyze Quantum Effect", command=analyze_quantum, bg="#256B9A", fg="white", font=("Arial", 10, "bold"))
btn_analyze.grid(row=0, column=6, padx=8)

# ---------------------
# Middle: process table
# ---------------------
frame_mid = tk.LabelFrame(root, text="Process Table (Arrival Time, Burst Time)", bg="#BDCDDE", font=("Arial", 12, "bold"), padx=8, pady=8)
frame_mid.pack(fill="x", padx=14)

entries_at = []
entries_bt = []

def create_process_inputs():
    for widget in frame_mid.winfo_children():
        widget.destroy()
    try:
        n = int(entry_n.get())
        if n <= 0:
            raise ValueError
    except:
        messagebox.showerror("Error", "Enter a valid positive integer for number of processes.")
        return
        raise

    header = tk.Frame(frame_mid, bg="#F7FBFF")
    header.pack(fill="x")
    tk.Label(header, text="Process", width=12, bg="#2E8BFF", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=4, pady=4)
    tk.Label(header, text="Arrival Time", width=16, bg="#4682B4", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=4, pady=4)
    tk.Label(header, text="Burst Time", width=16, bg="#4169E1", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=4, pady=4)

    entries_at.clear()
    entries_bt.clear()
    for i in range(n):
        row = tk.Frame(frame_mid, bg="#F7FBFF")
        row.pack(fill="x", pady=2)
        tk.Label(row, text=f"P{i+1}", width=12, font=("Arial", 10)).grid(row=0, column=0, padx=4)
        at = tk.Entry(row, width=18, font=("Arial", 10))
        bt = tk.Entry(row, width=18, font=("Arial", 10))
        at.grid(row=0, column=1, padx=4)
        bt.grid(row=0, column=2, padx=4)
        entries_at.append(at)
        entries_bt.append(bt)

    # comparison inputs
    comp_frame = tk.Frame(frame_mid, bg="#F7FBFF")
    comp_frame.pack(fill="x", pady=6)
    tk.Label(comp_frame, text="Compare Quantum Q1:", bg="#F7FBFF").grid(row=0, column=0, padx=6)
    global entry_q1, entry_q2
    entry_q1 = tk.Entry(comp_frame, width=6)
    entry_q1.grid(row=0, column=1, padx=6)
    tk.Label(comp_frame, text="with Q2:", bg="#F7FBFF").grid(row=0, column=2, padx=6)
    entry_q2 = tk.Entry(comp_frame, width=6)
    entry_q2.grid(row=0, column=3, padx=6)
    btn_compare = tk.Button(comp_frame, text="Compare Quanta", command=compare_quanta,
                        bg="#9DB84B", fg="white", font=("Arial", 10, "bold"), activebackground="#9DB84B")
    btn_compare.grid(row=0, column=4, padx=8)

    # random-fill button
    sample_btn = tk.Button(frame_mid, text="Fill Random Data", command=fill_random_example,
                       bg="#32CD32", fg="white", font=("Arial", 10, "bold"), activebackground="#228B22")
    sample_btn.pack(pady=6)

def fill_random_example():
    try:
        n = int(entry_n.get())
        if n < 1:
            return
        for i in range(n):
            if i < len(entries_at):
                entries_at[i].delete(0, tk.END)
                entries_bt[i].delete(0, tk.END)
                entries_at[i].insert(0, str(random.randint(0, 5)))
                entries_bt[i].insert(0, str(random.randint(1, 10)))
    except:
        pass

btn_create = tk.Button(frame_top, text="Create Table Inputs", command=create_process_inputs, bg="#256B9A", fg="white", font=("Arial", 10, "bold"))
btn_create.grid(row=0, column=7, padx=8)

# ---------------------
# Bottom: results
# ---------------------
frame_bottom = tk.LabelFrame(root, text="Results", bg="#EAF6FF", font=("Arial", 12, "bold"), padx=8, pady=8)
frame_bottom.pack(fill="both", expand=True, padx=12, pady=10)

# Treeview setup
cols = ("Process", "AT", "BT", "CT", "TAT", "WT", "RT")
tree = ttk.Treeview(frame_bottom, columns=cols, show="headings", height=8)

for c in cols:
    tree.heading(c, text=c)
# column widths and anchor: Process left, others center
tree.column("Process", width=120, anchor="w")
tree.column("AT", width=90, anchor="center")
tree.column("BT", width=90, anchor="center")
tree.column("CT", width=100, anchor="center")
tree.column("TAT", width=100, anchor="center")
tree.column("WT", width=100, anchor="center")
tree.column("RT", width=90, anchor="center")

# add a vertical scrollbar for the tree
vsb = ttk.Scrollbar(frame_bottom, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=vsb.set)
vsb.pack(side="right", fill="y")
tree.pack(fill="both", expand=True, padx=6, pady=6)

# Style (already configured above)
style.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF", foreground="black")
style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

# Alternate row colors
tree.tag_configure('oddrow', background="#EAF6FF")
tree.tag_configure('evenrow', background="#FFFFFF")

# Labels
lbl_avg = tk.Label(frame_bottom, text="ATAT: -   |   AWT: -   |   CS: -",
                   font=("Arial", 10, "bold"), bg="#EAF6FF", fg="darkred")
lbl_avg.pack(pady=4)

lbl_extras = tk.Label(frame_bottom, text="Total Time: -   CPU Util: -   Throughput: -   Avg RespRatio: -",
                      font=("Arial", 9), bg="#EAF6FF")
lbl_extras.pack(pady=2)

lbl_rr = tk.Label(frame_bottom, text="Response Ratios (per proc): -",
                  font=("Arial", 9), bg="#EAF6FF", wraplength=920, justify="left")
lbl_rr.pack(fill="x", pady=2, padx=4)

# start GUI

root.mainloop()
