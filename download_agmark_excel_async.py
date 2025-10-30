import asyncio
import os
import pandas as pd
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "https://agmarknet.gov.in/SearchCmmMkt.aspx"
DOWNLOAD_DIR = Path("downloads_agmark")
FAILED_CSV = "failed_downloads.csv"
CONCURRENCY = 5  # ← run 5 at a time

DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def fetch_one(play, browser, row, semaphore):
    """
    One unit of work: open page, go to url, click download, save.
    `row` is a dict with keys: CommodityName, CommodityCode, FromDate, ToDate
    """
    async with semaphore:
        commodity_name = row["CommodityName"]
        commodity_code = str(row["CommodityCode"])
        from_date = row["FromDate"]
        to_date = row["ToDate"]

        print(f"\n🌐 Processing {commodity_name} | {from_date} → {to_date}")

        # build url
        url = (
            f"{BASE_URL}?Tx_Commodity={commodity_code}"
            f"&Tx_State=0&Tx_District=0&Tx_Market=0"
            f"&DateFrom={from_date}&DateTo={to_date}"
            f"&Fr_Date={from_date}&To_Date={to_date}"
            f"&Tx_Trend=2"
            f"&Tx_CommodityHead={commodity_name}"
            f"&Tx_StateHead=--Select--&Tx_DistrictHead=--Select--&Tx_MarketHead=--Select--"
        )

        # one isolated context per job
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        try:
            await page.goto(url, timeout=240_000)
            await page.wait_for_selector("#cphBody_ButtonExcel", timeout=240_000)

            print("📥 Clicking 'Export To Excel'...")
            async with page.expect_download(timeout=240_000) as download_info:
                await page.click("#cphBody_ButtonExcel", timeout=240_000)

            download = await download_info.value
            filename = f"{commodity_name}_{from_date}_to_{to_date}.xls"
            save_path = DOWNLOAD_DIR / filename
            await download.save_as(str(save_path))
            print(f"✅ Downloaded: {filename}")

        except Exception as e:
            print(f"❌ Failed: {commodity_name} ({from_date} → {to_date}) | {e}")
            return {
                "CommodityName": commodity_name,
                "CommodityCode": commodity_code,
                "FromDate": from_date,
                "ToDate": to_date,
                "Error": str(e),
            }
        finally:
            await context.close()

        return None  # success


async def main():
    # ======== READ INPUT FILES =========
    commodities = pd.read_csv("commodities.csv")  # CommodityName,CommodityCode
    dates = pd.read_csv("dates.csv")              # FromDate,ToDate

    # build all work upfront
    jobs = []
    for _, c_row in commodities.iterrows():
        for _, d_row in dates.iterrows():
            jobs.append(
                {
                    "CommodityName": c_row["CommodityName"],
                    "CommodityCode": c_row["CommodityCode"],
                    "FromDate": d_row["FromDate"],
                    "ToDate": d_row["ToDate"],
                }
            )

    failed_rows = []
    semaphore = asyncio.Semaphore(CONCURRENCY)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        tasks = [
            fetch_one(p, browser, job, semaphore)
            for job in jobs
        ]

        # run them all, 5 at a time because of the semaphore
        results = await asyncio.gather(*tasks)

        # collect failures
        for r in results:
            if r is not None:
                failed_rows.append(r)

        await browser.close()

    if failed_rows:
        pd.DataFrame(failed_rows).to_csv(FAILED_CSV, index=False)
        print(f"\n⚠️ Some downloads failed. Logged in {FAILED_CSV}")

    print("\n🎯 All done.")


if __name__ == "__main__":
    asyncio.run(main())
