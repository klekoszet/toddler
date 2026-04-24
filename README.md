# [EN] Toddler - Integrated Analytical System (v2.2)

## 1. Project Goal
An end-to-end desktop GUI application designed to automate the entire data processing workflow for quantitative research. Toddler seamlessly combines Data Cleaning (QC), Iterative Proportional Fitting (IPF Weighting), and Statistical Analysis into one cohesive tool. It works directly with SPSS (`.sav`) and CSV files, outputting ready-to-use analytical reports and SPSS Syntax.

## 2. Vibe Coding & Development Approach
This comprehensive system is the culmination of the "vibe coding" methodology. While AI handled the heavy lifting of generating the Tkinter graphical interface and pandas data manipulation boilerplate, I maintained strict control as the domain architect. I designed the statistical logic, defined the parameters for data exclusion, orchestrated the Raking algorithm limits, and mapped the export syntax. This project demonstrates how researchers can orchestrate AI models to build highly specialized, professional-grade analytical tools without writing every line of UI code manually.

## 3. Key Features
- **Tabbed Graphical Interface (GUI):** A fully visual workspace replacing the old CLI. Features scrollable checkbox panels for easy handling of massive datasets with hundreds of variables.
- **Customizable Data Prep (QC):** Dynamic thresholds for data cleaning. Users can manually set allowed missing data percentages, minimum variance for straight-liners, custom seconds for speeders, and max lengths for long-strings.
- **Inline Weighting Editor:** An integrated IPF module that dynamically generates input fields for weighting targets based on the selected variables' unique categories. Automatically recodes continuous variables (e.g., exact age) into brackets based on user-defined ranges before weighting.
- **Advanced Stat Engine:** Executes difference tests (ANOVA, t-tests), correlations, business metrics (NPS, T2B/B2B), creates indices with Cronbach's Alpha, and runs wave-to-wave tracking analyses.
- **Smart Exporters:** Generates ready-to-run SPSS Syntax (`.sps`), detailed Excel tables (`.xlsx`), and automated PowerPoint presentations (`.pptx`) based strictly on the queued analyses.
- **Smart Test Selection:** The engine automatically verifies underlying statistical assumptions (normality via Shapiro-Wilk/K-S tests, and variance homogeneity via Levene's test). If assumptions are violated, the system dynamically falls back to the appropriate non-parametric alternatives (e.g., Mann-Whitney U, Kruskal-Wallis, Wilcoxon, Spearman's rho) or applies Welch's correction.
- 
## 4. Security & Data Protection
**Zero-Cloud Architecture.** All processing—from Mahalanobis distance calculations to Raking—is executed 100% locally on the machine's RAM. No respondent data, metadata, or analytical structures are sent to external APIs or LLMs. This guarantees total compliance with GDPR, NDA agreements, and academic data ethics.

## 5. Performance & Limitations
- **Memory Bound:** The tool relies on loading the full `.sav` file into RAM via `pandas`. It is incredibly fast for typical market/academic research but may hit hardware limits on exceptionally massive, multi-gigabyte datasets.
- **Format Constraints:** Exports currently target standard MS Office formats and IBM SPSS.

## 6. Future Roadmap
As an actively developed system, upcoming features include:
- **Wave-Specific Filtering:** Allowing the Stat Engine to compute specific metrics (like a single NPS score) strictly for one defined survey wave without manual dataset splitting.
- **Scale Reversal Algorithms:** Automatic detection of scale directionality to automatically reverse negative items before calculating indices.
- **Multi-Response Support:** Expanding the engine to natively cross-tabulate and analyze multiple-choice (dichotomous sets) questions.

## 🛠️ Requirements & Execution
- Python 3.10+
- Libraries: `pip install pandas numpy pyreadstat scipy openpyxl python-pptx`
- Run: `python main.py`

---

# [PL] Toddler - Zintegrowany System Analityczny (v2.2)

## 1. Cel projektu
Kompleksowa aplikacja desktopowa (GUI) stworzona do automatyzacji całego procesu Data Processing w badaniach ilościowych. Toddler łączy w jednym oknie moduły do czyszczenia danych (QC), ważenia prób (Raking/IPF) oraz silnik statystyczny. Pracuje na plikach SPSS (`.sav`) i CSV, generując zautomatyzowane raporty oraz gotowy kod Syntax.

## 2. Podejście do tworzenia (Vibe Coding)
System jest rezultatem zastosowania metodologii "vibe codingu". Zamiast tracić czas na ręczne kodowanie zakładek i przycisków w bibliotece Tkinter, wykorzystałem AI do zbudowania architektury interfejsu. Moją rolą było zarządzanie wiedzą domenową: zaprojektowanie reguł statystycznych, określenie metodologii odrzucania braków danych, zdefiniowanie logiki ważenia oraz integracja testów istotności (np. poprawka Bonferroniego). Projekt dowodzi, że ekspert badawczy może za pomocą AI tworzyć potężne, dedykowane oprogramowanie analityczne.

## 3. Kluczowe Funkcje
- **Graficzny Interfejs (GUI):** Nowoczesne okno z zakładkami, które całkowicie zastąpiło starą konsolę (CLI). Wykorzystuje przewijane panele z checkboxami ułatwiające pracę z bazami liczącymi setki zmiennych.
- **Elastyczne Progi Czyszczenia:** Możliwość swobodnego wpisywania limitów bezpośrednio w aplikacji (np. dozwolony procent braków danych, dokładny próg wariancji, sztywny limit sekund dla speederów).
- **Wbudowany Edytor Wag (IPF):** Narzędzie samodzielnie sczytuje kategorie ze wskazanych zmiennych i generuje pola do wpisania proporcji docelowych. Umożliwia automatyczne zrekodowanie zmiennych ciągłych (np. wieku) na wpisane przedziały z poziomu interfejsu.
- **Silnik Statystyczny:** Realizuje m.in. testy różnic, korelacje, wskaźniki NPS i T2B, tworzenie indeksów z Alfą Cronbacha oraz analizę trackingową między falami. Wylicza wszystkie zlecane zadania w jednym przebiegu.
- **Inteligentny Eksport:** Zapisuje wynikową bazę `.sav`, generuje kod `.sps` dla SPSS-a, a na podstawie zleconych analiz tworzy raporty w formatach `.xlsx` oraz `.pptx`.
- **Inteligentny Dobór Testów:** Silnik automatycznie weryfikuje założenia statystyczne (normalność rozkładu za pomocą testu Shapiro-Wilka/Kołmogorowa-Smirnowa oraz jednorodność wariancji testem Levene'a). W przypadku niespełnienia założeń, system samodzielnie przełącza się na odpowiednie alternatywy nieparametryczne (np. test Manna-Whitneya, Kruskala-Wallisa, Wilcoxona, rho Spearmana) lub stosuje poprawkę Welcha.

## 4. Bezpieczeństwo i ochrona danych
**Pełna izolacja (Zero-Cloud).** Cały proces analityczny odbywa się w 100% na lokalnym komputerze użytkownika. Żadne surowe bazy danych czy struktury prób badawczych nie są wysyłane do zewnętrznych chmur ani modeli AI. Zapewnia to maksymalne bezpieczeństwo i zgodność z obostrzeniami RODO oraz tajemnicą biznesową (NDA).

## 5. Wydajność i ograniczenia
- **Zależność od RAM:** Aplikacja przechowuje przetwarzaną bazę w pamięci operacyjnej komputera. Działa optymalnie i błyskawicznie dla standardowych prób ankietowych, lecz przy olbrzymich plikach (dziesiątki milionów komórek) może obciążyć słabsze maszyny.

## 6. Perspektywy rozwoju
Toddler ma otwartą, modułową architekturę. Najbliższe plany rozwoju to m.in.:
- **Filtrowanie wewnątrz silnika:** Pozwoli na zlecanie obliczeń (np. NPS) wyłącznie dla wybranej grupy czy fali, bez konieczności uprzedniego dzielenia pliku.
- **Automatyczne odwracanie skal:** Wdrożenie algorytmu detekcji kierunku pytań w bateriach w celu bezbłędnego budowania indeksów.
- **Obsługa pytań wielokrotnego wyboru (Multi-Response):** Rozbudowa parsera statystycznego o natywną obsługę zestawów dychotomicznych.

## 🛠️ Wymagania i Uruchomienie
- Python 3.10+
- Biblioteki: `pip install pandas numpy pyreadstat scipy openpyxl python-pptx`
- Uruchomienie: `python main.py`
