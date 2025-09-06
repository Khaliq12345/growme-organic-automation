from playwright.sync_api import sync_playwright
import os
import time
import subprocess
from src.config import config


TIMEOUT = 120000


# Download the output
def download_file(file_url, save_path, filename="download.xlsx"):
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
def run(headless: bool, domain_lst) -> str | None:
    with sync_playwright() as p:
        try:
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
            download_file(file_url, "./outputs", f"{list_name}.xlsx")
            # Delete Job
            delete_icon_selector = f"{tr_selector} i.triggerDeleteDocumentApp"
            page.click(delete_icon_selector)
            page.wait_for_selector("div.jconfirm", timeout=TIMEOUT)
            page.click('div.jconfirm button.c-btn--success:has-text("OK")')
            #
            print("Process ended !!!")
            # page.pause()
            browser.close()
            return list_name
        except Exception as e:
            print(f"Processing Error {e}")
            return None


if __name__ == "__main__":
    run(False, ["agola.com", "ikilo.fr", "dorsal.bj"])
