import sys
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import pyreadstat
import os
import numpy as np

from modules.data_cleaner import DataCleaner
from modules.data_weighter import DataWeighter
from modules.stat_engine import StatEngine
from modules.exporters import ExportManager

# ---------------------------------------------------------
# KLASA POMOCNICZA: Przewijana lista checkboxów
# ---------------------------------------------------------
class CheckListFrame(tk.Frame):
    def __init__(self, parent, label_text, **kwargs):
        super().__init__(parent, **kwargs)
        self.vars = {}  
        
        lbl = tk.Label(self, text=label_text, font=('Arial', 10, 'bold'))
        lbl.pack(anchor=tk.W, pady=(0,5))

        self.canvas = tk.Canvas(self, height=200, width=280, bg="white", highlightthickness=1)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def update_items(self, items):
        for child in self.scrollable_frame.winfo_children():
            child.destroy()
        self.vars = {}
        for item in items:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.scrollable_frame, text=item, variable=var, bg="white")
            chk.pack(anchor=tk.W)
            self.vars[item] = var

    def get_checked(self):
        return [name for name, var in self.vars.items() if var.get()]

# ---------------------------------------------------------
# GŁÓWNA APLIKACJA GUI
# ---------------------------------------------------------
class ToddlerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Toddler - Zintegrowany System Analityczny 2.2")
        self.root.geometry("1150x850")
        
        self.spss_path = ""
        self.variables = []
        self.meta = None
        self.stats_queue = []
        self.weight_entries = {} 

        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Zakładki
        self.tab_file = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_file, text="1. Plik i Tryb")
        self.build_tab_file()

        self.tab_clean = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_clean, text="2. Czyszczenie (QC)")
        self.build_tab_clean()

        self.tab_weight = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_weight, text="3. Ważenie (IPF)")
        self.build_tab_weight()

        self.tab_stats = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_stats, text="4. Statystyki")
        self.build_tab_stats()

        # Przycisk uruchomienia
        self.btn_run = tk.Button(self.root, text="URUCHOM ANALIZĘ", bg="#4CAF50", fg="white", font=('Arial', 14, 'bold'), command=self.run_pipeline)
        self.btn_run.pack(fill=tk.X, padx=10, pady=10, ipady=10)

    # =====================================================
    # ZAKŁADKA 1: PLIK
    # =====================================================
    def build_tab_file(self):
        tk.Button(self.tab_file, text="Wczytaj bazę (.sav / .csv)", bg="#ff9800", fg="white", font=('Arial', 11, 'bold'), command=self.load_file).pack(pady=20)
        self.lbl_file = tk.Label(self.tab_file, text="Nie wybrano pliku", fg="gray")
        self.lbl_file.pack()

        frame_mode = tk.LabelFrame(self.tab_file, text="Architektura Pracy", font=('Arial', 10, 'bold'), padx=20, pady=20)
        frame_mode.pack(fill=tk.X, padx=40, pady=20)

        self.var_global_mode = tk.StringVar(value="3")
        tk.Radiobutton(frame_mode, text="[1] Tylko Syntax (.sps) - Generuje kod, bez zapisu raportów", variable=self.var_global_mode, value="1").pack(anchor=tk.W, pady=5)
        tk.Radiobutton(frame_mode, text="[2] Hybryda - Czyszczenie/Ważenie i zapis nowej bazy, statystyka tylko w .sps", variable=self.var_global_mode, value="2").pack(anchor=tk.W, pady=5)
        tk.Radiobutton(frame_mode, text="[3] Pełen Kombajn - Eksport kompletnych raportów (XLSX, PPTX, SAV, SPS)", variable=self.var_global_mode, value="3").pack(anchor=tk.W, pady=5)

    # =====================================================
    # ZAKŁADKA 2: CZYSZCZENIE (Zmiany w układzie)
    # =====================================================
    def build_tab_clean(self):
        container = tk.Frame(self.tab_clean)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        left_frame = tk.Frame(container)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        # ZBIORCZA RAMKA: FILTRY
        frame_filters = tk.LabelFrame(left_frame, text="FILTRY", font=('Arial', 12, 'bold'), padx=10, pady=10)
        frame_filters.pack(fill=tk.BOTH, expand=True)

        # Braki danych
        self.chk_miss = tk.BooleanVar(value=True)
        tk.Checkbutton(frame_filters, text="Usuwaj braki danych", variable=self.chk_miss, font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        tk.Label(frame_filters, text="Maksymalny % braków w skali (np. 15):").pack(anchor=tk.W)
        self.entry_missing_thr = tk.Entry(frame_filters, width=10)
        self.entry_missing_thr.insert(0, "50")
        self.entry_missing_thr.pack(anchor=tk.W, pady=(0, 10))

        # Straight-liners
        self.chk_straight = tk.BooleanVar(value=True)
        tk.Checkbutton(frame_filters, text="Straight-liners (Niska wariancja)", variable=self.chk_straight, font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        tk.Label(frame_filters, text="Próg wariancji:").pack(anchor=tk.W)
        self.entry_var_thr = tk.Entry(frame_filters, width=10)
        self.entry_var_thr.insert(0, "0.2")
        self.entry_var_thr.pack(anchor=tk.W, pady=(0, 10))

        # Speeders
        self.chk_speed = tk.BooleanVar(value=True)
        tk.Checkbutton(frame_filters, text="Speeders (Zbyt szybko)", variable=self.chk_speed, font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        tk.Label(frame_filters, text="Zmienna czasu dla Speeders:").pack(anchor=tk.W)
        self.combo_time = ttk.Combobox(frame_filters, state="readonly", width=30)
        self.combo_time.pack(anchor=tk.W)
        tk.Label(frame_filters, text="Minimalny czas wypełnienia (sekundy):").pack(anchor=tk.W)
        self.entry_speed_thr = tk.Entry(frame_filters, width=10)
        self.entry_speed_thr.insert(0, "120") # Domyślna wartość, którą można zmienić
        self.entry_speed_thr.pack(anchor=tk.W, pady=(0, 10))

        # Long-strings
        self.chk_long = tk.BooleanVar(value=True)
        tk.Checkbutton(frame_filters, text="Long-strings (Ciągi odpowiedzi)", variable=self.chk_long, font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        tk.Label(frame_filters, text="Maksymalny dozwolony ciąg (np. 9):").pack(anchor=tk.W)
        self.entry_longstr = tk.Entry(frame_filters, width=10)
        self.entry_longstr.insert(0, "5")
        self.entry_longstr.pack(anchor=tk.W, pady=(0, 10))

        # Mahalanobis
        self.chk_mahal = tk.BooleanVar()
        tk.Checkbutton(frame_filters, text="Mahalanobis (Anomalie wielowymiarowe)", variable=self.chk_mahal, font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 10))

        # Prawa strona - Checkboxy dla zmiennych
        self.check_list_clean = CheckListFrame(container, "Wybierz zmienne do analizy (Baterie Skal):")
        self.check_list_clean.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # =====================================================
    # ZAKŁADKA 3: WAŻENIE
    # =====================================================
    def build_tab_weight(self):
        container = tk.Frame(self.tab_weight)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.chk_weighting = tk.BooleanVar()
        tk.Checkbutton(container, text="WŁĄCZ MODUŁ WAŻENIA (IPF)", variable=self.chk_weighting, font=('Arial', 12, 'bold'), fg="blue").pack(anchor=tk.W, pady=(0, 10))

        content_frame = tk.Frame(container)
        content_frame.pack(fill=tk.BOTH, expand=True)

        self.check_list_weight = CheckListFrame(content_frame, "Wybierz zmienne do WAŻENIA:")
        self.check_list_weight.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        right_frame = tk.LabelFrame(content_frame, text="Nadaj wagi kategoriom (wpisz proporcje, np. 0.5)", padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Wybór źródła wag
        self.var_weight_src = tk.StringVar(value="manual")
        tk.Radiobutton(right_frame, text="Ustaw cele ręcznie", variable=self.var_weight_src, value="manual").pack(anchor=tk.W)
        tk.Radiobutton(right_frame, text="Wczytaj cele z pliku Excel/CSV", variable=self.var_weight_src, value="file").pack(anchor=tk.W)
        
        btn_frame = tk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        self.btn_weight_file = tk.Button(btn_frame, text="Wybierz plik Excel", command=self.load_weight_file)
        self.btn_weight_file.pack(side=tk.LEFT)
        self.lbl_weight_file = tk.Label(btn_frame, text="Brak pliku", fg="gray")
        self.lbl_weight_file.pack(side=tk.LEFT, padx=10)

        tk.Button(right_frame, text="ZAŁADUJ KATEGORIE ZAZNACZONYCH ZMIENNYCH", bg="#2196F3", fg="white", font=('Arial', 9, 'bold'), command=self.refresh_weight_inputs).pack(fill=tk.X, pady=10)

        self.weight_canvas = tk.Canvas(right_frame, bg="#f0f0f0")
        self.weight_scroll = ttk.Scrollbar(right_frame, orient="vertical", command=self.weight_canvas.yview)
        self.weight_editor = tk.Frame(self.weight_canvas, bg="#f0f0f0")
        
        self.weight_editor.bind("<Configure>", lambda e: self.weight_canvas.configure(scrollregion=self.weight_canvas.bbox("all")))
        self.weight_canvas.create_window((0, 0), window=self.weight_editor, anchor="nw")
        self.weight_canvas.configure(yscrollcommand=self.weight_scroll.set)
        
        self.weight_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.weight_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_weight_inputs(self):
        for child in self.weight_editor.winfo_children(): child.destroy()
        self.weight_entries = {}
        
        selected = self.check_list_weight.get_checked()
        if not selected or not self.spss_path: return

        df = pd.read_csv(self.spss_path) if self.spss_path.endswith('.csv') else pyreadstat.read_sav(self.spss_path)[0]

        for var in selected:
            frame = tk.Frame(self.weight_editor, pady=5, bg="#e0e0e0", relief=tk.RIDGE, bd=1)
            frame.pack(fill=tk.X, pady=5, padx=5)
            tk.Label(frame, text=f"ZMIENNA: {var}", font=('Arial', 10, 'bold'), bg="#e0e0e0").pack(anchor=tk.W, padx=5, pady=2)
            
            categories = df[var].dropna().unique()
            cat_container = tk.Frame(frame, bg="#e0e0e0")
            
            if pd.api.types.is_numeric_dtype(df[var]) and len(categories) > 8:
                recode_frame = tk.Frame(frame, bg="#e0e0e0")
                recode_frame.pack(fill=tk.X, padx=5, pady=2)
                tk.Label(recode_frame, text="Wpisz przedziały po przecinku (np. 18-24, 25-34, 35-99):", bg="#e0e0e0", fg="#d32f2f", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
                
                entry_bins = tk.Entry(recode_frame, width=40)
                entry_bins.pack(side=tk.LEFT)
                
                btn = tk.Button(recode_frame, text="Zastosuj przedziały", command=lambda v=var, e=entry_bins, c=cat_container: self.render_weight_rows(v, [b.strip() for b in e.get().split(',') if b.strip()], c))
                btn.pack(side=tk.LEFT, padx=5)

            cat_container.pack(fill=tk.X, padx=5, pady=5)
            self.render_weight_rows(var, categories, cat_container)

    def render_weight_rows(self, var, categories, container):
        for child in container.winfo_children(): child.destroy()
        self.weight_entries[var] = {}
        
        for cat in categories:
            row = tk.Frame(container, bg="#e0e0e0")
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=f"Kategoria [{cat}]:", width=20, anchor=tk.W, bg="#e0e0e0").pack(side=tk.LEFT)
            ent = tk.Entry(row, width=10)
            ent.pack(side=tk.LEFT, padx=10)
            self.weight_entries[var][cat] = ent

    # =====================================================
    # ZAKŁADKA 4: STATYSTYKI
    # =====================================================
    def build_tab_stats(self):
        top = tk.Frame(self.tab_stats)
        top.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(top, text="Wybierz typ analizy:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.combo_stat_type = ttk.Combobox(top, state="readonly", width=50, values=[
            "1. Porównanie grup niezależnych (t-Student, ANOVA)",
            "2. Pomiary powtarzane (t-Zależne, Wilcoxon)",
            "3. Korelacja (Pearson, Spearman)",
            "4. Analiza Wskaźnikowa: T2B / B2B",
            "5. Analiza Wskaźnikowa: NPS",
            "6. Tworzenie Indeksu (Średnia + Alfa Cronbacha)",
            "7. Tracking (Porównanie dwóch Fal)"
        ])
        self.combo_stat_type.pack(side=tk.LEFT, padx=10)
        
        self.frame_stat_params = tk.LabelFrame(self.tab_stats, text="Parametry Analizy", padx=10, pady=10)
        self.frame_stat_params.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Button(self.tab_stats, text="+ DODAJ ANALIZĘ DO KOLEJKI", bg="#2196F3", fg="white", font=('Arial', 10, 'bold'), command=self.add_to_queue).pack(pady=10)

        tk.Label(self.tab_stats, text="Kolejka zleconych analiz:", font=('Arial', 9, 'bold')).pack(anchor=tk.W, padx=10)
        self.listbox_queue = tk.Listbox(self.tab_stats, height=6)
        self.listbox_queue.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(self.tab_stats, text="Usuń zaznaczoną analizę z kolejki", command=lambda: self.listbox_queue.delete(tk.ANCHOR)).pack()

        self.combo_stat_type.bind("<<ComboboxSelected>>", self.update_stat_params)

    def update_stat_params(self, event=None):
        for widget in self.frame_stat_params.winfo_children(): widget.destroy()
        sel = self.combo_stat_type.get()
        if not sel: return

        self.check_list_stats = CheckListFrame(self.frame_stat_params, "Zmienne poddawane analizie:")
        self.check_list_stats.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.check_list_stats.update_items(self.variables)

        right = tk.Frame(self.frame_stat_params)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        if sel.startswith("1"):
            tk.Label(right, text="Zmienna Grupująca (Niezależna):").pack(anchor=tk.W)
            self.combo_stat_group = ttk.Combobox(right, values=self.variables, state="readonly")
            self.combo_stat_group.pack(anchor=tk.W, fill=tk.X)
        elif sel.startswith("6"):
            tk.Label(right, text="Nazwa nowego Indeksu:").pack(anchor=tk.W)
            self.entry_index_name = tk.Entry(right)
            self.entry_index_name.pack(anchor=tk.W, fill=tk.X)
        elif sel.startswith("7"):
            tk.Label(right, text="Zmienna definiująca Falę:").pack(anchor=tk.W)
            self.combo_stat_wave = ttk.Combobox(right, values=self.variables, state="readonly")
            self.combo_stat_wave.pack(anchor=tk.W, fill=tk.X, pady=(0, 10))
            tk.Label(right, text="Kod Fali 1 (np. 1 lub 2023):").pack(anchor=tk.W)
            self.entry_w1 = tk.Entry(right)
            self.entry_w1.pack(anchor=tk.W, fill=tk.X, pady=(0, 5))
            tk.Label(right, text="Kod Fali 2:").pack(anchor=tk.W)
            self.entry_w2 = tk.Entry(right)
            self.entry_w2.pack(anchor=tk.W, fill=tk.X, pady=(0, 10))
            tk.Label(right, text="Metryka (mean / nps / t2b):").pack(anchor=tk.W)
            self.combo_tracking_metric = ttk.Combobox(right, values=['mean', 'nps', 't2b'], state="readonly")
            self.combo_tracking_metric.current(0)
            self.combo_tracking_metric.pack(anchor=tk.W, fill=tk.X)

    # =====================================================
    # LOGIKA
    # =====================================================
    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("SPSS/CSV", "*.sav *.csv")])
        if path:
            self.spss_path = path
            self.lbl_file.config(text=os.path.basename(path), fg="black")
            try:
                df = pd.read_csv(path, nrows=1) if path.endswith('.csv') else pyreadstat.read_sav(path, metadataonly=True)[0]
                self.variables = df.columns.tolist()
                
                self.combo_time['values'] = self.variables
                self.check_list_clean.update_items(self.variables)
                self.check_list_weight.update_items(self.variables)
                
                messagebox.showinfo("Sukces", f"Pomyślnie wczytano plik.\nLiczba zmiennych: {len(self.variables)}")
            except Exception as e:
                messagebox.showerror("Błąd", f"Błąd wczytywania:\n{e}")

    def load_weight_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xls *.csv")])
        if path:
            self.weight_file_path = path
            self.lbl_weight_file.config(text=os.path.basename(path), fg="black")

    def add_to_queue(self):
        sel_type = self.combo_stat_type.get()
        if not sel_type: return
        
        sel_vars = self.check_list_stats.get_checked()
        if not sel_vars:
            messagebox.showwarning("Uwaga", "Wybierz przynajmniej jedną zmienną poddawaną analizie.")
            return

        task = {"type": sel_type[:1], "name": sel_type.split(". ")[1], "vars": sel_vars}

        if task["type"] == "1":
            group_var = getattr(self, 'combo_stat_group', None)
            if not group_var or not group_var.get(): return messagebox.showwarning("Uwaga", "Wybierz zmienną grupującą.")
            task["group"] = group_var.get()
        elif task["type"] == "6":
            idx_name = getattr(self, 'entry_index_name', None)
            if not idx_name or not idx_name.get(): return messagebox.showwarning("Uwaga", "Podaj nazwę indeksu.")
            task["idx_name"] = idx_name.get().strip()
        elif task["type"] == "7":
            wave_var = getattr(self, 'combo_stat_wave', None)
            if not wave_var or not wave_var.get(): return
            task["wave_var"] = wave_var.get()
            task["w1"] = self.entry_w1.get().strip()
            task["w2"] = self.entry_w2.get().strip()
            task["metric"] = self.combo_tracking_metric.get()

        self.stats_queue.append(task)
        desc = f"[{task['name']}] Zmienne: {len(task['vars'])}"
        if "group" in task: desc += f" by {task['group']}"
        self.listbox_queue.insert(tk.END, desc)

    def run_pipeline(self):
        if not self.spss_path:
            return messagebox.showerror("Błąd", "Najpierw wczytaj bazę danych (Zakładka 1).")

        global_mode = self.var_global_mode.get()
        
        try:
            if self.spss_path.endswith('.csv'): df = pd.read_csv(self.spss_path)
            else: df, self.meta = pyreadstat.read_sav(self.spss_path)
        except Exception as e:
            return messagebox.showerror("Błąd", f"Nie można odczytać danych:\n{e}")
            
        final_df = df.copy()
        cleaner = DataCleaner(final_df)
        data_modified = False

        scale_items = self.check_list_clean.get_checked()
        missing_thr = float(self.entry_missing_thr.get() or 15) / 100
        variance_thr = float(self.entry_var_thr.get() or 0.1)
        
        clean_opts = {
            'speeders': self.chk_speed.get(),
            'straight_liners': self.chk_straight.get(),
            'long_strings': self.chk_long.get(),
            'mahalanobis': self.chk_mahal.get(),
            'missing': self.chk_miss.get()
        }

        # --- ETAP 1: CZYSZCZENIE ---
        if any(clean_opts.values()) and global_mode in ['2', '3']:
            if clean_opts['missing'] and scale_items:
                cleaner.df = cleaner.df.dropna(subset=scale_items, thresh=int(len(scale_items)*(1.0 - missing_thr)))
            if clean_opts['long_strings'] and scale_items:
                max_str = int(self.entry_longstr.get() or 9)
                cleaner.remove_long_strings(scale_items, max_str)
            if clean_opts['straight_liners'] and scale_items:
                cleaner.remove_straight_liners(scale_items, variance_thr)
            if clean_opts['mahalanobis'] and len(cleaner.df) > len(scale_items):
                cleaner.remove_mahalanobis_outliers(scale_items, 0.001)
            if clean_opts['speeders']:
                time_col = self.combo_time.get()
                if time_col:
                    try:
                        speed_thr = float(self.entry_speed_thr.get())
                    except ValueError:
                        speed_thr = cleaner.df[time_col].median() * 0.35 # Zabezpieczenie, wraca do starej zasady 35% mediany jeśli pole jest puste
                    cleaner.remove_speeders(time_col, speed_thr)
            
            final_df = cleaner.df
            data_modified = True

        # --- ETAP 2: WAŻENIE ---
        weight_vars = self.check_list_weight.get_checked()
        if self.chk_weighting.get() and weight_vars and global_mode in ['2', '3']:
            targets = {}
            if self.var_weight_src.get() == "manual":
                for var in weight_vars:
                    if var in self.weight_entries:
                        var_targets = {}
                        for cat, ent in self.weight_entries[var].items():
                            val = ent.get().strip()
                            if val: var_targets[cat] = float(val)
                        if var_targets: targets[var] = var_targets
            else:
                if hasattr(self, 'weight_file_path'):
                    w_df = pd.read_excel(self.weight_file_path) if self.weight_file_path.endswith('.xlsx') else pd.read_csv(self.weight_file_path)
                    for var in weight_vars:
                        v_data = w_df[w_df.iloc[:, 0] == var]
                        if not v_data.empty: targets[var] = dict(zip(v_data.iloc[:, 1], v_data.iloc[:, 2]))

            if targets:
                # Automatyczne rekodowanie roczników na przedziały zdefiniowane w interfejsie
                for var, t_dict in targets.items():
                    if var in final_df.columns:
                        cleaner.auto_recode_from_targets(var, list(t_dict.keys()))
                
                final_df = cleaner.df 
                weighter = DataWeighter(final_df)
                try:
                    final_df = weighter.rake_weights(targets).get_dataframe()
                    data_modified = True
                except Exception as e:
                    messagebox.showerror("Błąd ważenia", str(e))

        # --- ETAP 3: ZAPIS ZMODYFIKOWANEJ BAZY ---
        if data_modified and global_mode in ['2', '3']:
            final_df = final_df.reset_index(drop=True)
            try:
                base_dir = os.path.dirname(self.spss_path)
                save_path = os.path.join(base_dir, "Wundt_Oczyszczone.sav")
                
                if hasattr(self, 'meta') and self.meta:
                    new_col_labels = [self.meta.column_names_to_labels.get(col, str(col)) for col in final_df.columns]
                    safe_val_labels = {k: v for k, v in self.meta.variable_value_labels.items() if k in final_df.columns}
                    pyreadstat.write_sav(final_df, save_path, column_labels=new_col_labels, variable_value_labels=safe_val_labels)
                else:
                    pyreadstat.write_sav(final_df, save_path)
            except Exception as e:
                messagebox.showerror("Błąd zapisu", f"Nie można zapisać bazy SAV:\n{e}")

        # --- ETAP 4: SILNIK STATYSTYCZNY ---
        history = []
        if self.stats_queue:
            engine = StatEngine(final_df)
            for task in self.stats_queue:
                t = task["type"]
                vars_list = task["vars"]
                try:
                    if t == "1": history.append(engine.compare_independent_groups(vars_list, task["group"]))
                    elif t == "2": history.append(engine.compare_repeated_measures(vars_list))
                    elif t == "3": history.append(engine.correlation_matrix(vars_list))
                    elif t == "4":
                        for v in vars_list: history.append(engine.calculate_t2b_b2b(v, 1, 5))
                    elif t == "5":
                        for v in vars_list: history.append(engine.calculate_nps(v))
                    elif t == "6":
                        res = engine.create_index(vars_list, task["idx_name"])
                        history.append(res)
                        final_df = engine.df 
                    elif t == "7":
                        history.append(engine.compare_waves(vars_list, task["wave_var"], task["w1"], task["w2"], task["metric"]))
                except Exception as e:
                    messagebox.showerror("Błąd Analizy", f"Błąd w obliczeniach dla testu {task['name']}:\n{e}")

        # --- ETAP 5: EKSPORTY (XLSX, PPTX, SPS) ---
        prep_logs = cleaner.get_summary() if global_mode in ['2','3'] else {}
        time_col_val = self.combo_time.get() if clean_opts['speeders'] else None
        
        exporter = ExportManager(
            df=final_df, 
            history=history, 
            prep_summary=prep_logs, 
            clean_opts=clean_opts, 
            scale_items=scale_items, 
            time_col=time_col_val, 
            speeder_threshold=None
        )
        
        exporter.export_spss_syntax(global_mode)
        
        if global_mode == '3':
            if history:
                exporter.export_excel()
                exporter.export_pptx()
                msg = "Proces analityczny zakończony!\n\nWygenerowano i zapisano pliki w folderze głównym skryptu:\n- Zaktualizowaną bazę SAV\n- Syntax SPS\n- Raport Excel (XLSX)\n- Prezentację PowerPoint (PPTX)"
            else:
                msg = "Proces oczyszczania zakończony!\nZapisano oczyszczoną bazę (SAV) oraz plik Syntax (SPS).\n\nUWAGA: Pliki Excel (XLSX) i PPTX nie zostały wygenerowane, ponieważ nie zleciłeś żadnych analiz statystycznych do kolejki (Zakładka 4)."
            messagebox.showinfo("Zakończono", msg)
        else:
            messagebox.showinfo("Zakończono", "Proces zdefiniowany przez wybrany tryb architektury zakończył się pomyślnie!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ToddlerGUI(root)
    root.mainloop()
