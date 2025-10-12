# Agmark Data  Exatraction Automation

This project automates the download of agricultural market data (Agmarknet) using **Playwright** and **Python**.

## Features
- Automatically opens Agmarknet URLs for multiple commodities and date ranges  
- Exports and saves Excel files automatically  
- Logs failed downloads in a separate CSV  
- Organizes downloads by commodity and date  

## Project Folder Structure
Agmark Data  Exatraction Automation/

│

├── download_agmark_excel.py

├── Commodity.csv

├── DateRange.csv

├── failed_downloads.csv

├── downloads_agmark/

│   ├── Apple_01-Jan-2018_to_31-Mar-2018.xls

│   ├── Banana_01-Jan-2018_to_31-Mar-2018.xls

│   └── ...

└── README.md


## Setup

1. **Install dependencies**
   ```bash
   pip install playwright pandas
   playwright install

2. **Run the script**
    python download_automation_full.py

3. The downloaded Excel files will appear in the downloads_agmark/ folder.

   **CSV Inputs**
- commodities.csv → Edit names and codes of commodity from available list in Agmarket detail excel file, Commodity sheet
- dates.csv → Contains FromDate and ToDate columns(Edit according to the requirement)

## Notes
- If a file fails to download, details are saved in failed_downloads.csv.
- Website occasionally returns 503 Service Unavailable; rerun the script later.

## Benefits for Stakeholders

**Farmers**  
- Access to real-time market prices helps farmers decide when and where to sell their produce for maximum profit.  
- Historical data analysis enables better planning for future crop cycles.  
- Reduced dependency on intermediaries for market information.  

**Traders and Merchants**  
- Quick access to price trends across multiple markets facilitates better trading decisions.  
- Automated alerts for significant price movements or market opportunities.  
- Comprehensive data for inventory management and procurement planning.  

**Policy Makers and Researchers**  
- Aggregated data provides insights into agricultural market dynamics.  
- Historical trends support evidence-based policy formulation.  
- Market analysis helps identify areas requiring intervention or support.

## Documentation
A detailed step-by-step procedure of this project is attached separately. Please refer to it for installation, setup, and usage instructions.-Agmarknet_Data_Automation
