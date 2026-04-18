# toddler
ENG/PL

ENG
Toddler - Integrated Analytical System
Toddler is a professional tool designed to automate the cleaning, weighting, and statistical analysis of quantitative research data. Built for researchers working with SPSS (.sav) and CSV files, the program combines the computational power of Python with the ability to generate ready-to-use Syntax for IBM SPSS Statistics.

1. Core Features
🛠 Data Preparation (Data Prep)
Cleaning:

Removal of "speeders" (respondents with completion times below a specified threshold).

Detection of "straight-liners" (respondents showing abnormally low variance in scale questions).

Removal of "long-strings" (repetitive sequences of identical answers).

Multivariate anomaly detection using Mahalanobis Distance.

Handling of missing data (drops respondents missing >15% of scale items).

Weighting:

Advanced IPF (Iterative Proportional Fitting) Raking algorithm executed natively in Python.

Automatic trimming of extreme weights to prevent variance inflation.

Automatic recoding of continuous variables (e.g., exact age) into brackets based on target weighting structures.

📊 Statistical Engine (Stat Engine)
Difference Tests: Comparisons of independent groups (Independent t-test, Welch's t-test, Mann-Whitney U, ANOVA, Kruskal-Wallis) and repeated measures (Paired t-test, Wilcoxon).

Relationship Analysis: Correlation matrices (Pearson, Spearman) with automatic Bonferroni correction applied for multiple comparisons.

Business Metrics: Calculation of NPS (Net Promoter Score) and Top 2 Boxes / Bottom 2 Boxes (T2B / B2B).

Indices: Creation of aggregate index variables (means) alongside the automatic calculation of the Cronbach's Alpha reliability coefficient.

Tracking: Wave-to-Wave comparisons (e.g., Wave 1 vs Wave 2) evaluating shifts in Means, NPS, or T2B, complete with statistical significance testing.

📤 Results Export
SPSS Syntax (.sps): Generation of ready-to-run code to seamlessly replicate analyses within SPSS.

MS Excel (.xlsx): Detailed output tables accompanied by data cleaning logs.

MS PowerPoint (.pptx): Automated slide deck creation featuring result tables.

2. Operational Architectures (Global Modes)
The program offers three distinct workflow architectures:

Syntax Only: Acts as a rapid code generator for SPSS. It does not modify or save new data files.

Hybrid: Python handles the heavy lifting of data cleaning and weighting, exporting a clean, finalized .sav file. Statistical analyses are generated as SPSS Syntax.

Full Automation (Combine): Comprehensive end-to-end processing. Python prepares the data, executes all statistical tests internally, and exports final reports (Excel/PPTX).

3. Installation & Usage
Requirements
Python 3.10+

Required libraries: pandas, numpy, pyreadstat, scipy, openpyxl, python-pptx

Execution
Run the program via the system terminal / command prompt to ensure optimal memory stability:

Bash
python main.py
4. Roadmap & Future Enhancements (To-Do)
Despite its high stability, the system is continuously evolving. Planned upgrades include:

Wave-Specific Calculations: Implementing the ability to filter and calculate specific metrics (like NPS or T2B) for a single, specific wave without needing to split the database.

Automatic Scale Detection: Algorithms to identify scale directionality (positive vs. negative) to automatically reverse items prior to index creation.

Multi-Response Handling: Expanding the statistical engine to process and analyze multiple-choice questions (dichotomous sets).

GUI (Graphical User Interface): Transitioning from a Command Line Interface (CLI) to a fully dedicated desktop application window.

Advanced Trimming Configuration: Adding the ability to manually set Weight Cap/Floor thresholds directly from the configuration menu.





PL
Toddler - Zintegrowany System Analityczny
Toddler to profesjonalne narzędzie do automatyzacji procesów czyszczenia, ważenia oraz analizy statystycznej danych badawczych (ilościowych). Program został zaprojektowany z myślą o badaczach pracujących na plikach SPSS (.sav) oraz CSV, łącząc moc obliczeniową Pythona z możliwością generowania składni (Syntax) dla IBM SPSS Statistics.

1. Główne Funkcje
🛠 Przygotowanie Danych (Data Prep)
Czyszczenie (Cleaning):

Usuwanie "speedersów" (respondentów o zbyt krótkim czasie wypełniania).

Wykrywanie "straight-linerów" (osób o niskiej wariancji odpowiedzi).

Usuwanie "long-strings" (powtarzalnych ciągów tych samych wartości).

Wykrywanie anomalii wielowymiarowych (Dystans Mahalanobisa).

Obsługa braków danych (threshold 15%).

Ważenie (Weighting):

Zaawansowany algorytm IPF Raking realizowany natywnie w Pythonie.

Automatyczny trimming (przycinanie) wag ekstremalnych.

Rekodowanie zmiennych ciągłych (np. wiek) na przedziały na podstawie docelowych struktur wagowych.

📊 Silnik Statystyczny (Stat Engine)
Testy Różnic: Porównania grup niezależnych (t-Student, ANOVA, testy nieparametryczne) oraz pomiarów powtarzanych.

Analiza Związków: Macierze korelacji (Pearson, Spearman) z automatyczną korektą Bonferroniego dla testów wielokrotnych.

Wskaźniki Biznesowe: Obliczanie NPS (Net Promoter Score) oraz Top 2 Boxes / Bottom 2 Boxes.

Indeksy: Tworzenie indeksów (średnie) wraz z automatycznym wyliczaniem współczynnika rzetelności Alfa Cronbacha.

Tracking: Porównywanie fal badania (Wave 1 vs Wave 2) pod kątem zmian w średnich, NPS lub T2B wraz z testami istotności statystycznej.

📤 Eksport Wyników
SPSS Syntax (.sps): Generowanie gotowego kodu do odtworzenia analiz w SPSS.

MS Excel (.xlsx): Szczegółowe tabele wynikowe wraz z logami z procesu czyszczenia danych.

MS PowerPoint (.pptx): Automatyczne tworzenie slajdów z tabelami wyników.

2. Tryby Pracy (Global Modes)
Program oferuje trzy architektury pracy:

Tylko Syntax: Program służy jako szybki generator kodu dla SPSS. Nie modyfikuje plików danych.

Hybryda: Python wykonuje czyszczenie i ważenie, zapisując nową bazę .sav. Analizy statystyczne są generowane w formie Syntaxu.

Pełen Kombajn: Kompleksowa automatyzacja. Python przygotowuje dane, wykonuje analizy i eksportuje raporty końcowe (Excel/PPTX).

3. Instalacja i Uruchomienie
Wymagania
Python 3.10+

Biblioteki: pandas, numpy, pyreadstat, scipy, openpyxl, python-pptx

Uruchomienie
Bash
python main.py

4. Mapa Drogowa i Funkcje do Dopracowania (To-Do)
Mimo wysokiej stabilności, system jest w ciągłym rozwoju. Planowane usprawnienia obejmują:

Wave-Specific Calculations: Implementacja możliwości filtrowania i liczenia zmiennych (np. NPS lub T2B) tylko dla konkretnej fali, bez konieczności dzielenia bazy danych.

Automatyczne Wykrywanie Skal: Algorytm rozpoznający kierunek skal (pozytywne vs negatywne) w celu automatycznego odwracania wartości przed tworzeniem indeksów.

Obsługa Multi-Response: Rozbudowa silnika o analizę pytań wielokrotnego wyboru (zmienne dychotomiczne).

GUI (Graficzny Interfejs): Przejście z interfejsu konsolowego (CLI) na dedykowane okno aplikacji.

Zaawansowany Trimming: Dodanie opcji ręcznego ustawiania Cap/Floor dla wag bezpośrednio z menu konfiguracji.
