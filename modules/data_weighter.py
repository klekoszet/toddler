import pandas as pd
import numpy as np

class DataWeighter:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.weight_col = 'waga_analityczna'
        self.df[self.weight_col] = 1.0

    def rake_weights(self, target_distributions: dict, max_iterations=15, tolerance=0.005):
        print("\n[Ważenie] Uruchamianie bezpiecznego algorytmu Rakingu...")
        for iteration in range(max_iterations):
            max_dev = 0.0
            
            for col, targets in target_distributions.items():
                if col not in self.df.columns: continue
                total_w = self.df[self.weight_col].sum()
                
                for cat, target_prop in targets.items():
                    mask = (self.df[col].astype(str).str.strip() == str(cat).strip())
                    if not mask.any(): continue
                    
                    current_prop = self.df.loc[mask, self.weight_col].sum() / total_w
                    if current_prop > 0:
                        adjustment = target_prop / current_prop
                        adjustment = min(max(adjustment, 0.01), 100.0) 
                        self.df.loc[mask, self.weight_col] *= adjustment
                        max_dev = max(max_dev, abs(target_prop - current_prop))
            
            if max_dev < tolerance:
                print(f"[Ważenie] Sukces! Zbieżność po {iteration + 1} iteracjach.")
                break
        
        return self._trim_and_normalize()

    def _trim_and_normalize(self, upper=3.0, lower=0.33):
        print("[Ważenie] Nakładanie limitów (Trimming) i wyrównywanie bazy...")
        n = len(self.df)
        current_sum = self.df[self.weight_col].sum()
        if current_sum > 0: self.df[self.weight_col] *= (n / current_sum)
        
        # Szybki numpy clip ratujący pamięć
        self.df[self.weight_col] = np.clip(self.df[self.weight_col].values, lower, upper)
        
        final_sum = self.df[self.weight_col].sum()
        if final_sum > 0: self.df[self.weight_col] *= (n / final_sum)
        print("[Ważenie] Zakończono z sukcesem.")
        return self

    def get_dataframe(self) -> pd.DataFrame:
        return self.df