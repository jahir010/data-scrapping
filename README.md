# Data Scrapping Repository

A Python-based project for scraping and organizing URLs related to various academic disciplines and sub-disciplines. Each CSV file in this repository contains a list of URLs tailored to a specific discipline and sub-discipline combination.

## Repository Structure

```
/ (root)
├── *.csv                 # URL lists organized by discipline and sub-discipline
├── programme_details.py  # Module for handling programme details parsing and storage
├── main.py               # Entry point for running the scraping and processing pipeline
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## CSV Naming Convention

Every CSV file **must** follow the naming pattern:

```
<Discipline>_<sub-discipline>_urls.csv
```

* **Discipline**: A broad field of study (e.g., `Business&Management`).
* **sub-discipline**: A more focused area within the discipline (e.g., `public-administration`).
* The suffix `_urls.csv` indicates the file contains only URL entries.

**Example**:

```
Business&Management_public-administration_urls.csv
```

This file represents:

* Discipline: `Business&Management`
* Sub-discipline: `public-administration`

> **Note:** Whenever you add or rename a CSV, update both the `Discipline` and `sub-discipline` in the filename to match the new content.

## Getting Started

1. **Clone the repository**

   ```bash
   git clone https://github.com/jahir010/data-scrapping.git
   cd data-scrapping
   ```

2. **Install Dependencies**

   Use [pip](https://pip.pypa.io/) and the provided `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set variables in main.py:**

   * Update the CSV filename, discipline, and sub‑discipline each time before running main.py.

4. **Run the Script:**

   ```bash
   python main.py 
   ```

## License

This project is licensed under the MIT License. See `LICENSE` for details.
