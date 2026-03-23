from playwright.sync_api import sync_playwright
import time
import openpyxl

def main():
    log_file = open("registrazione.txt", "w", encoding="utf-8")

    def log(message):
        print(message)
        log_file.write(message + "\n")

    with sync_playwright() as p:
        # Argomenti semplificati per Chromium
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        context = browser.new_context(record_har_path='registrazione.har')
        page = context.new_page()

        # Gestisci nuove pagine
        def handle_new_page(new_page):
            log(f"Nuova pagina aperta: {new_page.url}")
            new_page.on("request", log_request)
            new_page.on("response", log_response)

        # Monitora tutte le richieste di rete
        def log_request(request):
            log(f"Richiesta: {request.method} {request.url} -> {request.resource_type}")

        def log_response(response):
            log(f"Risposta: {response.status} {response.url}")

        page.on("request", log_request)
        page.on("response", log_response)

        browser.on("page", handle_new_page)

        # Gestisci popup
        def handle_popup(popup):
            log(f"Popup aperto: {popup.url}")
            if '/view/file/' in popup.url:
                log(f"Popup PDF: {popup.url}")
                popup.wait_for_load_state('networkidle')
                # Scarica
                response = page.request.get(popup.url)
                if response.status == 200:
                    file_name = popup.url.split('/')[-1]
                    with open(f"./downloads/{file_name}", "wb") as f:
                        f.write(response.body())
                    log(f"PDF scaricato: {file_name}")
            popup.on("request", log_request)
            popup.on("response", log_response)

        page.on("popup", handle_popup)

        # Gestisci download
        def handle_download(download):
            log(f"Download iniziato: {download.url} -> {download.suggested_filename}")
            try:
                import os
                os.makedirs("./downloads", exist_ok=True)
                download.save_as(f"./downloads/{download.suggested_filename}")
                log(f"Download salvato: {download.suggested_filename}")
            except Exception as e:
                log(f"Errore download: {e}")

        page.on("download", handle_download)

        try:
            log("Tentativo di caricamento pagina...")
            response = page.goto("http://172.16.90.4:8080/adiJed/ui/login/page.jsp", timeout=60000, wait_until='domcontentloaded')
            log(f"Response status: {response.status if response else 'None'}")
            log(f"URL corrente: {page.url}")
            log(f"Titolo pagina: {page.title()}")

            if page.url == "about:blank":
                log("ERRORE: Pagina ancora su about:blank. Possibili cause:")
                log("- Timeout troppo breve")
                log("- Problema di rete/firewall")
                log("- Sito richiede autenticazione")
                log("- Argomenti browser incompatibili")
                log("Prova ad aprire manualmente l'URL in un browser normale.")

            # Aspetta che la pagina sia completamente caricata
            page.wait_for_load_state('networkidle', timeout=30000)

            # Aspetta navigazione alla home page (login manuale)
            try:
                page.wait_for_url("**/home.do", timeout=60000)
                log("Navigazione alla home page completata.")
            except:
                log("Timeout attesa home page. Procedendo comunque.")

            # Verifica se siamo sulla pagina home
            if "home.do" in page.url:
                log("Siamo sulla pagina home. Facendo screenshot...")
                page.screenshot(path='screenshot.png')
                log("Screenshot salvato come screenshot.png")

                # Aspetta che la pagina sia pronta
                page.wait_for_load_state('networkidle', timeout=30000)

                # Trova elementi a con href contenente 'pdf' (case insensitive)
                all_a = page.locator('a').all()
                pdf_links = [link for link in all_a if link.get_attribute('href') and 'pdf' in link.get_attribute('href').lower()]
                if pdf_links:
                    log(f"Trovati {len(pdf_links)} elementi a con href contenente 'pdf'. Scaricando...")
                    for i, link in enumerate(pdf_links):
                        href = link.get_attribute('href')
                        if not href.startswith('http'):
                            href = 'http://172.16.90.4:8080' + href
                        try:
                            response = page.request.get(href)
                            if response.status == 200:
                                filename = href.split('/')[-1].split('?')[0]
                                with open(f"./downloads/{filename}", "wb") as f:
                                    f.write(response.body())
                                log(f"PDF {filename} scaricato.")
                            else:
                                log(f"Errore download {href}: {response.status}")
                        except Exception as e:
                            log(f"Errore nel download di {href}: {e}")
                else:
                    log("Nessun elemento a con href contenente 'pdf' trovato.")

                # Leggi l'elenco dei codici da Excel
                wb = openpyxl.load_workbook('elenco_codici_studi.xlsx')
                sheet = wb.active
                codes = [row[0] for row in sheet.iter_rows(min_row=2, values_only=True) if row[0]]
                log(f"Trovati {len(codes)} codici in elenco_codici_studi.xlsx")
                # Limita a primi 5 per test
                codes = codes[:5]
                for code in codes:
                    log(f"Elaborando codice: {code}")
                    # Cerca il codice
                    search_input = page.locator('input[placeholder*="Cerca"]')
                    search_input.fill(code)
                    page.wait_for_timeout(2000)  # Aspetta aggiornamento
                    page.screenshot(path=f'screenshot_{code}.png')
                    log(f"Screenshot per {code} salvato.")
                    # Prova a cliccare img PDF
                    pdf_imgs = page.locator('img[src*="getDocumentIcon"]').all()
                    if pdf_imgs:
                        log(f"Trovate {len(pdf_imgs)} img PDF per {code}, cliccando la prima...")
                        pdf_imgs[0].click()
                        # Aspetta popup
                        page.wait_for_timeout(2000)
                    else:
                        log(f"Nessuna img PDF per {code}")

                # Per debug, trova tutti gli elementi a con href
                all_links = page.locator('a[href]').all()
                if all_links:
                    log(f"Trovati {len(all_links)} elementi a con href.")
                    for i, link in enumerate(all_links[:10]):  # Limita a 10 per non floodare
                        href = link.get_attribute('href')
                        text = link.inner_text().strip()
                        log(f"  {i+1}: href='{href}' text='{text}'")
                else:
                    log("Nessun elemento a con href trovato.")
            else:
                log("Non siamo sulla pagina home. Login manuale richiesto.")

            log("Puoi interagire manualmente se necessario. Quando clicchi sul link PDF, vedrai tutte le richieste in console.")
            log("Premi Ctrl+C per chiudere.")

            # Monitora cambi di URL nella pagina principale
            def on_url_change(frame):
                if frame == page.main_frame:
                    log(f"Navigazione principale a: {frame.url}")

            page.on("framenavigated", on_url_change)

            # Aspetta input o interruzione
            try:
                time.sleep(30)  # Ridotto a 30 secondi per test
            except KeyboardInterrupt:
                log("Interrotto dall'utente")

        except Exception as e:
            log(f"Errore durante goto: {e}")
            log("Prova ad aprire l'URL manualmente in un browser.")

        finally:
            log("Chiudendo il browser...")
            try:
                context.close()
                browser.close()
            except Exception as e:
                log(f"Errore chiusura: {e}")
            log_file.close()

if __name__ == "__main__":
    main()