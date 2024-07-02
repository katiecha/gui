import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import statistics

def load_csv():
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filepath:
        csv_path_entry.delete(0, tk.END)
        csv_path_entry.insert(0, filepath)

def calc_period_full_and_spec(df):
    rising_edges = df[df['Channel 0'].diff() == 1]['Time [s]']
    full_func_periods = [rising_edges.iloc[i+3] - rising_edges.iloc[i] for i in range(0, len(rising_edges) - 3, 4)]
    full_func_periods = [item * 1000000 for item in full_func_periods]
    specific_part_periods = rising_edges.diff(periods=1).iloc[2::4] * 1000000
    return full_func_periods, specific_part_periods.dropna().values

def calc_stats(data, requested_stats):
    results = {}
    if 'mean' in requested_stats:
        results['mean'] = statistics.mean(data)
    if 'stdev' in requested_stats:
        results['stdev'] = statistics.stdev(data)
    if 'min' in requested_stats:
        results['min'] = min(data)
    if 'max' in requested_stats:
        results['max'] = max(data)
    if 'median' in requested_stats:
        results['median'] = statistics.median(data)
    if 'mode' in requested_stats:
        try:
            results['mode'] = statistics.mode(data)
        except statistics.StatisticsError:
            results['mode'] = 'No unique mode'
    return results

def filter_data_above_threshold(full_func_periods, specific_part_periods, min_threshold):
    filtered_full = []
    filtered_specific = []
    counter = 0
    irr_counter = 0

    for index, full_length in enumerate(full_func_periods):
        counter += 1
        if full_length >= min_threshold:
            filtered_full.append(full_length)
            filtered_specific.append(specific_part_periods[index])
            irr_counter += 1

    return filtered_full, filtered_specific, counter, irr_counter

def get_threshold_stats_text(full_func_periods, specific_part_periods, requested_stats, min_threshold):
    filtered_full, filtered_specific, counter, irr_counter = filter_data_above_threshold(full_func_periods, specific_part_periods, min_threshold)
    
    result_text = f'Number of irregular function iterations: {irr_counter}/{counter}\n'
    if filtered_full:
        full_stats = calc_stats(filtered_full, requested_stats)
        specific_stats = calc_stats(filtered_specific, requested_stats)
        
        full_stats_text = "\n".join([f"{key.title()}: {value}" for key, value in full_stats.items()])
        specific_stats_text = "\n".join([f"{key.title()}: {value}" for key, value in specific_stats.items()])
        
        result_text += f"\nStatistics for full functions with lengths above {min_threshold} microseconds:\n{full_stats_text}"
        result_text += f"\n\nStatistics for specific parts of the function:\n{specific_stats_text}"
    else:
        result_text += f"No function lengths are above the specified threshold of {min_threshold} microseconds."
    
    return result_text

def start_analysis():
    filepath = csv_path_entry.get()
    if not filepath:
        messagebox.showerror("Error", "Please select a CSV file.")
        return
    
    try:
        min_threshold = float(threshold_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number for the threshold.")
        return
    
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load CSV file: {e}")
        return

    requested_stats = ['mean', 'stdev', 'min', 'max', 'median', 'mode']
    
    full_func_periods, specific_part_periods = calc_period_full_and_spec(df)
    
    full_stats = calc_stats(full_func_periods, requested_stats)
    specific_stats = calc_stats(specific_part_periods, requested_stats)
    
    full_stats_text = "\n".join([f"{key.title()}: {value}" for key, value in full_stats.items()])
    specific_stats_text = "\n".join([f"{key.title()}: {value}" for key, value in specific_stats.items()])
    
    threshold_stats_text = get_threshold_stats_text(full_func_periods, specific_part_periods, requested_stats, min_threshold)
    
    regular_stats_text = f"Full Function Statistics:\n{full_stats_text}\n\nSpecific Part Statistics:\n{specific_stats_text}"
    
    regular_stats_label.config(text=regular_stats_text)
    threshold_stats_label.config(text=threshold_stats_text)

    if not regular_stats_frame.winfo_ismapped():
        regular_stats_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        threshold_stats_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

def collect_data():
    # Placeholder for your Saleae capture code
    messagebox.showinfo("Info", "Collect Data functionality to be implemented.")

# GUI code below!
app = tk.Tk()
app.title("CSV Analysis GUI")

notebook = ttk.Notebook(app)

# Create the Collect Data tab
collect_data_frame = ttk.Frame(notebook, padding=10)
notebook.add(collect_data_frame, text='Collect Data')

tk.Button(collect_data_frame, text="Collect Data", command=collect_data).grid(row=0, column=0, padx=10, pady=10)

# Create the Analyze Data tab
analyze_data_frame = ttk.Frame(notebook, padding=10)
notebook.add(analyze_data_frame, text='Analyze Data')

tk.Label(analyze_data_frame, text="CSV File:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
csv_path_entry = tk.Entry(analyze_data_frame, width=50)
csv_path_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
browse_button = tk.Button(analyze_data_frame, text="Browse", command=load_csv)
browse_button.grid(row=0, column=2, padx=10, pady=5, sticky="w")

tk.Label(analyze_data_frame, text="Threshold (microseconds):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
threshold_entry = tk.Entry(analyze_data_frame)
threshold_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

start_button = tk.Button(analyze_data_frame, text="Start Analysis", command=start_analysis)
start_button.grid(row=2, column=0, columnspan=3, pady=10)

# Create a scrollable frame for statistics
stats_canvas = tk.Canvas(analyze_data_frame)
stats_scrollbar = ttk.Scrollbar(analyze_data_frame, orient="vertical", command=stats_canvas.yview)
scrollable_stats_frame = ttk.Frame(stats_canvas)

scrollable_stats_frame.bind(
    "<Configure>",
    lambda e: stats_canvas.configure(
        scrollregion=stats_canvas.bbox("all")
    )
)

stats_canvas.create_window((0, 0), window=scrollable_stats_frame, anchor="nw")
stats_canvas.configure(yscrollcommand=stats_scrollbar.set)

stats_canvas.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
stats_scrollbar.grid(row=3, column=3, sticky="ns")

# Use LabelFrame to group stats but initially hide them
regular_stats_frame = ttk.LabelFrame(scrollable_stats_frame, text="Regular Statistics", padding=10)
regular_stats_label = tk.Label(regular_stats_frame, text="", justify="left", anchor="w", wraplength=800)
regular_stats_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

threshold_stats_frame = ttk.LabelFrame(scrollable_stats_frame, text="Threshold Statistics", padding=10)
threshold_stats_label = tk.Label(threshold_stats_frame, text="", justify="left", anchor="w", wraplength=800)
threshold_stats_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Initially hide the stats frames
regular_stats_frame.grid_remove()
threshold_stats_frame.grid_remove()

# Configure grid weights
analyze_data_frame.columnconfigure(0, weight=1)
analyze_data_frame.columnconfigure(1, weight=1)
analyze_data_frame.columnconfigure(2, weight=1)
analyze_data_frame.rowconfigure(3, weight=1)

scrollable_stats_frame.columnconfigure(0, weight=1)
regular_stats_frame.columnconfigure(0, weight=1)
threshold_stats_frame.columnconfigure(0, weight=1)

notebook.pack(expand=1, fill="both", padx=10, pady=10)

app.mainloop()
