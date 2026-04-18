import pandas as pd
import numpy as np
from scipy import stats
import itertools

class StatEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def _check_normality(self, data: np.ndarray, name: str = "Zmienna") -> tuple:
        n = len(data)
        if n < 3: return False, f"[{name}] Zbyt mała próba."
        if n <= 100: stat, p_val = stats.shapiro(data); test_name = "Shapiro-Wilk"
        else: stat, p_val = stats.kstest(data, 'norm', args=(np.mean(data), np.std(data, ddof=1))); test_name = "K-S"
        return p_val >= 0.05, ""

    def compare_independent_groups(self, dvs: list, iv: str, apply_bonferroni: bool = True):
        batch_results = []
        k_tests = len(dvs) 
        for dv in dvs:
            if dv not in self.df.columns or iv not in self.df.columns: continue
            data = self.df[[dv, iv]].dropna()
            categories = data[iv].unique()
            groups = [data[data[iv] == cat][dv].values for cat in categories]
            if len(categories) < 2: continue
            
            all_normal = all(self._check_normality(g)[0] for g in groups)
            _, p_lev = stats.levene(*groups)
            is_var_equal = p_lev >= 0.05
            
            if len(categories) == 2:
                g1, g2 = groups[0], groups[1]
                if not all_normal: t_name, stat, p_val = "Manna-Whitneya", *stats.mannwhitneyu(g1, g2, alternative='two-sided')
                elif not is_var_equal: t_name, stat, p_val = "t-Studenta (Welch)", *stats.ttest_ind(g1, g2, equal_var=False)
                else: t_name, stat, p_val = "t-Studenta", *stats.ttest_ind(g1, g2, equal_var=True)
            else:
                if not all_normal or not is_var_equal: t_name, stat, p_val = "Kruskala-Wallisa", *stats.kruskal(*groups)
                else: t_name, stat, p_val = "ANOVA", *stats.f_oneway(*groups)

            p_adj = min(1.0, p_val * k_tests) if apply_bonferroni else p_val
            batch_results.append({"Zmienna Zależna": dv, "Zmienna Grupująca": iv, "Wybrany Test": t_name, "Wartość p (surowa)": round(p_val, 4), "Skorygowane p (Bonferroni)": round(p_adj, 4), "Wniosek": "Istotne" if p_adj < 0.05 else "Brak istotności"})
        return batch_results

    def compare_repeated_measures(self, vars_list: list, apply_bonferroni: bool = True):
        pairs = list(itertools.combinations(vars_list, 2))
        k_tests = len(pairs)
        batch_results = []
        for pre_var, post_var in pairs:
            if pre_var not in self.df.columns or post_var not in self.df.columns: continue
            data = self.df[[pre_var, post_var]].dropna()
            g1, g2 = data[pre_var].values, data[post_var].values
            if len(g1) < 2: continue
            if self._check_normality(g2 - g1)[0]: t_name, stat, p_val = "t-Zależne", *stats.ttest_rel(g1, g2)
            else: t_name, stat, p_val = "Wilcoxon", *stats.wilcoxon(g1, g2)

            p_adj = min(1.0, p_val * k_tests) if apply_bonferroni else p_val
            batch_results.append({"Zmienna 1": pre_var, "Zmienna 2": post_var, "Wybrany Test": t_name, "Wartość p (surowa)": round(p_val, 4), "Skorygowane p (Bonferroni)": round(p_adj, 4), "Wniosek": "Istotne" if p_adj < 0.05 else "Brak"})
        return batch_results

    def correlation_matrix(self, vars_list: list, alternative: str = 'two-sided', apply_bonferroni: bool = True):
        pairs = list(itertools.combinations(vars_list, 2))
        k_tests = len(pairs)
        batch_results = []
        for v1, v2 in pairs:
            data = self.df[[v1, v2]].dropna()
            if len(data) < 2: continue
            arr1, arr2 = data.values.T
            try:
                if self._check_normality(arr1)[0] and self._check_normality(arr2)[0]: t_name, stat, p_val = "Pearson", *stats.pearsonr(arr1, arr2, alternative=alternative)
                else: t_name, stat, p_val = "Spearman", *stats.spearmanr(arr1, arr2, alternative=alternative)
            except TypeError:
                t_name, stat, p_val = ("Pearson", *stats.pearsonr(arr1, arr2)) if (self._check_normality(arr1)[0] and self._check_normality(arr2)[0]) else ("Spearman", *stats.spearmanr(arr1, arr2))
                if alternative != 'two-sided': p_val /= 2

            p_adj = min(1.0, p_val * k_tests) if apply_bonferroni else p_val
            batch_results.append({"Zmienna 1": v1, "Zmienna 2": v2, "Wybrany Test": t_name, "r": round(stat, 3), "Skorygowane p": round(p_adj, 4), "Wniosek": "Istotne" if p_adj < 0.05 else "Brak"})
        return batch_results

    def calculate_t2b_b2b(self, col: str, min_v: float, max_v: float):
        data = pd.to_numeric(self.df[col], errors='coerce').dropna()
        if len(data) == 0: return [{"Błąd": "Brak danych"}]
        t = len(data)
        return [{"Zmienna": col, "T2B": f"{len(data[data >= max_v - 1])/t*100:.1f}%", "B2B": f"{len(data[data <= min_v + 1])/t*100:.1f}%", "Wybrany Test": "T2B/B2B"}]

    def calculate_nps(self, col: str):
        data = pd.to_numeric(self.df[col], errors='coerce').dropna()
        data = data[(data >= 0) & (data <= 10)]
        if len(data) == 0: return [{"Błąd": "Brak danych 0-10"}]
        nps = (len(data[data >= 9])/len(data))*100 - (len(data[data <= 6])/len(data))*100
        return [{"Zmienna": col, "NPS": round(nps, 1), "Wybrany Test": "NPS"}]

    def create_index(self, cols: list, idx_name: str):
        data = self.df[cols].apply(pd.to_numeric, errors='coerce').dropna()
        k = len(cols)
        if len(data) == 0 or k < 2: return [{"Błąd": "Brak danych"}]
        var_sum, total_var = data.var(axis=0, ddof=1).sum(), data.sum(axis=1).var(ddof=1)
        alpha = (k / (k - 1)) * (1 - (var_sum / total_var)) if total_var > 0 else 0
        self.df[idx_name] = data.mean(axis=1)
        return [{"Utworzony Indeks": idx_name, "Składowe": ", ".join(cols), "Alfa Cronbacha": round(alpha, 3)}]

    def compare_waves(self, vars_list: list, wave_col: str, w1, w2, metric: str, max_v=None):
        results = []
        d1 = self.df[self.df[wave_col].astype(str) == str(w1)]
        d2 = self.df[self.df[wave_col].astype(str) == str(w2)]
        
        for var in vars_list:
            if var not in d1.columns or var not in d2.columns: continue
            
            v1_data = pd.to_numeric(d1[var], errors='coerce').dropna()
            v2_data = pd.to_numeric(d2[var], errors='coerce').dropna()
            if len(v1_data) == 0 or len(v2_data) == 0: continue
            
            if metric == 'mean':
                val1, val2 = v1_data.mean(), v2_data.mean()
                stat, p_val = stats.ttest_ind(v1_data, v2_data, equal_var=False)
                metric_name = "Średnia"
            elif metric == 'nps':
                v1_data, v2_data = v1_data[(v1_data>=0)&(v1_data<=10)], v2_data[(v2_data>=0)&(v2_data<=10)]
                val1 = (len(v1_data[v1_data>=9])/len(v1_data)*100) - (len(v1_data[v1_data<=6])/len(v1_data)*100)
                val2 = (len(v2_data[v2_data>=9])/len(v2_data)*100) - (len(v2_data[v2_data<=6])/len(v2_data)*100)
                # T-test na zrekodowanych wartościach jako substytut z-testu dla proporcji
                r1 = v1_data.apply(lambda x: 100 if x>=9 else (-100 if x<=6 else 0))
                r2 = v2_data.apply(lambda x: 100 if x>=9 else (-100 if x<=6 else 0))
                stat, p_val = stats.ttest_ind(r1, r2, equal_var=False)
                metric_name = "NPS"
            elif metric == 't2b' and max_v is not None:
                val1 = len(v1_data[v1_data>=max_v-1])/len(v1_data)*100
                val2 = len(v2_data[v2_data>=max_v-1])/len(v2_data)*100
                r1 = v1_data.apply(lambda x: 100 if x>=max_v-1 else 0)
                r2 = v2_data.apply(lambda x: 100 if x>=max_v-1 else 0)
                stat, p_val = stats.ttest_ind(r1, r2, equal_var=False)
                metric_name = "T2B (%)"
                
            results.append({
                "Zmienna Zależna": var, "Wskaźnik": metric_name,
                f"Fala {w1}": round(val1, 2), f"Fala {w2}": round(val2, 2),
                "Różnica": round(val2 - val1, 2),
                "Wartość p": round(p_val, 4), "Wniosek": "Istotny spadek/wzrost" if p_val < 0.05 else "Różnica nieistotna"
            })
        return results