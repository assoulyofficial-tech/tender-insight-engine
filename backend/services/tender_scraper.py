"""
Tender Scraper Service.
Adapted from the user's Playwright-based scraper.
"""
import asyncio
import io
from datetime import datetime, date
from typing import List, Tuple, Set, Optional
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

from config import settings
from database import supabase
from services.document_extractor import DocumentExtractor

# Configuration
HOMEPAGE_URL = "https://www.marchespublics.gov.ma/pmmp/"
TENDER_LINK_PREFIX = "https://www.marchespublics.gov.ma/index.php?page=entreprise.EntrepriseDetailConsultation&refConsultation="
CATEGORY_FILTER = "2"  # Fournitures only

FORM_DATA = {
    "nom": "Assouly",
    "prenom": "Ben Ahmed",
    "email": "test@test.com",
}

# Timeouts (ms)
TIMEOUT_PAGE_LOAD = 30000
TIMEOUT_FORM_WAIT = 15000
TIMEOUT_DOWNLOAD_WAIT = 60000


class TenderScraper:
    """Scraper for Moroccan government tenders."""

    def __init__(self):
        self.browser = None
        self.context = None
        self.running = False
        self.extractor = DocumentExtractor()

    async def run(self, target_date: date):
        """Run the scraper for a specific date."""
        self.running = True
        date_str = target_date.strftime("%d/%m/%Y")

        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=settings.SCRAPER_HEADLESS)
            self.context = await self.browser.new_context(accept_downloads=True)

            try:
                # Phase 1: Collect tender links
                tender_links = await self._collect_tender_links(date_str)
                print(f"Found {len(tender_links)} tender links for {date_str}")

                # Phase 2: Download each tender
                semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_DOWNLOADS)
                tasks = [
                    self._download_tender(url, idx, semaphore)
                    for idx, url in enumerate(tender_links, 1)
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Summary
                success_count = sum(1 for r in results if r is True)
                print(f"Downloaded: {success_count}/{len(tender_links)}")

            finally:
                await self.browser.close()
                self.running = False

    async def stop(self):
        """Stop the scraper."""
        self.running = False
        if self.browser:
            await self.browser.close()

    async def _collect_tender_links(self, date_str: str) -> List[str]:
        """Navigate and collect all tender links for the given date."""
        page = await self.context.new_page()

        try:
            await page.goto(HOMEPAGE_URL)
            await page.click("text=Consultations en cours")
            await page.select_option(
                "#ctl0_CONTENU_PAGE_AdvancedSearch_categorie",
                value=CATEGORY_FILTER,
            )

            # Set date range
            section = page.locator('text="Date de mise en ligne :"').locator("..")
            await section.locator("input").nth(0).fill(date_str)
            await section.locator("input").nth(1).fill(date_str)

            # Clear deadline date
            deadline_section = page.locator(
                'text="Date limite de remise des plis :"'
            ).locator("..")
            for i in range(2):
                input_field = deadline_section.locator("input").nth(i)
                await input_field.click()
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Delete")

            # Search
            await page.locator('input[title="Lancer la recherche"]').nth(0).click()
            await page.wait_for_load_state("networkidle")
            await page.select_option(
                "#ctl0_CONTENU_PAGE_resultSearch_listePageSizeTop",
                value="500",
            )
            await page.wait_for_selector(
                "a[href*='EntrepriseDetailConsultation']",
                timeout=20000,
            )

            # Extract links
            all_links = await page.eval_on_selector_all("a", "els => els.map(el => el.href)")
            tender_links = list(
                set(
                    link
                    for link in all_links
                    if link and link.startswith(TENDER_LINK_PREFIX)
                )
            )

            return tender_links

        finally:
            await page.close()

    async def _download_tender(
        self, tender_url: str, idx: int, semaphore: asyncio.Semaphore
    ) -> bool:
        """Download a single tender and process its files."""
        async with semaphore:
            page = None
            try:
                page = await self.context.new_page()
                await page.goto(tender_url, timeout=TIMEOUT_PAGE_LOAD)

                # Click download button
                await page.click(
                    'a[id="ctl0_CONTENU_PAGE_linkDownloadDce"]',
                    timeout=TIMEOUT_FORM_WAIT,
                )
                await page.wait_for_selector(
                    "#ctl0_CONTENU_PAGE_EntrepriseFormulaireDemande_nom",
                    timeout=TIMEOUT_FORM_WAIT,
                )

                # Fill form
                await page.check(
                    "#ctl0_CONTENU_PAGE_EntrepriseFormulaireDemande_accepterConditions"
                )
                await page.fill(
                    "#ctl0_CONTENU_PAGE_EntrepriseFormulaireDemande_nom",
                    FORM_DATA["nom"],
                )
                await page.fill(
                    "#ctl0_CONTENU_PAGE_EntrepriseFormulaireDemande_prenom",
                    FORM_DATA["prenom"],
                )
                await page.fill(
                    "#ctl0_CONTENU_PAGE_EntrepriseFormulaireDemande_email",
                    FORM_DATA["email"],
                )
                await page.click("#ctl0_CONTENU_PAGE_validateButton")
                await page.wait_for_selector(
                    "#ctl0_CONTENU_PAGE_EntrepriseDownloadDce_completeDownload",
                    timeout=TIMEOUT_FORM_WAIT,
                )

                # Download to memory
                async with page.expect_download(timeout=TIMEOUT_DOWNLOAD_WAIT) as download_info:
                    await page.click(
                        "#ctl0_CONTENU_PAGE_EntrepriseDownloadDce_completeDownload"
                    )

                download = await download_info.value
                
                # Read file into memory (no disk writes!)
                file_path = await download.path()
                with open(file_path, "rb") as f:
                    file_bytes = io.BytesIO(f.read())

                # Extract deadline from page
                deadline = await self._extract_deadline(page)

                # Store in database
                await self._store_tender(
                    tender_url,
                    download.suggested_filename,
                    file_bytes,
                    deadline,
                )

                print(f"✓ Tender #{idx} downloaded and processed")
                return True

            except PlaywrightTimeout as e:
                print(f"✗ Tender #{idx} timeout: {e}")
                return False
            except Exception as e:
                print(f"✗ Tender #{idx} error: {e}")
                return False
            finally:
                if page:
                    await page.close()

    async def _extract_deadline(self, page) -> Optional[dict]:
        """Extract deadline from tender page."""
        try:
            deadline_text = await page.locator(
                'text="Date et heure limite de remise des plis"'
            ).locator("..").locator("span").inner_text()
            
            # Parse: DD/MM/YYYY HH:MM
            parts = deadline_text.strip().split()
            if len(parts) >= 2:
                return {
                    "date": parts[0],
                    "time": parts[1] if len(parts) > 1 else None,
                }
        except:
            pass
        return None

    async def _store_tender(
        self,
        url: str,
        filename: str,
        file_bytes: io.BytesIO,
        deadline: Optional[dict],
    ):
        """Store tender in database and trigger extraction."""
        tender_data = {
            "reference_url": url,
            "scrape_date": date.today().isoformat(),
            "status": "SCRAPED",
        }

        if deadline:
            # Parse deadline
            try:
                dl_date = datetime.strptime(deadline["date"], "%d/%m/%Y").date()
                tender_data["submission_deadline_date"] = dl_date.isoformat()
                tender_data["deadline_source"] = "WEBSITE"
                if deadline.get("time"):
                    tender_data["submission_deadline_time"] = deadline["time"]
            except:
                pass

        # Insert into database
        if supabase:
            result = await supabase.insert("tenders", tender_data)
            tender_id = result[0]["id"]

            # Extract documents (memory-only)
            await self.extractor.extract_and_store(
                tender_id, filename, file_bytes
            )
        else:
            print("Warning: No database connection. Tender not stored.")
