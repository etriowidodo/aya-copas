import logging
import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ------------------------------
# Constants and Configuration
# ------------------------------
SMALL_FILE_MAX = 100 * 1024 * 1024  # < 100MB
MEDIUM_FILE_MAX = 800 * 1024 * 1024  # 100-800MB
LARGE_FILE_MIN = MEDIUM_FILE_MAX  # > 800MB


class HybridCopyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AYA COPAS")
        self.root.geometry("760x520")
        import ctypes
        myappid = 'artainovasipersada.ayarapihinfolder.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        os.environ['PYTHONWINDOWICON'] = os.path.abspath('AYA.ico')
        self._set_app_icon(root)
        # GUI state
        self.source_type = tk.StringVar(value="Folder")  # "File" or "Folder"
        self.source_path = tk.StringVar()
        self.dest_path = tk.StringVar()
        self.progress = tk.DoubleVar(value=0.0)
        self.status = tk.StringVar(value="Ready")
        self.speed = tk.StringVar(value="0 MB/s")
        self.file_count = tk.IntVar(value=0)
        self.files_total = tk.IntVar(value=0)
        self.eta = tk.StringVar(value="-")
        self.current_file = tk.StringVar(value="")

        # Runtime state
        self.cancel_flag = threading.Event()
        self.executor = None
        self.cpu_count = os.cpu_count() or 4
        self.total_bytes = 0
        self.copied_bytes = 0
        self._bytes_lock = threading.Lock()
        self._start_time = None

        self.create_widgets()

    def _get_resource_path(self, filename):
        base_path = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(base_path, filename),
            os.path.join(getattr(sys, '_MEIPASS', ''), filename),
            filename
        ]
        for path in possible_paths:
            if path and os.path.exists(path):
                return path
        return None
    def _set_app_icon(self, window=None):
        target = window or self
        try:
            target.iconbitmap(self._get_resource_path('AYA.ico'))
        except Exception as e:
            logging.warning(f"Failed to set icon: {e}")

    def create_widgets(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        # Source Type Selection
        type_frame = ttk.Frame(main)
        type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(type_frame, text="Source Type:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Combobox(
            type_frame,
            textvariable=self.source_type,
            values=["File", "Folder"],
            state="readonly",
            width=8
        ).pack(side=tk.LEFT)

        # Paths
        path_frame = ttk.LabelFrame(main, text="File Operations", padding=10)
        path_frame.pack(fill=tk.X, pady=6)

        ttk.Label(path_frame, text="Source:").grid(row=0, column=0, sticky="w")
        src_entry = ttk.Entry(path_frame, textvariable=self.source_path)
        src_entry.grid(row=0, column=1, padx=6, sticky="we")
        ttk.Button(path_frame, text="Browse", command=self.browse_source).grid(row=0, column=2)

        ttk.Label(path_frame, text="Destination:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        dst_entry = ttk.Entry(path_frame, textvariable=self.dest_path)
        dst_entry.grid(row=1, column=1, padx=6, sticky="we", pady=(8, 0))
        ttk.Button(path_frame, text="Browse", command=self.browse_dest).grid(row=1, column=2, pady=(8, 0))

        path_frame.columnconfigure(1, weight=1)

        # Progress
        prog = ttk.LabelFrame(main, text="Progress", padding=10)
        prog.pack(fill=tk.X, pady=6)

        ttk.Label(prog, textvariable=self.status).pack(anchor="w")
        ttk.Label(prog, textvariable=self.current_file, foreground="gray").pack(anchor="w")
        ttk.Progressbar(prog, variable=self.progress, maximum=100).pack(fill=tk.X, pady=8)

        stats = ttk.Frame(prog)
        stats.pack(fill=tk.X)
        ttk.Label(stats, text="Speed:").pack(side=tk.LEFT)
        ttk.Label(stats, textvariable=self.speed).pack(side=tk.LEFT, padx=(4, 16))
        ttk.Label(stats, text="ETA:").pack(side=tk.LEFT)
        ttk.Label(stats, textvariable=self.eta).pack(side=tk.LEFT, padx=(4, 16))
        ttk.Label(stats, text="Files:").pack(side=tk.LEFT)
        ttk.Label(stats, textvariable=self.file_count).pack(side=tk.LEFT, padx=(4, 2))
        ttk.Label(stats, text="/").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Label(stats, textvariable=self.files_total).pack(side=tk.LEFT)

        # Buttons
        btns = ttk.Frame(main)
        btns.pack(fill=tk.X, pady=10)
        ttk.Button(btns, text="Start Copy", command=self.start_copy).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btns, text="Cancel", command=self.cancel_copy).pack(side=tk.LEFT)

        # Tips
        tips = ttk.LabelFrame(main, text="Tips", padding=10)
        tips.pack(fill=tk.X, pady=6)
        ttk.Label(
            tips,
            justify="left",
            text="- Pilih 'File' untuk menyalin file tunggal besar\n"
                 "- Pilih 'Folder' untuk menyalin seluruh isi folder\n"
                 "- File >1GB akan menggunakan buffer 64MB otomatis"
        ).pack(anchor="w")

    def browse_source(self):
        """Show appropriate dialog based on source type"""
        if self.source_type.get() == "File":
            path = filedialog.askopenfilename(title="Select File to Copy")
        else:
            path = filedialog.askdirectory(title="Select Source Folder")

        if path:
            self.source_path.set(path)
            # Auto-set destination to same directory for single file
            if self.source_type.get() == "File":
                self.dest_path.set(os.path.dirname(path))

    def browse_dest(self):
        """Show appropriate destination dialog based on source type"""
        if self.source_type.get() == "File":
            initial_file = os.path.basename(self.source_path.get())
            path = filedialog.asksaveasfilename(
                title="Save File As",
                initialfile=initial_file,
                defaultextension=os.path.splitext(initial_file)[1]
            )
        else:
            path = filedialog.askdirectory(title="Select Destination Folder")

        if path:
            self.dest_path.set(path)

    def start_copy(self):
        if not self.source_path.get() or not self.dest_path.get():
            messagebox.showerror("Error", "Please select source and destination")
            return

        src = self.source_path.get()
        dst = self.dest_path.get()

        if os.path.abspath(src) == os.path.abspath(dst):
            messagebox.showerror("Error", "Source and destination cannot be the same")
            return

        # Special check for single file overwrite
        if self.source_type.get() == "File" and os.path.isfile(dst):
            if not messagebox.askyesno("Confirm", "Target file exists. Overwrite?"):
                return

        self.cancel_flag.clear()
        self.progress.set(0.0)
        self.file_count.set(0)
        self.copied_bytes = 0
        self.total_bytes = 0
        self.status.set("Preparing...")
        self.speed.set("0 MB/s")
        self.eta.set("-")
        self.current_file.set("")

        threading.Thread(target=self._run_copy, daemon=True).start()
        self._start_time = time.time()
        self.root.after(200, self._tick_ui)

    def _run_copy(self):
        try:
            base_src = self.source_path.get()
            base_dst = self.dest_path.get()
            files = []

            if self.source_type.get() == "File":
                # Single file mode
                if not os.path.isfile(base_src):
                    raise ValueError("Source is not a file")

                filename = os.path.basename(base_src)
                if os.path.isdir(base_dst):
                    dst_path = os.path.join(base_dst, filename)
                else:
                    dst_path = base_dst

                size = os.path.getsize(base_src)
                files.append((base_src, dst_path, size))
                self.total_bytes = size

                # Create destination directory if needed
                dst_dir = os.path.dirname(dst_path)
                if dst_dir and not os.path.exists(dst_dir):
                    os.makedirs(dst_dir, exist_ok=True)
            else:
                # Folder mode
                if not os.path.isdir(base_src):
                    raise ValueError("Source is not a directory")

                for root_dir, _, filenames in os.walk(base_src):
                    rel_dir = os.path.relpath(root_dir, base_src)
                    for name in filenames:
                        src = os.path.join(root_dir, name)
                        rel_path = os.path.normpath(os.path.join(rel_dir, name))
                        dst = os.path.join(base_dst, rel_path)
                        try:
                            size = os.path.getsize(src)
                        except OSError:
                            continue
                        files.append((src, dst, size))
                        self.total_bytes += size

                # Create all directories in advance
                dirs_to_create = set(os.path.dirname(dst) for _, dst, _ in files)
                for d in dirs_to_create:
                    if d and not os.path.exists(d):
                        os.makedirs(d, exist_ok=True)

            if not files:
                self.status.set("No files to copy")
                return

            self.files_total.set(len(files))

            if len(files) == 1:
                # Single file copy
                src, dst, size = files[0]
                self.status.set(f"Copying: {os.path.basename(src)}")
                self._copy_file(src, dst, size)
            else:
                # Multiple files
                self.status.set(f"Copying {len(files)} files...")
                self._copy_multiple_files(files)

            if self.cancel_flag.is_set():
                self.status.set("Operation cancelled")
            else:
                self.status.set(f"Completed! Copied {self.file_count.get()} files")

        except Exception as e:
            self.status.set(f"Error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            if self.executor:
                self.executor.shutdown(wait=False)
                self.executor = None

    def _copy_multiple_files(self, files):
        """Handle folder copy with multiple files"""
        # Split files by size
        small_med = [(s, d, sz) for (s, d, sz) in files if sz < LARGE_FILE_MIN]
        large = [(s, d, sz) for (s, d, sz) in files if sz >= LARGE_FILE_MIN]

        # Determine worker count
        workers = self.cpu_count
        if len(small_med) > 5000:
            workers = min(self.cpu_count * 2, 64)

        self.executor = ThreadPoolExecutor(max_workers=workers)

        # Process small/medium files in parallel
        futures = []
        for (src, dst, size) in small_med:
            futures.append(self.executor.submit(self._copy_file, src, dst, size))

        for fut in as_completed(futures):
            if self.cancel_flag.is_set():
                break
            _ = fut.result()

        # Process large files one by one
        if not self.cancel_flag.is_set():
            for (src, dst, size) in large:
                if self.cancel_flag.is_set():
                    break
                self._copy_file(src, dst, size)

    def _copy_file(self, src, dst, size):
        """Copy a single file with progress updates"""
        if self.cancel_flag.is_set():
            return

        try:
            # Update current file (for multi-file operations)
            if self.files_total.get() > 1:
                self.current_file.set(os.path.basename(src))

            # Skip if file exists and is identical
            if os.path.exists(dst):
                try:
                    st_src = os.stat(src)
                    st_dst = os.stat(dst)
                    if st_src.st_size == st_dst.st_size and int(st_src.st_mtime) == int(st_dst.st_mtime):
                        self._add_progress(size)
                        self._inc_file()
                        return
                except OSError:
                    pass

            # Determine buffer size
            buffer_size = self._get_buffer_size(size)
            copied = 0

            with open(src, 'rb') as f_src, open(dst, 'wb') as f_dst:
                while not self.cancel_flag.is_set():
                    chunk = f_src.read(buffer_size)
                    if not chunk:
                        break
                    f_dst.write(chunk)
                    copied += len(chunk)
                    self._add_progress(len(chunk))

            # Preserve file metadata
            if not self.cancel_flag.is_set():
                try:
                    st = os.stat(src)
                    os.utime(dst, (st.st_atime, st.st_mtime))
                except OSError:
                    pass
                self._inc_file()

        except Exception as e:
            print(f"Error copying {src}: {e}")
            raise

    def _get_buffer_size(self, file_size):
        """Determine optimal buffer size for file copy"""
        if file_size > 1 * 1024 * 1024 * 1024:  # >1GB
            return 64 * 1024 * 1024  # 64MB
        elif file_size > 500 * 1024 * 1024:  # 500MB-1GB
            return 16 * 1024 * 1024  # 16MB
        elif file_size > 50 * 1024 * 1024:  # 50-500MB
            return 8 * 1024 * 1024  # 8MB
        else:  # <50MB
            return 4 * 1024 * 1024  # 4MB

    def _add_progress(self, nbytes):
        with self._bytes_lock:
            self.copied_bytes += nbytes

    def _inc_file(self):
        self.root.after(0, lambda: self.file_count.set(self.file_count.get() + 1))

    def _tick_ui(self):
        """Periodic UI update"""
        if self.total_bytes > 0:
            pct = (self.copied_bytes / self.total_bytes) * 100.0
            self.progress.set(min(100.0, pct))

            elapsed = max(0.001, time.time() - (self._start_time or time.time()))
            mbps = (self.copied_bytes / (1024 * 1024)) / elapsed
            self.speed.set(f"{mbps:.2f} MB/s")

            remaining = max(0, self.total_bytes - self.copied_bytes)
            if mbps > 0:
                eta_sec = remaining / (mbps * 1024 * 1024)
                if eta_sec >= 3600:
                    self.eta.set(f"{int(eta_sec // 3600)}h {int((eta_sec % 3600) // 60)}m")
                elif eta_sec >= 60:
                    self.eta.set(f"{int(eta_sec // 60)}m {int(eta_sec % 60)}s")
                else:
                    self.eta.set(f"{int(eta_sec)}s")

        if not self.cancel_flag.is_set() and self.progress.get() < 100.0:
            self.root.after(200, self._tick_ui)

    def cancel_copy(self):
        self.cancel_flag.set()
        self.status.set("Cancelling...")
        if self.executor:
            self.executor.shutdown(wait=False)
            self.executor = None

    def on_closing(self):
        self.cancel_copy()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = HybridCopyApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()