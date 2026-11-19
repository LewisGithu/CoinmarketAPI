# 🪙 CoinMarketCap Automated API Data Pull & Transformation

### 📌 Project Overview
An automated Python pipeline that pulls live cryptocurrency market data via the CoinMarketCap API, flattens the JSON response into a structured Pandas DataFrame, and applies automated data normalization for trend analysis.

### 🛠️ Tech Stack
* **Language:** Python 3.10+
* **Libraries:** `requests`, `pandas`, `seaborn`, `matplotlib`, `json`, `time`
* **API:** CoinMarketCap Pro/Sandbox API

### 🔄 What I Did
1. **API Integration:** Built a `Request` loop with error handling and header authorization (`X-CMC_PRO_API_KEY`).
2. **JSON Flattening:** Parsed nested dictionary/list responses using `json_normalize`.
3. **Automated Runner:** Implemented a timestamped execution loop to append live data snapshots at regular intervals.
4. **Exploratory Data Analysis:** Visualized percentage change distributions (`percent_change_1h` vs `24h`) using Seaborn.

### 🚀 How to Run Locally
1. Clone the repo:
   ```bash
   git clone https://github.com/LewisGithu/CoinmarketAPI
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your environment variable:
   ```bash
   export CMC_API_KEY="your_actual_api_key_here"
   ```
4. Run the script:
   ```bash
   python coinmarketcap_script.py
   ```
