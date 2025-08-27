from __future__ import annotations

import configparser
import re
from typing import List

from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

RICH_CONTAINER_SEL = "div.richtext-content-container"
PARAGRAPH_SEL = f"{RICH_CONTAINER_SEL} p"


# ---------- helpers (moved out of the main function) ----------

def setup_chrome_driver(headless: bool = True) -> webdriver.Chrome:
    """Create and return a configured Chrome WebDriver."""
    options = Options()
    if headless:
        # If this flag fails on your environment, change to "--headless"
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1200,1600")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--lang=de-DE")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    # slightly reduce automation fingerprints
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    return webdriver.Chrome(options=options)


def normalize_text(s: str) -> str:
    """Remove invisible chars; keep newlines; collapse spaces/tabs."""
    s = s.replace("\u00ad", "")   # soft hyphen
    s = s.replace("\u200b", "")   # zero-width space
    s = s.replace("\u2060", "")   # word joiner
    s = s.replace("\u00a0", " ")  # NBSP -> space
    s = re.sub(r"[ \t]+", " ", s) # collapse spaces/tabs (keep \n)
    return s.strip()


def click_consent_if_any(driver: webdriver.Chrome) -> bool:
    """Best-effort: dismiss common cookie consent buttons if visible."""
    candidates = [
        ("button", "Alle akzeptieren"),
        ("button", "Akzeptieren"),
        ("button", "Zustimmen"),
        ("button", "Einverstanden"),
        ("button[aria-label='Zustimmen']", None),
    ]
    clicked = False
    for css, text in candidates:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, css)
            for el in elements:
                if _should_click_element(el, text) and _try_click_element(el):
                    clicked = True
        except WebDriverException:
            # Finding elements failed unexpectedly; ignore and continue
            continue
    return clicked


def _should_click_element(el, text):
    """Helper function to determine if element should be clicked"""
    if not el.is_displayed():
        return False

    if text is None:
        return True

    label = (el.text or "").strip()
    return text.lower() in label.lower()


def _try_click_element(el):
    """Helper function to attempt clicking an element"""
    try:
        el.click()
        time.sleep(0.2)
        return True
    except (ElementClickInterceptedException, ElementNotInteractableException, WebDriverException):
        return False


def try_reveal_buttons(driver: webdriver.Chrome) -> int:
    """Click buttons that might reveal text (e.g., 'Lösung', 'anzeigen', 'Mehr')."""
    clicks = 0
    try:
        for b in driver.find_elements(By.TAG_NAME, "button"):
            t = (b.text or "").strip().lower()
            if any(k in t for k in ["lösung", "lösungen", "anzeigen", "einblenden", "mehr", "weiterlesen"]):
                if b.is_displayed():
                    try:
                        b.click()
                        time.sleep(0.2)
                        clicks += 1
                    except (ElementClickInterceptedException, ElementNotInteractableException, WebDriverException):
                        continue
    except WebDriverException:
        pass
    return clicks


def wait_for_container(driver: webdriver.Chrome, max_wait: int) -> None:
    """Wait until the rich text container is present, or raise TimeoutError."""
    try:
        WebDriverWait(driver, max_wait).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, RICH_CONTAINER_SEL))
        )
    except TimeoutException as exc:
        raise TimeoutError("Rich text container did not appear within timeout.") from exc


def get_paragraph_elements(driver: webdriver.Chrome) -> List:
    """Return current <p> elements under the content container."""
    # find_elements never raises NoSuchElementException; it returns an empty list
    return driver.find_elements(By.CSS_SELECTOR, PARAGRAPH_SEL)


def get_element_text_len(driver: webdriver.Chrome, el) -> int:
    """Return normalized innerText length of a WebElement."""
    try:
        raw = driver.execute_script("return arguments[0].innerText;", el) or ""
    except (StaleElementReferenceException, WebDriverException):
        # As a fallback, try 'text' property; may be empty or partial
        raw = getattr(el, "text", "") or ""
    return len(normalize_text(raw))


def ensure_paragraph_filled(
    driver: webdriver.Chrome,
    actions: ActionChains,
    p_el,
    per_para_wait: float,
    poll: float,
) -> None:
    """
    Scroll paragraph into view and wait until its text length grows and then stabilizes.
    This helps trigger lazy injections (e.g., IntersectionObserver).
    """
    deadline = time.time() + per_para_wait
    last_len = -1
    stable = 0

    # bring to viewport and hover
    try:
        actions.move_to_element(p_el).perform()
    except WebDriverException:
        pass
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", p_el)
    except WebDriverException:
        pass

    while time.time() < deadline:
        click_consent_if_any(driver)
        try_reveal_buttons(driver)

        try:
            cur_len = get_element_text_len(driver, p_el)
        except WebDriverException:
            cur_len = last_len

        if cur_len > last_len:
            last_len = cur_len
            stable = 0
        else:
            stable += 1

        if stable >= 2:
            break

        time.sleep(poll)


def extract_paragraph_texts(driver: webdriver.Chrome) -> List[str]:
    """Extract normalized textContent per <p>; keep paragraph boundaries (no fabrication)."""
    out: List[str] = []
    ps_final = get_paragraph_elements(driver)
    for p in ps_final:
        try:
            txt = driver.execute_script("return arguments[0].textContent;", p) or ""
        except (StaleElementReferenceException, WebDriverException):
            txt = getattr(p, "text", "") or ""
        txt = normalize_text(txt)
        if txt:
            out.append(txt)
    return out


import time
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    WebDriverException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)

# 受け入れボタンの候補（テキスト or セレクタ）
CONSENT_TEXT_KEYWORDS = [
    "alle akzeptieren", "akzeptieren", "zustimmen", "einverstanden",
    "accept all", "accept", "agree", "got it", "ok"
]
CONSENT_SELECTORS = [
    "#onetrust-accept-btn-handler",                     # OneTrust
    "button[aria-label='Zustimmen']",                   # generic
    "button[data-testid='uc-accept-all-button']",       # Usercentrics
    "button#sp-accept",                                 # SourcePoint (例)
    "button[mode='primary']",                           # 一部の汎用テーマ
]

def _safe_click(driver, el) -> bool:
    """Try normal click, JS click, and Enter key as fallbacks."""
    try:
        if not el.is_displayed():
            driver.execute_script("arguments[0].style.display='block';", el)
    except WebDriverException:
        pass
    try:
        el.click()
        return True
    except (ElementClickInterceptedException, ElementNotInteractableException, WebDriverException):
        pass
    # JS click
    try:
        driver.execute_script("arguments[0].click();", el)
        return True
    except WebDriverException:
        pass
    # Enter key as last resort
    try:
        from selenium.webdriver.common.keys import Keys
        el.send_keys(Keys.ENTER)
        return True
    except WebDriverException:
        return False

def _try_click_selectors_in_context(driver, selectors: List[str]) -> bool:
    for css in selectors:
        try:
            for el in driver.find_elements(By.CSS_SELECTOR, css):
                if _safe_click(driver, el):
                    return True
        except WebDriverException:
            continue
    return False


def _try_click_text_buttons_in_context(driver, keywords: List[str]) -> bool:
    """Find any <button> whose visible text contains keywords (case-insensitive)."""
    if _find_button("button", driver, keywords):
        # 一部のCMPは<a>をボタンとして使う
        return _find_button("a", driver, keywords)
    return False


def _find_button(tag, driver, keywords: List[str]) -> bool:
    try:
        for b in driver.find_elements(By.TAG_NAME, tag):
            t = (b.text or "").strip().lower()
            if any(k in t for k in keywords) and _safe_click(driver, b):
                return True
    except WebDriverException:
        pass
    return False

def _try_click_in_top_level(driver) -> bool:
    if _try_click_selectors_in_context(driver, CONSENT_SELECTORS):
        return True
    if _try_click_text_buttons_in_context(driver, CONSENT_TEXT_KEYWORDS):
        return True
    return False

def _try_click_in_iframes(driver) -> bool:
    """Iterate iframes (depth=1) and try same selectors/text inside."""
    frames = driver.find_elements(By.TAG_NAME, "iframe")
    for fr in frames:
        try:
            driver.switch_to.frame(fr)
            if _try_click_selectors_in_context(driver, CONSENT_SELECTORS):
                driver.switch_to.default_content()
                return True
            if _try_click_text_buttons_in_context(driver, CONSENT_TEXT_KEYWORDS):
                driver.switch_to.default_content()
                return True
            driver.switch_to.default_content()
        except WebDriverException:
            # 必ず元に戻す
            try:
                driver.switch_to.default_content()
            except WebDriverException:
                pass
            continue
    return False

def _try_click_in_shadow_dom(driver) -> bool:
    """
    Usercentrics等のshadow DOMをJSで直接走査してクリック。
    """
    js = r"""
    const keywords = %s;
    function matchesText(node) {
      const t = (node && (node.innerText || node.textContent) || '').trim().toLowerCase();
      return keywords.some(k => t.includes(k));
    }
    function clickNode(node) {
      try { node.click(); return true; } catch(e) {}
      try { node.dispatchEvent(new MouseEvent('click', {bubbles:true})); return true; } catch(e) {}
      return false;
    }
    function findInRoot(root) {
      if (!root) return false;
      const btns = root.querySelectorAll('button, a, [role="button"]');
      for (const n of btns) {
        if (matchesText(n) || n.matches('#onetrust-accept-btn-handler,[data-testid="uc-accept-all-button"]')) {
          if (clickNode(n)) return true;
        }
      }
      return false;
    }
    // 既知のホストを探す
    const hosts = [
      'usercentrics-root', '#usercentrics-root', 'uc-consent',
      '#onetrust-consent-sdk'
    ];
    for (const sel of hosts) {
      const h = document.querySelector(sel);
      if (!h) continue;
      const sr = h.shadowRoot || (h.attachShadow && h.attachShadow({mode:'open'}));
      if (sr && findInRoot(sr)) return true;
    }
    // 全shadowを総当り
    function* allShadowHosts(rootDoc) {
      const all = rootDoc.querySelectorAll('*');
      for (const el of all) {
        if (el.shadowRoot) yield el.shadowRoot;
      }
    }
    for (const sr of allShadowHosts(document)) {
      if (findInRoot(sr)) return true;
    }
    return false;
    """ % (CONSENT_TEXT_KEYWORDS,)
    try:
        return bool(driver.execute_script(js))
    except WebDriverException:
        return False

def accept_cookies_and_reload(driver, url: str, pause: float = 0.3) -> bool:
    """
    Click a cookie consent once (top-level, iframes, shadow DOM), then reload the same URL.
    Returns True if something was clicked.
    """
    clicked = False
    # 1) top-level
    if _try_click_in_top_level(driver):
        clicked = True
    # 2) iframes
    if not clicked and _try_click_in_iframes(driver):
        clicked = True
    # 3) shadow DOM
    if not clicked and _try_click_in_shadow_dom(driver):
        clicked = True

    if clicked:
        time.sleep(pause)
        try:
            driver.get(url)   # refresh by reloading the same URL (より確実)
        except WebDriverException:
            pass
        time.sleep(pause)
    return clicked

# ---------- main API ----------

def fetch_topthema_transcript(
    url_: str,
    output_file: str = "input/reference.txt",
    headless: bool = False,
    max_wait: int = 60,          # overall wait cap (seconds)
    per_para_wait: float = 6.0,  # per-paragraph wait cap (seconds)
    poll: float = 0.25           # polling interval (seconds)
) -> None:
    """
    Fetch manuscript from DW Top Thema /lm reliably:

      - Always use /lm (no fallback; no reconstruction).
      - For each <p>, scroll into view and wait for its text to 'fill':
          * placeholders often fill only when in viewport.
          * wait until text length grows and stabilizes.
      - Never abort on timeouts: always extract what is present at the end.
      - Sentence split by (.?!:) or newline (no dash splitting).
    """
    driver = setup_chrome_driver(headless=headless)
    actions = ActionChains(driver)

    try:
        # Navigate to /lm page
        lm_url = url_.rstrip("/") + "/lm"
        driver.get(lm_url)

        # click cookie consent once and reload the same page
        accept_cookies_and_reload(driver, lm_url)

        # Wait for container; raise TimeoutError if truly absent
        wait_for_container(driver, max_wait=max_wait)

        # Initial interactions to unlock content
        click_consent_if_any(driver)
        try_reveal_buttons(driver)

        # Ensure we have some paragraphs (poll until present or timeout)
        start = time.time()
        paragraphs = get_paragraph_elements(driver)
        while not paragraphs and (time.time() - start) < max_wait:
            time.sleep(0.25)
            paragraphs = get_paragraph_elements(driver)

        # Pass 1: per-paragraph 'fill' (scroll + stability wait)
        for p in paragraphs:
            ensure_paragraph_filled(driver, actions, p, per_para_wait=per_para_wait, poll=poll)

        # Pass 2: slow page scroll down/up to trigger any late injections
        for _ in range(8):
            try:
                driver.execute_script("window.scrollBy(0, 500);")
            except WebDriverException:
                break
            click_consent_if_any(driver)
            try_reveal_buttons(driver)
            time.sleep(0.2)
        for _ in range(8):
            try:
                driver.execute_script("window.scrollBy(0, -500);")
            except WebDriverException:
                break
            time.sleep(0.1)

        # Extract final text per paragraph
        para_texts = extract_paragraph_texts(driver)

        # Join paragraphs; then split sentences by (.?!:) or newline
        script_text = "\n".join(para_texts)
        sentences = re.split(r"(?<=[.?!:])\s+|\n+", script_text)

        # Write output
        with open(output_file, "w", encoding="utf-8") as f:
            for s in sentences:
                s = s.strip()
                if s:
                    f.write(s + "\n")

    finally:
        try:
            driver.quit()
        except WebDriverException:
            # Driver already closed or unreachable; nothing else to do
            pass


if __name__ == "__main__":
    # read config
    config = configparser.ConfigParser()
    config.read('config.ini')
    url = config['TOP_THEMA']['url']

    fetch_topthema_transcript(url)

