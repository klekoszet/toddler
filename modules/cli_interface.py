import pandas as pd
import tkinter as tk
from tkinter import filedialog

def print_menu(options: list):
    for i, option in enumerate(options):
        end_char = "\t" if (i + 1) % 2 != 0 else "\n"
        print(f"[{i}] {option:<35}", end=end_char)
    print() 

def select_single_variable(columns: list, prompt_text: str) -> str:
    print(f"\n{'-'*50}\n{prompt_text}")
    print_menu(columns)
    while True:
        try:
            choice = input("\nPodaj numer zmiennej (lub wciśnij Enter, aby pominąć): ").strip()
            if not choice: return None
            idx = int(choice)
            if 0 <= idx < len(columns): return columns[idx]
            print("Błąd: Liczba spoza zakresu.")
        except ValueError:
            print("Błąd: Wprowadź poprawną liczbę.")

def select_multiple_variables(columns: list, prompt_text: str) -> list:
    print(f"\n{'-'*50}\n{prompt_text}")
    print_menu(columns)
    while True:
        try:
            choice = input("\nPodaj numery (np. 1, 2, 5-8, lub Enter aby pominąć): ").strip()
            if not choice: return []
            selected_vars = []
            for part in choice.split(','):
                part = part.strip()
                if '-' in part:  
                    start, end = map(int, part.split('-'))
                    selected_vars.extend(columns[start : end + 1])
                else:
                    selected_vars.append(columns[int(part)])
            return list(dict.fromkeys(selected_vars))
        except (ValueError, IndexError):
            print("Błąd: Nieprawidłowy format. Spróbuj ponownie.")

def get_speeder_threshold(df: pd.DataFrame, time_col: str):
    if not time_col: return None
    print(f"\n--- Konfiguracja Speeders ({time_col}) ---")
    print("[1] Ręcznie (sekundy)\n[2] Automatycznie (35% mediany)")
    choice = input("Wybór [1/2]: ").strip()
    if choice == '1': return float(input("Podaj minimum sekund: "))
    elif choice == '2':
        med = df[time_col].median()
        print(f"Mediana: {med:.2f}s. Próg: {med*0.35:.2f}s.")
        return med * 0.35
    return None

def get_weighting_targets(df: pd.DataFrame, selected_vars: list) -> dict:
    if not selected_vars: return {}
    print("\n--- Konfiguracja Ważenia ---")
    print("[1] Wpisz ręcznie\n[2] Import z pliku (Excel/CSV)")
    choice = input("Wybór [1/2]: ").strip()
    
    if choice == '1':
        targets = {}
        for var in selected_vars:
            print(f"\nZmienna: {var}")
            unique_vals = df[var].dropna().unique()
            categories_to_weight = unique_vals
            
            if len(unique_vals) > 10:
                ans = input("Czy chcesz nadać wagi dla PRZEDZIAŁÓW (np. 18-25, 26-40)? [t/n]: ").strip().lower()
                if ans == 't':
                    cat_str = input("Podaj nazwy przedziałów oddzielone przecinkami (np. 18-25, 26-40): ")
                    categories_to_weight = [c.strip() for c in cat_str.split(',')]
            
            var_targets = {}
            for cat in categories_to_weight:
                while True:
                    try:
                        prop = float(input(f"  Proporcja dla '{cat}' (np. 0.52): "))
                        if 0 <= prop <= 1:
                            var_targets[cat] = prop
                            break
                    except ValueError: print("  Błąd: Poprawna liczba (z kropką).")
            targets[var] = var_targets
        return targets
    elif choice == '2':
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        file_path = filedialog.askopenfilename(title="Wybierz plik wag (Excel/CSV)", filetypes=[("Excel/CSV", "*.xlsx *.csv")])
        root.destroy()
        if not file_path: return {}
        config_df = pd.read_excel(file_path) if file_path.endswith('.xlsx') else pd.read_csv(file_path)
        targets = {}
        for var in selected_vars:
            var_data = config_df[config_df.iloc[:, 0] == var]
            if not var_data.empty:
                targets[var] = dict(zip(var_data.iloc[:, 1], var_data.iloc[:, 2]))
        return targets
    return {}

def select_prep_mode() -> str:
    print("\n" + "="*50)
    print("--- ETAP 1: TRYB PRZYGOTOWANIA DANYCH ---")
    print("[1] Pełne (Czyszczenie + Ważenie)")
    print("[2] TYLKO Czyszczenie")
    print("[3] TYLKO Ważenie")
    print("[4] Pomiń przygotowanie (surowa baza)")
    while True:
        choice = input("Wybierz tryb (1-4): ").strip()
        if choice in ['1', '2', '3', '4']: return choice

def get_cleaning_options() -> dict:
    print("\n--- KONFIGURACJA CZYSZCZENIA ---")
    print("Wybierz (t/n), aby włączyć/wyłączyć filtry:")
    return {
        "missing": input("Usuwać braki danych (>15% w skali)? [t/n]: ").strip().lower() == 't',
        "speeders": input("Usuwać speedersów (zbyt krótki czas)? [t/n]: ").strip().lower() == 't',
        "straight_liners": input("Usuwać straight-linerów (niska wariancja)? [t/n]: ").strip().lower() == 't',
        "long_strings": input("Usuwać powtarzalne ciągi (Long-strings)? [t/n]: ").strip().lower() == 't',
        "mahalanobis": input("Usuwać anomalie wielowymiarowe (Mahalanobis)? [t/n]: ").strip().lower() == 't'
    }

def select_analysis_type() -> int:
    print("\n" + "="*50)
    print("--- MODUŁ STATYSTYCZNY I BIZNESOWY ---")
    options = [
        "[1] Porównanie grup niezależnych (np. t-Student, ANOVA)",
        "[2] Pomiary powtarzane (np. pre-test vs post-test)",
        "[3] Korelacja (np. r Pearsona, rho Spearmana)",
        "[4] Analiza T2B / B2B (Top / Bottom 2 Boxes)",
        "[5] Net Promoter Score (NPS)",
        "[6] Tworzenie Indeksu (Średnia + Alfa Cronbacha)",
        "[7] Analiza Trackingowa (Porównanie dwóch Fal: Średnie / NPS / T2B)",
        "[0] Zakończ program i generuj raporty (XLSX, PPTX, SPS)"
    ]
    for opt in options: print(opt)
    while True:
        choice = input("\nWybierz analizę (0-7): ").strip()
        if choice in [str(i) for i in range(8)]: return int(choice)

def select_global_mode() -> str:
    print("\n" + "="*50)
    print("--- ARCHITEKTURA PRACY SYSTEMU ---")
    print("[1] TYLKO SYNTAX: Generator kodu .sps (Brak XLSX/PPTX/SAV)")
    print("[2] HYBRYDA: Python czyści/waży i zapisuje .SAV, reszta to Syntax .sps")
    print("[3] PEŁEN KOMBAJN: Python robi wszystko (zapisuje SAV, XLSX, PPTX oraz .sps)")
    while True:
        choice = input("Wybierz tryb (1-3): ").strip()
        if choice in ['1', '2', '3']: return choice