import os
import sys
import time
import socket
import subprocess
import pytest
from datetime import date
from playwright.sync_api import sync_playwright

# Setup paths
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(TEST_DIR)

TEST_PORT = 8089
BASE_URL = f"http://localhost:{TEST_PORT}"

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

@pytest.fixture(scope="module")
def dashboard_server():
    """Fixture to start the cantor dashboard server on a test port."""
    server_script = os.path.join(REPO_DIR, "cantor_dashboard", "server.py")
    
    server_log_path = os.path.join(REPO_DIR, "scratch", "server.log")
    os.makedirs(os.path.dirname(server_log_path), exist_ok=True)
    server_log = open(server_log_path, "w", encoding="utf-8")
    
    # Start the server subprocess on a custom port to avoid collisions
    env = os.environ.copy()
    env["PORT"] = str(TEST_PORT)
    
    print(f"\n[Test UI] Starting dashboard server on port {TEST_PORT}...")
    proc = subprocess.Popen(
        [sys.executable, server_script],
        env=env,
        stdout=server_log,
        stderr=server_log
    )
    
    # Wait for port to open
    retries = 20
    server_ready = False
    for i in range(retries):
        if is_port_open(TEST_PORT):
            server_ready = True
            break
        time.sleep(0.5)
        
    if not server_ready:
        proc.terminate()
        server_log.close()
        # Read the log to show why it failed
        with open(server_log_path, "r", encoding="utf-8") as f:
            log_content = f.read()
        raise RuntimeError(f"Server failed to start on port {TEST_PORT}. Logs:\n{log_content}")
        
    print("[Test UI] Server is ready. Running UI assertions...")
    yield BASE_URL
    
    print("[Test UI] Shutting down dashboard server...")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    server_log.close()


def test_badge_readability_and_wrapping(dashboard_server):
    """End-to-end UI readability test asserting that badges do not wrap onto multiple lines."""
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        
        # Test across different viewports (Desktop, Tablet, Mobile)
        viewports = [
            {"width": 1200, "height": 800, "name": "Desktop"},
            {"width": 768, "height": 1024, "name": "Tablet"},
            {"width": 375, "height": 667, "name": "Mobile"}
        ]
        
        # Sample dates to test
        sample_dates = [
            "2026-06-13",  # Saturday with simple martyr (Julian) and hierarch
            "2026-06-21",  # Sunday with martyr (Julian of Tarsus)
            "2026-06-24",  # Nativity of St. John the Baptist (Vigil)
            "2026-06-30"   # Synaxis of the 12 Apostles (Great Doxology)
        ]
        
        for viewport in viewports:
            page = browser.new_page(viewport=viewport)
            
            # Log console and errors to a file for diagnosis
            log_file_path = os.path.join(REPO_DIR, "scratch", "ui_console.log")
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
            
            def log_console(msg):
                log_msg = f"[Console] {msg.type}: {msg.text}\n"
                print(log_msg.strip(), flush=True)
                with open(log_file_path, "a", encoding="utf-8") as lf:
                    lf.write(log_msg)
                    
            def log_error(err):
                log_msg = f"[Page Error] {err}\n"
                print(log_msg.strip(), flush=True)
                with open(log_file_path, "a", encoding="utf-8") as lf:
                    lf.write(log_msg)
            
            page.on("console", log_console)
            page.on("pageerror", log_error)
            page.goto(BASE_URL)
            
            # Verify basic elements are loaded
            page.wait_for_selector("#liturgical-date-input")
            page.wait_for_selector("#resolve-date-btn")
            
            # Wait for initial load spinner to hide to prevent race conditions
            try:
                page.wait_for_selector("#context-spinner", state="hidden", timeout=10000)
            except Exception as e:
                print(f"[Test UI] Warning: Initial spinner did not hide on {viewport['name']}: {e}", flush=True)
            
            for test_date in sample_dates:
                print(f"[Test UI] Viewport: {viewport['name']} ({viewport['width']}px) | Resolving date: {test_date}", flush=True)
                
                # Fill the date input and trigger resolve
                page.fill("#liturgical-date-input", test_date)
                page.click("#resolve-date-btn")
                
                # Wait for response and context rendering
                page.wait_for_selector("#context-spinner", state="hidden", timeout=15000)
                page.wait_for_selector(".context-row", timeout=15000)
                
                # Capture visual regression screenshots
                screenshots_dir = os.path.join(REPO_DIR, "audit_results", "screenshots")
                os.makedirs(screenshots_dir, exist_ok=True)
                screenshot_path = os.path.join(screenshots_dir, f"{viewport['name']}_{test_date}.png")
                page.screenshot(path=screenshot_path)
                print(f"[Test UI] Saved screenshot to {screenshot_path}", flush=True)
                
                # Retrieve all badge elements on the context card
                # This matches all bordered badges (season, tone, fast, color, category, etc.)
                badge_classes = [
                    ".badge", 
                    ".badge-category", 
                    ".badge-season", 
                    ".badge-tone", 
                    ".badge-fast", 
                    ".badge-color"
                ]
                
                badge_selectors = ", ".join(badge_classes)
                badges = page.query_selector_all(badge_selectors)
                
                assert len(badges) > 0, f"No badges found on the page for date {test_date}"
                
                for idx, badge in enumerate(badges):
                    text = badge.inner_text().strip()
                    box = badge.bounding_box()
                    
                    if not box or not text:
                        continue
                    
                    # Assertions for single-line readability:
                    # 1. Height check: A badge that wraps (e.g. "HIERAR\nCH") will render at ~32px to 48px height.
                    #    A single-line badge with padding is typically between 14px and 26px height.
                    #    We assert height remains strictly below 28px.
                    assert box["height"] < 28, (
                        f"Readability Failure in {viewport['name']} view! "
                        f"Badge '{text}' wrapped and rendered at {box['height']}px height. "
                        f"Expected height < 28px (single-line limit)."
                    )
                    
                    # 2. Bounding box sanity checks
                    assert box["width"] > 0, f"Badge '{text}' has zero width."
                    assert box["height"] > 0, f"Badge '{text}' has zero height."
                    
                    # 3. Text Overflow / Clipping Check:
                    # Assert that the element's scrollWidth is equal to or less than its clientWidth.
                    # If scrollWidth > clientWidth, the text content is being clipped.
                    has_overflow = badge.evaluate("(el) => el.scrollWidth > el.clientWidth")
                    assert not has_overflow, (
                        f"Readability Failure in {viewport['name']} view! "
                        f"Badge '{text}' has clipped text (scrollWidth {badge.evaluate('(el) => el.scrollWidth')} > clientWidth {badge.evaluate('(el) => el.clientWidth')})."
                    )
                    
                    # 4. Programmatic Contrast Ratio Check:
                    # Computes sRGB relative luminance with alpha blending and asserts WCAG AA standards (>= 3.0:1 for large/bold text).
                    js_contrast_checker = """
                    (el) => {
                        function parseRgb(colorStr) {
                            const matches = colorStr.match(/\\d+(\\.\\d+)?/g);
                            if (!matches) return [255, 255, 255];
                            return matches.slice(0, 3).map(Number);
                        }
                        function getLuminance(r, g, b) {
                            let a = [r, g, b].map(v => {
                                v /= 255;
                                return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
                            });
                            return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722;
                        }
                        function getCompositedBgColor(targetEl) {
                            let colors = [];
                            let current = targetEl;
                            while (current) {
                                const bg = window.getComputedStyle(current).backgroundColor;
                                if (bg && bg !== "transparent" && bg !== "rgba(0, 0, 0, 0)") {
                                    const matches = bg.match(/\\d+(\\.\\d+)?/g);
                                    if (matches) {
                                        const r = Number(matches[0]);
                                        const g = Number(matches[1]);
                                        const b = Number(matches[2]);
                                        const a = matches[3] !== undefined ? Number(matches[3]) : 1.0;
                                        colors.push({ r, g, b, a });
                                        if (a === 1.0) break;
                                    }
                                }
                                current = current.parentElement;
                            }
                            let r = 255, g = 255, b = 255; // default fallback white background
                            for (let i = colors.length - 1; i >= 0; i--) {
                                const c = colors[i];
                                r = c.r * c.a + r * (1 - c.a);
                                g = c.g * c.a + g * (1 - c.a);
                                b = c.b * c.a + b * (1 - c.a);
                            }
                            return [r, g, b];
                        }
                        const style = window.getComputedStyle(el);
                        const rgb1 = parseRgb(style.color);
                        const rgb2 = getCompositedBgColor(el);
                        const lum1 = getLuminance(...rgb1);
                        const lum2 = getLuminance(...rgb2);
                        return (Math.max(lum1, lum2) + 0.05) / (Math.min(lum1, lum2) + 0.05);
                    }
                    """
                    contrast_ratio = badge.evaluate(js_contrast_checker)
                    assert contrast_ratio >= 3.0, (
                        f"Readability Failure in {viewport['name']} view! "
                        f"Badge '{text}' has low contrast ratio: {contrast_ratio:.2f}:1. "
                        f"Expected contrast ratio >= 3.0:1."
                    )
            
            page.close()
        
        browser.close()


def test_stress_data_rendering(dashboard_server):
    """Stress test the dashboard UI layout using Playwright request interception with a massive commemoration string."""
    import json
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 375, "height": 667}) # Mobile viewport
        
        # Intercept api resolve request and inject stress content
        def handle_route(route):
            response = route.fetch()
            data = response.json()
            
            # Inject massive commemoration string
            data["context"]["commemoration"] = (
                "Lorem Ipsum Venerable Martyr Saint Hieromartyr Apostle Prophet Onuphrius Bartholomew Basil Nicholas "
                "the Wonderworker Bartholomew & Barnabas and Peter and Paul of Stamford Stamford Divine Office "
                "Recension Recension Source Assets Universal Feast day collision check of the Lviv Synod"
            )
            # Add multiple long saints
            data["context"]["commemoration_list"] = [
                "Extremely Long Saint Commemoration Name Part One the Martyr of Tarsus",
                "Second Extremely Long Venerable Father Onuphrius the Great Hierarch of Kyivan Chant"
            ]
            route.fulfill(json=data)
            
        page.route("**/api/resolve*", handle_route)
        
        page.goto(BASE_URL)
        page.wait_for_selector("#liturgical-date-input")
        
        # Resolve a date to trigger mock data rendering
        page.fill("#liturgical-date-input", "2026-06-13")
        page.click("#resolve-date-btn")
        
        page.wait_for_selector("#context-spinner", state="hidden", timeout=15000)
        page.wait_for_selector(".context-row", timeout=15000)
        
        # Capture a screenshot of the stress layout
        screenshots_dir = os.path.join(REPO_DIR, "audit_results", "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        page.screenshot(path=os.path.join(screenshots_dir, "Mobile_Stress_Test.png"))
        print("[Test UI] Saved Mobile stress test screenshot", flush=True)
        
        # Verify that key elements don't crash and badges are checked
        badges = page.query_selector_all(".badge, .badge-category")
        for badge in badges:
            text = badge.inner_text().strip()
            box = badge.bounding_box()
            if not box or not text:
                continue
            # Badges should still be a reasonable height and not wrap out of control under stress
            assert box["height"] < 35, f"Badge '{text}' wrapped too many times under stress: {box['height']}px"
            
        page.close()
        browser.close()
