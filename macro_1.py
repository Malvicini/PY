import pyautogui
import time
import sys

# Prompt for placeholder values
VAR1 = input('Enter value for VAR1: ')

POS1 = (2016, 219)
POS2 = (1310, 213)
POS3 = (552, 161)
POS4 = (1400, 199)
POS5 = (1360, 205)
POS6 = (428, 248)
POS7 = (2428, 93)
#POS8 = (73, 199)
POS9 = (772, 565)
POS10 = (504, 20)
POS11 = (74, 165)

time.sleep(1)  # short delay before starting

# saved position POS1 = (2016, 219)
pyautogui.click(2016, 219)
time.sleep(0.5)
pyautogui.click(1971, 221)
time.sleep(0.5)
# saved position POS2 = (1310, 213)
pyautogui.click(1310, 213)
time.sleep(0.5)
# placeholder VAR1 - type where needed
pyautogui.typewrite(str(VAR1))
time.sleep(1.5)
# Check for ricerca_blu.png (552, 161) ricerca_blu.png
x, y = pyautogui.locateCenterOnScreen('ricerca_blu.png')
print(f"Found ricerca_blu.png at center ({x},{y}), clicking...")
pyautogui.click(x, y)

time.sleep(1.5)

# Check for se_questo_ok.png - if found proceed, otherwise jump to Punto_finale
try:
    result = pyautogui.locateCenterOnScreen('se_questo_ok.png')
except Exception as e:
    print(f"Image search error: {e}")
    result = None
time.sleep(1)

if result is not None:
    x, y = result
    print(f"Image 'se_questo_ok.png' found at {x}, {y} — proceeding...")
    
    skip_to_finale = False
    
    # saved position POS4 = (1400, 199)
    pyautogui.moveTo(1400, 199)
    time.sleep(0.5)
    pyautogui.click(1400, 199)
    time.sleep(1.5)
    # saved position POS5 = (1360, 205) data creazione
    # find the data_creazione image, then click the first freccia_data_creazione
    # that lies to the right of it
    rect = None
    for attempt in range(2):
        try:
            rect = pyautogui.locateOnScreen('data_creazione.jpg')
            if rect:
                break
        except Exception as e:
            print(f"Attempt {attempt+1}: Image search error for data_creazione.jpg: {e}")
        if attempt == 0:
            time.sleep(1)  # pause before retry
    
    if rect:
        print(f"Found data_creazione at {rect}, looking for arrow to the right")
        arrows = []
        for attempt in range(2):
            try:
                arrows = list(pyautogui.locateAllOnScreen('freccia_data_creazione.jpg'))
                if arrows:
                    break
            except Exception as e:
                print(f"Attempt {attempt+1}: Image search error for freccia_data_creazione.jpg: {e}")
            if attempt == 0:
                time.sleep(1)  # pause before retry
        
        # filter arrows positioned right of the data_creazione box
        right_arrows = [r for r in arrows if r.left > rect.left]
        if right_arrows:
            target = min(right_arrows, key=lambda r: r.left)
            cx, cy = pyautogui.center(target)
            print(f"Clicking arrow at ({cx},{cy})")
            pyautogui.click(cx, cy)
        else:
            print("No arrow found to the right of data_creazione, clicking POS5 fallback")
            pyautogui.click(*POS5)
    else:
        print("data_creazione.jpg not found, clicking POS5 fallback")
        pyautogui.click(*POS5)
    time.sleep(1.5)
    
    if not skip_to_finale:
        # saved position POS6 = (428, 254) click ufficio tecnico-disegni
        # Instead of clicking a fixed coordinate, search for the first occurrence
        # of the image 'ufficio-tecnico-disegni.png' from the top of the screen and click its center.
        matches = []
        for attempt in range(2):
            try:
                matches = list(pyautogui.locateAllOnScreen('ufficio-tecnico-disegni.png'))
                if matches:
                    break
            except Exception as e:
                print(f"Attempt {attempt+1}: Image search error for ufficio-tecnico-disegni.png: {e}")
            if attempt == 0:
                time.sleep(1)  # pause before retry

        if matches:
            # choose the match with smallest top (y) coordinate — i.e. first from the top
            top_match = min(matches, key=lambda r: r.top)
            cx, cy = pyautogui.center(top_match)
            print(f"Found ufficio-tecnico-disegni.png at center ({cx},{cy}), clicking...")
            pyautogui.click(cx, cy)
        else:
            print("ufficio-tecnico-disegni.png not found — jumping to Punto_finale")
            skip_to_finale = True

        time.sleep(2)
    
    if not skip_to_finale:
        # saved position POS7 = (2428, 93)
        #pyautogui.click(2428, 93)
        time.sleep(1.5)
        pyautogui.click(2290, 93)
        time.sleep(1.5)
        #x, y = pyautogui.locateCenterOnScreen('salva_pdf.jpg')
        #print(f"Found salva_pdf.jpg at center ({x},{y}), clicking...")
        #pyautogui.click(x, y)
        # saved position POS8 = (73, 199)
        #pyautogui.click(73, 199)
        #time.sleep(1.5)
        result_salva = None
        for attempt in range(2):
            try:
                result_salva = pyautogui.locateCenterOnScreen('salva_wind.png')
                if result_salva is not None:
                    break
            except Exception as e:
                print(f"Attempt {attempt+1}: Image search error for salva_wind.png: {e}")
            if attempt == 0:
                time.sleep(1)  # pause before retry
        
        if result_salva is not None:
            x, y = result_salva
            time.sleep(1.5)
            pyautogui.click(x, y)
        else:
            print("Image 'salva_wind.png' not found")
            time.sleep(1.5)
        
        # saved position POS9 = (772, 565)
        pyautogui.click(772, 565)
        time.sleep(1.5)
        # saved position POS10 = (504, 20)
        pyautogui.click(504, 20)
        time.sleep(1.5)
else:
    print("Image 'se_questo_ok.png' NOT found — jumping to Punto_finale...")

# Punto_finale torna indietro, saved position POS11 = (74, 165)
time.sleep(2)  # pause before going back
pyautogui.click(74, 165)
time.sleep(1.5)

if skip_to_finale:
    sys.exit(1)  # skip signal
else:
    sys.exit(0)  # success signal