from playwright.sync_api import sync_playwright
import pandas as pd
import os
import time

# ========== CONFIG ================
BASE_URL = "https://agmarknet.gov.in/SearchCmmMkt.aspx"
DOWNLOAD_DIR = "downloads_agmark"
FAILED_CSV = "failed_downloads.csv"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ======== READ INPUT FILES =========
commodities = pd.read_csv("commodities.csv")   # CommodityName,CommodityCode
dates = pd.read_csv("dates.csv")               # FromDate,ToDate

failed_rows = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    for _, c_row in commodities.iterrows():
        commodity_name = c_row["CommodityName"]
        commodity_code = str(c_row["CommodityCode"])

        for _, d_row in dates.iterrows():
            from_date = d_row["FromDate"]
            to_date = d_row["ToDate"]

            print(f"\n🌐 Processing {commodity_name} | {from_date} → {to_date}")

            # Build URL
            url = (
                f"{BASE_URL}?Tx_Commodity={commodity_code}"
                f"&Tx_State=0&Tx_District=0&Tx_Market=0"
                f"&DateFrom={from_date}&DateTo={to_date}"
                f"&Fr_Date={from_date}&To_Date={to_date}"
                f"&Tx_Trend=2"
                f"&Tx_CommodityHead={commodity_name}"
                f"&Tx_StateHead=--Select--&Tx_DistrictHead=--Select--&Tx_MarketHead=--Select--"
            )

            try:
                page.goto(url, timeout=240000)

                # Wait until Excel button appears
                page.wait_for_selector("#cphBody_ButtonExcel", timeout=240000)

                # Download Excel
                print("📥 Clicking 'Export To Excel'...")
                with page.expect_download(timeout=240000) as download_info:
                    page.click("#cphBody_ButtonExcel", timeout=240000)

                download = download_info.value
                filename = f"{commodity_name}_{from_date}_to_{to_date}.xls"
                save_path = os.path.join(DOWNLOAD_DIR, filename)
                download.save_as(save_path)

                print(f"✅ Downloaded: {filename}")

                # Small delay between downloads
                time.sleep(3)

            except Exception as e:
                print(f"❌ Failed: {commodity_name} ({from_date} → {to_date}) | {e}")
                failed_rows.append({
                    "CommodityName": commodity_name,
                    "CommodityCode": commodity_code,
                    "FromDate": from_date,
                    "ToDate": to_date,
                    "Error": str(e)
                })
                continue

    # Save failed downloads
    if failed_rows:
        pd.DataFrame(failed_rows).to_csv(FAILED_CSV, index=False)
        print(f"\n⚠️ Some downloads failed. Logged in {FAILED_CSV}")

    browser.close()

print("\n🎯 All done.")
