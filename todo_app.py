import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import csv
import os
from datetime import datetime

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Manager")
        self.root.geometry("800x600")
        self.root.configure(bg="#f5f5f5")
        
        # Set app style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("TButton", background="#4CAF50", foreground="black", padding=6, font=('Arial', 10))
        self.style.configure("TLabel", background="#f5f5f5", font=('Arial', 12))
        self.style.configure("Treeview", font=('Arial', 11), rowheight=25)
        self.style.map("Treeview", background=[('selected', '#4CAF50')])
        
        self.tasks = []
        self.csv_file = "tasks.csv"
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="To-Do List Manager", font=('Arial', 18, 'bold')).pack(side=tk.LEFT)
        
        # Create task list frame
        list_frame = ttk.Frame(self.main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for tasks
        self.tree = ttk.Treeview(list_frame, columns=("ID", "Task", "Due Date", "Status"), show="headings")
        self.tree.heading("ID", text="#")
        self.tree.heading("Task", text="Task")
        self.tree.heading("Due Date", text="Due Date")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("ID", width=50)
        self.tree.column("Task", width=400)
        self.tree.column("Due Date", width=150)
        self.tree.column("Status", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create buttons frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Add buttons
        ttk.Button(button_frame, text="Add Task", command=self.add_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit Task", command=self.edit_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Task", command=self.delete_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Mark Complete", command=self.mark_complete).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Mark Incomplete", command=self.mark_incomplete).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(20, 0))
        
        # Load tasks from CSV
        self.load_tasks()
        
        # Bind double-click event to edit task
        self.tree.bind("<Double-1>", lambda event: self.edit_task())
        
    def load_tasks(self):
        """Load tasks from CSV file"""
        if not os.path.exists(self.csv_file):
            # Create file with headers if it doesn't exist
            with open(self.csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["id", "task", "due_date", "status"])
            self.status_var.set(f"Created new tasks file: {self.csv_file}")
            return
            
        try:
            self.tasks = []
            with open(self.csv_file, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.tasks.append(row)
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Add tasks to treeview
            for task in self.tasks:
                self.tree.insert("", tk.END, values=(
                    task["id"], 
                    task["task"], 
                    task["due_date"], 
                    task["status"]
                ))
                
            self.status_var.set(f"Loaded {len(self.tasks)} tasks from {self.csv_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {str(e)}")
            self.status_var.set("Error loading tasks")
    
    def save_tasks(self):
        """Save tasks to CSV file"""
        try:
            with open(self.csv_file, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["id", "task", "due_date", "status"])
                writer.writeheader()
                writer.writerows(self.tasks)
            self.status_var.set(f"Saved {len(self.tasks)} tasks to {self.csv_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save tasks: {str(e)}")
            self.status_var.set("Error saving tasks")
    
    def add_task(self):
        """Add a new task"""
        # Create a dialog for adding a task
        dialog = TaskDialog(self.root, "Add Task")
        if dialog.result:
            task_text, due_date = dialog.result
            
            # Generate a new ID
            new_id = "1"
            if self.tasks:
                # Find the highest ID and increment by 1
                try:
                    highest_id = max(int(task["id"]) for task in self.tasks)
                    new_id = str(highest_id + 1)
                except ValueError:
                    # If there's an issue with IDs, just use the length + 1
                    new_id = str(len(self.tasks) + 1)
            
            # Create new task
            new_task = {
                "id": new_id,
                "task": task_text,
                "due_date": due_date,
                "status": "Pending"
            }
            
            # Add to tasks list
            self.tasks.append(new_task)
            
            # Add to treeview
            self.tree.insert("", tk.END, values=(
                new_task["id"], 
                new_task["task"], 
                new_task["due_date"], 
                new_task["status"]
            ))
            
            # Save tasks
            self.save_tasks()
            self.status_var.set(f"Added task: {task_text}")
    
    def edit_task(self):
        """Edit the selected task"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a task to edit")
            return
            
        # Get the selected task values
        item_values = self.tree.item(selected_item[0], "values")
        task_id = item_values[0]
        
        # Find the task in the list
        task_index = None
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                task_index = i
                break
                
        if task_index is None:
            messagebox.showerror("Error", "Task not found")
            return
            
        # Create a dialog for editing the task
        dialog = TaskDialog(self.root, "Edit Task", 
                           initial_task=self.tasks[task_index]["task"],
                           initial_date=self.tasks[task_index]["due_date"])
        
        if dialog.result:
            task_text, due_date = dialog.result
            
            # Update task
            self.tasks[task_index]["task"] = task_text
            self.tasks[task_index]["due_date"] = due_date
            
            # Update treeview
            self.tree.item(selected_item[0], values=(
                self.tasks[task_index]["id"],
                self.tasks[task_index]["task"],
                self.tasks[task_index]["due_date"],
                self.tasks[task_index]["status"]
            ))
            
            # Save tasks
            self.save_tasks()
            self.status_var.set(f"Updated task: {task_text}")
    
    def delete_task(self):
        """Delete the selected task"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a task to delete")
            return
            
        # Confirm deletion
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this task?"):
            return
            
        # Get the selected task values
        item_values = self.tree.item(selected_item[0], "values")
        task_id = item_values[0]
        
        # Find and remove the task from the list
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                removed_task = self.tasks.pop(i)
                break
        
        # Remove from treeview
        self.tree.delete(selected_item[0])
        
        # Save tasks
        self.save_tasks()
        self.status_var.set(f"Deleted task: {removed_task['task']}")
    
    def mark_complete(self):
        """Mark the selected task as complete"""
        self._change_task_status("Complete")
    
    def mark_incomplete(self):
        """Mark the selected task as pending"""
        self._change_task_status("Pending")
    
    def _change_task_status(self, status):
        """Change the status of the selected task"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", f"Please select a task to mark as {status.lower()}")
            return
            
        # Get the selected task values
        item_values = self.tree.item(selected_item[0], "values")
        task_id = item_values[0]
        
        # Find the task in the list
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = status
                
                # Update treeview
                self.tree.item(selected_item[0], values=(
                    task["id"],
                    task["task"],
                    task["due_date"],
                    task["status"]
                ))
                
                # Save tasks
                self.save_tasks()
                self.status_var.set(f"Marked task as {status.lower()}: {task['task']}")
                break


class TaskDialog:
    """Dialog for adding or editing a task"""
    def __init__(self, parent, title, initial_task="", initial_date=""):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create form
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Task entry
        ttk.Label(frame, text="Task:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.task_entry = ttk.Entry(frame, width=50)
        self.task_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        self.task_entry.insert(0, initial_task)
        
        # Due date entry
        ttk.Label(frame, text="Due Date:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.date_entry = ttk.Entry(frame, width=50)
        self.date_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Set initial date or today's date
        if initial_date:
            self.date_entry.insert(0, initial_date)
        else:
            today = datetime.now().strftime("%Y-%m-%d")
            self.date_entry.insert(0, today)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        
        # Set focus to task entry
        self.task_entry.focus_set()
        
        # Wait for dialog to close
        parent.wait_window(self.dialog)
    
    def save(self):
        """Save the task and close dialog"""
        task = self.task_entry.get().strip()
        due_date = self.date_entry.get().strip()
        
        if not task:
            messagebox.showerror("Error", "Task cannot be empty")
            return
            
        self.result = (task, due_date)
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel and close dialog"""
        self.dialog.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()