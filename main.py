import sys
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import pyreadstat

from modules.data_cleaner import DataCleaner
from modules.cli_interface import (
    select_single_variable, select_multiple_variables, get_speeder_threshold, 
    get_weighting_targets, select_analysis_type, select_prep_mode, get_cleaning_options, select_global_mode
)
from modules.data_weighter import DataWeighter
from modules.stat_engine import StatEngine

def select_file():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.askopenfilename(
        title="Wybierz bazę danych", 
        filetypes=[("SPSS/CSV", "*.sav *.csv")]
    )
    root.destroy()
    return file_path

def main():
    print("=========================================")
    print("   WUNDT: Zintegrowany System Analityczny")
    print("=========================================")
    
    global_mode = select_global_mode()
    
    file_path = select_file()
    if not file_path: sys.exit("Nie wybrano pliku.")

    try:
        meta = None
        if file_path.endswith('.csv'): df = pd.read_csv(file_path)
        else: df, meta = pyreadstat.read_sav(file_path)
    except Exception as e: sys.exit(f"Błąd wczytywania: {e}")

    columns = df.columns.tolist()
    prep_mode = select_prep_mode()
    final_df = df.copy()
    cleaner = DataCleaner(final_df)
    weight_targets = None
    data_was_modified = False

    clean_opts = {}
    time_col = None
    scale_items = []
    threshold = None

    # --- ETAP 1: CZYSZCZENIE ---
    if prep_mode in ['1', '2']:
        clean_opts = get_cleaning_options()
        time_col = select_single_variable(columns, "Zmienna określająca CZAS:") if clean_opts['speeders'] else None
        scale_items = select_multiple_variables(columns, "Zmienne skali (do braków/wariancji):") if any([clean_opts['missing'], clean_opts['straight_liners'], clean_opts['long_strings'], clean_opts['mahalanobis']]) else []

        if global_mode in ['2', '3']:
            if clean_opts['missing'] and scale_items:
                cleaner.df = cleaner.df.dropna(subset=scale_items, thresh=int(len(scale_items)*0.85)) 
            if clean_opts['long_strings'] and scale_items:
                max_str = input("Max ciąg identycznych odpowiedzi (np. 9): ").strip()
                if max_str.isdigit(): cleaner.remove_long_strings(scale_items, int(max_str))
            if clean_opts['straight_liners'] and scale_items:
                cleaner.remove_straight_liners(scale_items, 0.1)
            if clean_opts['mahalanobis'] and len(cleaner.df) > len(scale_items):
                cleaner.remove_mahalanobis_outliers(scale_items, 0.001)
            if clean_opts['speeders'] and time_col:
                threshold = get_speeder_threshold(final_df, time_col)
                if threshold: cleaner.remove_speeders(time_col, threshold)
            
            final_df = cleaner.df
            data_was_modified = True

    # --- ETAP 2: WAŻENIE ---
    if prep_mode in ['1', '3']:
        weight_vars = select_multiple_variables(final_df.columns.tolist(), "Wybierz zmienne do WAŻENIA:")
        if weight_vars:
            weight_targets = get_weighting_targets(final_df, weight_vars)
            if weight_targets and global_mode in ['2', '3']:
                for var, t_dict in weight_targets.items():
                    if var in final_df.columns: cleaner.auto_recode_from_targets(var, list(t_dict.keys()))
                final_df = cleaner.df
                weighter = DataWeighter(final_df)
                try: 
                    final_df = weighter.rake_weights(weight_targets).get_dataframe()
                    data_was_modified = True
                except Exception as e: print(f"Błąd ważenia: {e}")

    # --- ETAP 3: PANCERNY ZAPIS BAZY ---
    if data_was_modified and global_mode in ['2', '3']:
        save_path_sav = "Wundt_Oczyszczone_Dane.sav"
        save_path_csv = "Wundt_Oczyszczone_Dane.csv"
        print("\n[INFO] Przygotowywanie plików wynikowych bazy danych...")
        
        # Magia naprawcza: Defragmentacja pamięci RAM przed zapisem
        final_df = final_df.reset_index(drop=True)

        try:
            final_df.to_csv(save_path_csv, index=False, sep=';', decimal=',')
            print(f"[SUKCES] Zapisano ratunkową kopię CSV: {save_path_csv}")
        except Exception as e: print(f"[UWAGA] Błąd zapisu CSV: {e}")

        try:
            if meta:
                new_col_labels = [meta.column_names_to_labels.get(col, str(col)) for col in final_df.columns]
                safe_val_labels = {k: v for k, v in meta.variable_value_labels.items() if k in final_df.columns}
                pyreadstat.write_sav(final_df, save_path_sav, column_labels=new_col_labels, variable_value_labels=safe_val_labels)
            else:
                pyreadstat.write_sav(final_df, save_path_sav)
            print(f"[SUKCES] Zapisano oczyszczoną bazę SPSS: {save_path_sav}")
        except Exception as e: 
            print(f"[UWAGA] Zapis SAV zablokowany: {e}.")

    # --- ETAP 4: MODUŁ STATYSTYCZNY ---
    engine = StatEngine(final_df)
    current_cols = final_df.columns.tolist()
    history = [] 

    while True:
        analysis_choice = select_analysis_type()
        if analysis_choice == 0:
            print("\nZamykam program. Generowanie plików wyjściowych...")
            if history or prep_mode != '4':
                from modules.exporters import ExportManager
                prep_logs = cleaner.get_summary() if prep_mode in ['1', '2'] and global_mode in ['2','3'] else {}
                exporter = ExportManager(final_df, history, prep_logs, clean_opts, scale_items, time_col, threshold)
                
                exporter.export_spss_syntax(global_mode) 
                if global_mode == '3': 
                    exporter.export_excel()
                    exporter.export_pptx()
                print("\n[SUKCES] Pliki zostały wygenerowane zgodnie z wybraną architekturą.")
            break

        elif analysis_choice == 1:
            dvs = select_multiple_variables(current_cols, "Zmienne ZALEŻNE (wiele):")
            iv = select_single_variable(current_cols, "Zmienna NIEZALEŻNA (grupująca):")
            if dvs and iv: history.append(engine.compare_independent_groups(dvs, iv))

        elif analysis_choice == 2:
            vars_list = select_multiple_variables(current_cols, "Zmienne do pomiarów powtarzanych (min. 2):")
            if len(vars_list) >= 2: history.append(engine.compare_repeated_measures(vars_list))

        elif analysis_choice == 3:
            vars_list = select_multiple_variables(current_cols, "Zmienne do korelacji (min. 2):")
            if len(vars_list) >= 2:
                kierunek = input("Hipoteza: [1] Dwustronna czy [2] Jednostronna? (1/2): ").strip()
                history.append(engine.correlation_matrix(vars_list, 'greater' if kierunek == '2' else 'two-sided'))

        elif analysis_choice == 4:
            col = select_single_variable(current_cols, "Zmienna do T2B/B2B:")
            if col: history.append(engine.calculate_t2b_b2b(col, float(input("MIN: ")), float(input("MAX: "))))

        elif analysis_choice == 5:
            col = select_single_variable(current_cols, "Zmienna do NPS:")
            if col: history.append(engine.calculate_nps(col))

        elif analysis_choice == 6:
            cols = select_multiple_variables(current_cols, "Zmienne do Indeksu:")
            if cols:
                results = engine.create_index(cols, input("Nazwa dla indeksu: ").strip())
                history.append(results)
                if "Błąd" not in results[0]: current_cols = engine.df.columns.tolist()

        elif analysis_choice == 7:
            wave_col = select_single_variable(current_cols, "Zmienna definiująca FALĘ badania:")
            if wave_col:
                w1 = input("Kod FALI 1 (np. 1 lub 2023): ").strip()
                w2 = input("Kod FALI 2 (np. 2 lub 2024): ").strip()
                
                print("\n[1] Średnie  [2] NPS  [3] Top 2 Boxes (T2B)")
                m_choice = input("Wybór wskaźnika (1/2/3): ").strip()
                metric = 'mean' if m_choice == '1' else 'nps' if m_choice == '2' else 't2b'
                max_v = float(input("Górna granica skali (np. 5): ").strip()) if metric == 't2b' else None
                
                vars_list = select_multiple_variables(current_cols, f"Zmienne do Trackingu ({metric.upper()}):")
                if vars_list: history.append(engine.compare_waves(vars_list, wave_col, w1, w2, metric, max_v=max_v))

if __name__ == "__main__":
    main()