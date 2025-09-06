import sys

sys.path.append(".")
from playwright.sync_api import sync_playwright
import os
import time
import subprocess
from src.config import config
import pandas as pd

PROCESS_NAME = "Company_domains_gte1"
TIMEOUT = 120000
INPUT_FILE_NAME = f"./inputs/{PROCESS_NAME}.csv"

# Check for status file to continue progress
STATUS_FILE = "status.txt"
STATUS_FILE_EXIST = os.path.exists(STATUS_FILE)
STATUS_NUMBER = 0
if STATUS_FILE_EXIST:
    with open(STATUS_FILE, "r") as f:
        STATUS_NUMBER = int(f.read())

# Read the input data
DATAFRAME = pd.read_csv(INPUT_FILE_NAME, header=None)
print(DATAFRAME.shape)


# Download the output
def download_file(
    file_url,
    save_path,
    batch_number: int,
):
    filename = f"Batch_{batch_number}_of_{PROCESS_NAME}.xlsx"
    os.makedirs(save_path, exist_ok=True)
    file_path = os.path.join(save_path, filename)
    cmd = [
        "curl",
        "-L",
        "-o",
        file_path,
        file_url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Erreur lors du téléchargement : {result.stderr}")
    else:
        print(f"Fichier téléchargé dans : {file_path}")


# Run Scraping Browser
def start_downloading(
    headless: bool, domain_lst: list[str], batch_number: int
) -> str | None:
    with sync_playwright() as p:
        main_url = "https://apps.growmeorganic.com/login"
        after_login_url = (
            "https://apps.growmeorganic.com/dashboard/enrich/features/home"
        )
        browser = p.firefox.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        page.goto(main_url, timeout=TIMEOUT)
        page.wait_for_load_state("load", timeout=TIMEOUT)
        # Login
        page.fill("input#emaill", config.LOGIN_EMAIL)
        page.fill("input#passwordl", config.LOGIN_PASSWORD)
        page.click("button#send_login_f")
        # Form Processing
        page.goto(after_login_url, timeout=TIMEOUT)
        page.wait_for_load_state("load", timeout=TIMEOUT)
        page.fill("textarea#listData", "\n".join(domain_lst))
        timestamp = int(time.time())
        list_name = f"list_{timestamp}"
        page.fill("input#listName", list_name)
        page.select_option("#listQueryType", "normal")
        page.click("button:has-text('Upload my list')")
        # Retrieve Result
        tr_selector = f'tr[data-filter-view-content="{list_name}"]'
        page.wait_for_selector(tr_selector, timeout=TIMEOUT)
        download_button_selector = f"{tr_selector} div.wrapperDropDown.wrapperDropDownSmall.blockDownloadUserRight button"
        page.wait_for_selector(download_button_selector, timeout=TIMEOUT * 3)
        page.click(download_button_selector)
        link_selector = f'{tr_selector} a:has-text("Download in XLSX (.xlsx)")'
        file_url = page.get_attribute(link_selector, "href")
        # print(f"Got Download link {file_url}")
        download_file(file_url, "./outputs", batch_number)
        # Delete Job
        delete_icon_selector = f"{tr_selector} i.triggerDeleteDocumentApp"
        page.click(delete_icon_selector)
        page.wait_for_selector("div.jconfirm", timeout=TIMEOUT)
        page.click('div.jconfirm button.c-btn--success:has-text("OK")')
        # Logout
        page.goto("https://apps.growmeorganic.com/logout/", timeout=TIMEOUT)
        #
        print("Process ended !!!")
        # page.pause()
        browser.close()
        return list_name


def main():
    # split the dataframe into batches of 1000s
    chunks = [
        DATAFRAME.iloc[i : i + 1000] for i in range(0, len(DATAFRAME), 1000)
    ]
    for batch_number, chunk in enumerate(chunks):
        if batch_number <= STATUS_NUMBER:
            continue
        print(batch_number, chunk.shape)
        try:
            start_downloading(False, chunk[0].to_list(), batch_number)

            # update the status file
            with open(STATUS_FILE, "w") as f:
                f.write(str(batch_number))
        except Exception as e:
            print(f"Error while processing -- {e}")


if __name__ == "__main__":
    # run(False, ["agola.com", "ikilo.fr", "dorsal.bj"])
    main()
