import asyncio
import json
import logging
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Any, Dict, Optional

from .config import Config
from .scraper import PoeScraper
from .utils import Logger, ProgressTracker


class PoeScraperGUI(tk.Tk):
    """GUI application for Poe.com scraper"""
    
    def __init__(self, root: tk.Tk):
        super().__init__()
        self.title("Poe.com Scraper")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Initialize components
        self.config = Config()
        self.scraper = None
        self.logger = Logger("GUI")
        self.progress_tracker = None
        self.scraping_task = None
        
        # GUI state
        self.is_scraping = False
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        self.setup_layout()
        self.setup_logging()
        
        logging.basicConfig(level=logging.INFO)
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main title
        self.title_label = ttk.Label(
            self, 
            text="Poe.com Scraper", 
            style='Title.TLabel'
        )
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        
        # Create tabs
        self.create_scraping_tab()
        self.create_config_tab()
        self.create_results_tab()
        self.create_logs_tab()
        
    def create_scraping_tab(self):
        """Create the main scraping tab"""
        self.scraping_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.scraping_frame, text="Scraping")
        
        # Scraping controls frame
        controls_frame = ttk.LabelFrame(self.scraping_frame, text="Controls", padding=10)
        
        # Max conversations setting
        ttk.Label(controls_frame, text="Max Conversations:").grid(row=0, column=0, sticky='w', pady=2)
        self.max_conv_var = tk.StringVar(value="100")
        self.max_conv_entry = ttk.Entry(controls_frame, textvariable=self.max_conv_var, width=10)
        self.max_conv_entry.grid(row=0, column=1, sticky='w', padx=(5, 0), pady=2)
        
        # Export format selection
        ttk.Label(controls_frame, text="Export Format:").grid(row=1, column=0, sticky='w', pady=2)
        self.export_format_var = tk.StringVar(value="json")
        self.export_format_combo = ttk.Combobox(
            controls_frame, 
            textvariable=self.export_format_var,
            values=["json", "csv", "xlsx"],
            state="readonly",
            width=8
        )
        self.export_format_combo.grid(row=1, column=1, sticky='w', padx=(5, 0), pady=2)
        
        # Output directory selection
        ttk.Label(controls_frame, text="Output Directory:").grid(row=2, column=0, sticky='w', pady=2)
        self.output_dir_var = tk.StringVar(value="./output")
        self.output_dir_entry = ttk.Entry(controls_frame, textvariable=self.output_dir_var, width=30)
        self.output_dir_entry.grid(row=2, column=1, sticky='w', padx=(5, 0), pady=2)
        
        self.browse_button = ttk.Button(
            controls_frame, 
            text="Browse", 
            command=self.browse_output_directory
        )
        self.browse_button.grid(row=2, column=2, padx=(5, 0), pady=2)
        
        # Action buttons
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        self.start_button = ttk.Button(
            buttons_frame, 
            text="Start Scraping", 
            command=self.start_scraping,
            style='Accent.TButton'
        )
        self.start_button.pack(side='left', padx=(0, 5))
        
        self.stop_button = ttk.Button(
            buttons_frame, 
            text="Stop", 
            command=self.stop_scraping,
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=5)
        
        self.export_button = ttk.Button(
            buttons_frame, 
            text="Export Results", 
            command=self.export_results,
            state='disabled'
        )
        self.export_button.pack(side='left', padx=5)
        
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(self.scraping_frame, text="Progress", padding=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var, 
            maximum=100,
            length=400
        )
        self.progress_bar.pack(pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="Ready to scrape")
        self.status_label.pack()
        
        progress_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(self.scraping_frame, text="Statistics", padding=10)
        
        self.stats_text = scrolledtext.ScrolledText(
            stats_frame, 
            height=8, 
            width=60,
            state='disabled'
        )
        self.stats_text.pack(fill='both', expand=True)
        
        stats_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
    def create_config_tab(self):
        """Create configuration tab"""
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="Configuration")
        
        # Create scrollable frame
        canvas = tk.Canvas(self.config_frame)
        scrollbar = ttk.Scrollbar(self.config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Rate limiting configuration
        rate_limit_frame = ttk.LabelFrame(scrollable_frame, text="Rate Limiting", padding=10)
        
        ttk.Label(rate_limit_frame, text="Requests per minute:").grid(row=0, column=0, sticky='w', pady=2)
        self.requests_per_min_var = tk.StringVar(value=str(self.config.rate_limit.requests_per_minute))
        ttk.Entry(rate_limit_frame, textvariable=self.requests_per_min_var, width=10).grid(row=0, column=1, sticky='w', padx=(5, 0))
        
        ttk.Label(rate_limit_frame, text="Delay between requests (s):").grid(row=1, column=0, sticky='w', pady=2)
        self.delay_var = tk.StringVar(value=str(self.config.rate_limit.delay_between_requests))
        ttk.Entry(rate_limit_frame, textvariable=self.delay_var, width=10).grid(row=1, column=1, sticky='w', padx=(5, 0))
        
        rate_limit_frame.pack(fill='x', padx=10, pady=5)
        
        # Scraping configuration
        scraping_frame = ttk.LabelFrame(scrollable_frame, text="Scraping Settings", padding=10)
        
        ttk.Label(scraping_frame, text="Max retries:").grid(row=0, column=0, sticky='w', pady=2)
        self.max_retries_var = tk.StringVar(value=str(self.config.scraping.max_retries))
        ttk.Entry(scraping_frame, textvariable=self.max_retries_var, width=10).grid(row=0, column=1, sticky='w', padx=(5, 0))
        
        ttk.Label(scraping_frame, text="Timeout (s):").grid(row=1, column=0, sticky='w', pady=2)
        self.timeout_var = tk.StringVar(value=str(self.config.scraping.timeout_seconds))
        ttk.Entry(scraping_frame, textvariable=self.timeout_var, width=10).grid(row=1, column=1, sticky='w', padx=(5, 0))
        
        self.include_timestamps_var = tk.BooleanVar(value=self.config.scraping.include_timestamps)
        ttk.Checkbutton(
            scraping_frame, 
            text="Include timestamps", 
            variable=self.include_timestamps_var
        ).grid(row=2, column=0, columnspan=2, sticky='w', pady=2)
        
        self.skip_empty_var = tk.BooleanVar(value=self.config.scraping.skip_empty_conversations)
        ttk.Checkbutton(
            scraping_frame, 
            text="Skip empty conversations", 
            variable=self.skip_empty_var
        ).grid(row=3, column=0, columnspan=2, sticky='w', pady=2)
        
        scraping_frame.pack(fill='x', padx=10, pady=5)
        
        # Configuration buttons
        config_buttons_frame = ttk.Frame(scrollable_frame)
        
        ttk.Button(
            config_buttons_frame, 
            text="Load Config", 
            command=self.load_config
        ).pack(side='left', padx=5)
        
        ttk.Button(
            config_buttons_frame, 
            text="Save Config", 
            command=self.save_config
        ).pack(side='left', padx=5)
        
        ttk.Button(
            config_buttons_frame, 
            text="Reset to Defaults", 
            command=self.reset_config
        ).pack(side='left', padx=5)
        
        config_buttons_frame.pack(pady=10)
        
        # Pack scrollable components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_results_tab(self):
        """Create results viewing tab"""
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Results")
        
        # Results display
        self.results_text = scrolledtext.ScrolledText(
            self.results_frame,
            wrap=tk.WORD,
            height=25
        )
        self.results_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def create_logs_tab(self):
        """Create logs viewing tab"""
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="Logs")
        
        # Log controls
        log_controls = ttk.Frame(self.logs_frame)
        
        ttk.Button(
            log_controls, 
            text="Clear Logs", 
            command=self.clear_logs
        ).pack(side='left', padx=5)
        
        ttk.Button(
            log_controls, 
            text="Save Logs", 
            command=self.save_logs
        ).pack(side='left', padx=5)
        
        log_controls.pack(fill='x', padx=10, pady=(10, 5))
        
        # Logs display
        self.logs_text = scrolledtext.ScrolledText(
            self.logs_frame,
            wrap=tk.WORD,
            height=25,
            state='disabled'
        )
        self.logs_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
    def setup_layout(self):
        """Setup the main layout"""
        self.title_label.pack(pady=10)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
    def setup_logging(self):
        """Setup logging to GUI"""
        # Create custom handler for GUI logs
        class GUIHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                
            def emit(self, record):
                try:
                    msg = self.format(record)
                    self.text_widget.config(state='normal')
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.see(tk.END)
                    self.text_widget.config(state='disabled')
                except Exception:
                    pass
                    
        gui_handler = GUIHandler(self.logs_text)
        gui_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        
        self.logger.get_logger().addHandler(gui_handler)
        
    def browse_output_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir_var.get()
        )
        if directory:
            self.output_dir_var.set(directory)
            
    def apply_config_changes(self):
        """Apply configuration changes from GUI"""
        try:
            # Update rate limiting
            self.config.rate_limit.requests_per_minute = int(self.requests_per_min_var.get())
            self.config.rate_limit.delay_between_requests = float(self.delay_var.get())
            
            # Update scraping settings
            self.config.scraping.max_retries = int(self.max_retries_var.get())
            self.config.scraping.timeout_seconds = int(self.timeout_var.get())
            self.config.scraping.include_timestamps = self.include_timestamps_var.get()
            self.config.scraping.skip_empty_conversations = self.skip_empty_var.get()
            
            # Update output settings
            self.config.output.directory = self.output_dir_var.get()
            self.config.output.format = self.export_format_var.get()
            
        except ValueError as e:
            messagebox.showerror("Configuration Error", f"Invalid configuration value: {e}")
            
    def start_scraping(self):
        """Start the scraping process"""
        if self.is_scraping:
            return
            
        try:
            # Apply configuration changes
            self.apply_config_changes()
            
            # Validate max conversations
            max_conversations = int(self.max_conv_var.get())
            if max_conversations <= 0:
                raise ValueError("Max conversations must be positive")
                
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return
            
        # Update UI state
        self.is_scraping = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.export_button.config(state='disabled')
        
        # Clear previous results
        self.stats_text.config(state='normal')
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.config(state='disabled')
        
        # Start scraping in background thread
        self.scraping_task = threading.Thread(
            target=self._run_scraping_async,
            args=(max_conversations,),
            daemon=True
        )
        self.scraping_task.start()
        
    def _run_scraping_async(self, max_conversations: int):
        """Run scraping in async context"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the scraping
            loop.run_until_complete(self._scrape_data(max_conversations))
            
        except Exception as e:
            self.logger.get_logger().error(f"Scraping failed: {e}")
            self.root.after(0, lambda: self._scraping_finished(success=False, error=str(e)))
        finally:
            loop.close()
            
    async def _scrape_data(self, max_conversations: int):
        """Perform the actual scraping"""
        self.logger.get_logger().info("Starting scraping process...")
        
        try:
            # Initialize scraper
            self.scraper = PoeScraper(config_path=None)
            self.scraper.config = self.config
            
            # Setup progress tracking
            self.progress_tracker = ProgressTracker(max_conversations, "Scraping conversations")
            self.progress_tracker.add_callback(self._update_progress)
            
            # Start scraping
            async with self.scraper:
                conversations = await self.scraper.scrape_conversations(max_conversations)
                
            # Update results
            self.root.after(0, lambda: self._display_results(conversations))
            self.root.after(0, lambda: self._scraping_finished(success=True))
            
        except Exception as e:
            self.logger.get_logger().error(f"Scraping error: {e}")
            self.root.after(0, lambda: self._scraping_finished(success=False, error=str(e)))
            
    def _update_progress(self, current: int, total: int, percentage: float):
        """Update progress bar and status"""
        def update_ui():
            self.progress_var.set(percentage)
            self.status_label.config(text=f"Scraped {current}/{total} conversations ({percentage:.1f}%)")
            
        self.root.after(0, update_ui)
        
    def _display_results(self, conversations):
        """Display scraping results"""
        self.results_text.delete(1.0, tk.END)
        
        if not conversations:
            self.results_text.insert(tk.END, "No conversations found.")
            return
            
        # Display summary
        summary = f"Successfully scraped {len(conversations)} conversations:\n\n"
        
        for i, conv in enumerate(conversations[:10]):  # Show first 10
            summary += f"{i+1}. {conv.title} ({conv.bot_name}) - {len(conv.messages)} messages\n"
            
        if len(conversations) > 10:
            summary += f"\n... and {len(conversations) - 10} more conversations\n"
            
        self.results_text.insert(tk.END, summary)
        
        # Display statistics
        if self.scraper:
            stats = self.scraper.get_stats()
            self._display_stats(stats)
            
    def _display_stats(self, stats: Dict[str, Any]):
        """Display statistics in stats text widget"""
        self.stats_text.config(state='normal')
        self.stats_text.delete(1.0, tk.END)
        
        stats_text = "Scraping Statistics:\n\n"
        stats_text += f"Total Conversations: {stats.get('total_conversations', 0)}\n"
        stats_text += f"Total Messages: {stats.get('total_messages', 0)}\n"
        stats_text += f"Average Messages per Conversation: {stats.get('average_messages_per_conversation', 0):.1f}\n\n"
        
        if 'bot_distribution' in stats:
            stats_text += "Bot Distribution:\n"
            for bot_name, count in stats['bot_distribution'].items():
                stats_text += f"  {bot_name}: {count} conversations\n"
                
        self.stats_text.insert(tk.END, stats_text)
        self.stats_text.config(state='disabled')
        
    def _scraping_finished(self, success: bool, error: str = None):
        """Handle scraping completion"""
        self.is_scraping = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        if success:
            self.export_button.config(state='normal')
            self.status_label.config(text="Scraping completed successfully!")
            self.progress_var.set(100)
            messagebox.showinfo("Success", "Scraping completed successfully!")
        else:
            self.status_label.config(text=f"Scraping failed: {error}")
            messagebox.showerror("Error", f"Scraping failed: {error}")
            
    def stop_scraping(self):
        """Stop the scraping process"""
        if self.scraper:
            self.scraper.stop_scraping()
        self.logger.get_logger().info("Scraping stopped by user")
        
    def export_results(self):
        """Export scraped results"""
        if not self.scraper or not self.scraper.conversations:
            messagebox.showwarning("No Data", "No conversations to export")
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                title="Save Export As",
                defaultextension=f".{self.export_format_var.get()}",
                filetypes=[
                    ("JSON files", "*.json"),
                    ("CSV files", "*.csv"),
                    ("Excel files", "*.xlsx"),
                    ("All files", "*.*")
                ]
            )
            
            if filename:
                # Get format from file extension
                export_format = os.path.splitext(filename)[1][1:]  # Remove the dot
                
                filepath = self.scraper.export_data(
                    self.scraper.conversations,
                    format=export_format,
                    filename=os.path.splitext(os.path.basename(filename))[0]
                )
                
                messagebox.showinfo("Export Success", f"Data exported to: {filepath}")
                self.logger.get_logger().info(f"Data exported to: {filepath}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {e}")
            self.logger.get_logger().error(f"Export failed: {e}")
            
    def load_config(self):
        """Load configuration from file"""
        filepath = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                self.config = Config(filepath)
                self._update_config_gui()
                messagebox.showinfo("Success", "Configuration loaded successfully")
                self.logger.get_logger().info(f"Configuration loaded from: {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration: {e}")
                
    def save_config(self):
        """Save current configuration to file"""
        filepath = filedialog.asksaveasfilename(
            title="Save Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                self.apply_config_changes()
                self.config.save_to_file(filepath)
                messagebox.showinfo("Success", "Configuration saved successfully")
                self.logger.get_logger().info(f"Configuration saved to: {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {e}")
                
    def reset_config(self):
        """Reset configuration to defaults"""
        if messagebox.askyesno("Confirm", "Reset all settings to defaults?"):
            self.config = Config()
            self._update_config_gui()
            messagebox.showinfo("Success", "Configuration reset to defaults")
            
    def _update_config_gui(self):
        """Update GUI elements with current configuration"""
        self.requests_per_min_var.set(str(self.config.rate_limit.requests_per_minute))
        self.delay_var.set(str(self.config.rate_limit.delay_between_requests))
        self.max_retries_var.set(str(self.config.scraping.max_retries))
        self.timeout_var.set(str(self.config.scraping.timeout_seconds))
        self.include_timestamps_var.set(self.config.scraping.include_timestamps)
        self.skip_empty_var.set(self.config.scraping.skip_empty_conversations)
        self.output_dir_var.set(self.config.output.directory)
        self.export_format_var.set(self.config.output.format)
        
    def clear_logs(self):
        """Clear the logs display"""
        self.logs_text.config(state='normal')
        self.logs_text.delete(1.0, tk.END)
        self.logs_text.config(state='disabled')
        
    def save_logs(self):
        """Save logs to file"""
        filepath = filedialog.asksaveasfilename(
            title="Save Logs",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    f.write(self.logs_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Logs saved to: {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save logs: {e}")

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = PoeScraperGUI(root)
    
    # Handle window closing
    def on_closing():
        if app.is_scraping:
            if messagebox.askokcancel("Quit", "Scraping is in progress. Do you want to quit?"):
                app.stop_scraping()
                root.destroy()
        else:
            root.destroy()
            
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()