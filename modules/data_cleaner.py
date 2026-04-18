import pandas as pd
import numpy as np
from scipy.spatial import distance

class DataCleaner:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.log = {}

    def _update_log(self, name: str, original_len: int):
        self.log[name] = original_len - len(self.df)

    def remove_speeders(self, time_col: str, threshold: float):
        l = len(self.df)
        self.df = self.df[pd.to_numeric(self.df[time_col], errors='coerce') >= threshold]
        self._update_log("Usunięto Speeders", l)

    def remove_straight_liners(self, cols: list, var_threshold: float = 0.1):
        l = len(self.df)
        variances = self.df[cols].apply(pd.to_numeric, errors='coerce').var(axis=1)
        self.df = self.df[variances >= var_threshold]
        self._update_log("Usunięto Straight-liners", l)

    def remove_long_strings(self, cols: list, max_len: int):
        l = len(self.df)
        def max_consecutive(row):
            vals = row.dropna().values
            if len(vals) == 0: return 0
            changes = np.concatenate(([True], vals[:-1] != vals[1:], [True]))
            return np.diff(np.where(changes)[0]).max()
            
        self.df = self.df[self.df[cols].apply(max_consecutive, axis=1) <= max_len]
        self._update_log("Usunięto Long-strings", l)

    def remove_mahalanobis_outliers(self, cols: list, p_value_thresh: float = 0.001):
        l = len(self.df)
        clean_data = self.df[cols].apply(pd.to_numeric, errors='coerce').dropna()
        if len(clean_data) > len(cols):
            cov_mat = np.cov(clean_data.values.T)
            inv_cov = np.linalg.pinv(cov_mat)
            mean_vec = np.mean(clean_data.values, axis=0)
            dists = [distance.mahalanobis(row, mean_vec, inv_cov) for row in clean_data.values]
            from scipy.stats import chi2
            p_vals = 1 - chi2.cdf(np.square(dists), len(cols))
            safe_indices = clean_data.index[p_vals > p_value_thresh]
            self.df = self.df.loc[self.df.index.isin(safe_indices) | ~self.df.index.isin(clean_data.index)]
        self._update_log("Usunięto Outliers (Mahalanobis)", l)

    def auto_recode_from_targets(self, col: str, targets: list):
        """Pomaga rekodować np. wiek ciągły w przedziały przed ważeniem."""
        if self.df[col].dtype in ['int64', 'float64'] and any('-' in str(t) for t in targets):
            bins, labels = [-np.inf], []
            for t in targets:
                if '-' in str(t):
                    s, e = map(float, str(t).split('-'))
                    if len(bins) == 1: bins[0] = s - 0.1
                    bins.append(e)
                    labels.append(t)
            if len(labels) > 0:
                self.df[col] = pd.cut(self.df[col], bins=bins, labels=labels, right=True).astype(str)

    def get_summary(self) -> dict:
        return self.log