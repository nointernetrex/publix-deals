"""
Publix Deals Website Generator
Double-click update_website.bat to run this script.
It reads Publix_Final.docx and generates index.html, styles.css, and script.js for GitHub Pages.
"""

import re
import sys
from pathlib import Path
from docx import Document

# Check if running in CI mode (no user prompts)
CI_MODE = '--ci' in sys.argv

# Paths
SCRIPT_DIR = Path(__file__).parent
DOCX_PATH = SCRIPT_DIR / "Publix_Final.docx"
OUTPUT_HTML = SCRIPT_DIR / "index.html"
OUTPUT_CSS = SCRIPT_DIR / "styles.css"
OUTPUT_JS = SCRIPT_DIR / "script.js"


def parse_document():
    """Parse the Word document and extract deal data."""
    doc = Document(DOCX_PATH)

    content = {
        'triple_stacks': [],
        'double_stacks': [],
        'bogo_deals': {},
        'digital_coupons': {}
    }

    current_section = None
    current_category = None
    current_deal = None
    current_field = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Detect main sections
        if 'TRIPLE STACKS' in text.upper():
            if current_deal and current_section in ['triple_stacks', 'double_stacks']:
                content[current_section].append(current_deal)
                current_deal = None
            current_section = 'triple_stacks'
            current_field = None
            continue
        elif 'DOUBLE STACKS' in text.upper():
            if current_deal and current_section in ['triple_stacks', 'double_stacks']:
                content[current_section].append(current_deal)
                current_deal = None
            current_section = 'double_stacks'
            current_field = None
            continue
        elif 'BOGO DEALS' in text.upper():
            if current_deal and current_section in ['triple_stacks', 'double_stacks']:
                content[current_section].append(current_deal)
                current_deal = None
            current_section = 'bogo_deals'
            current_field = None
            continue
        elif 'DIGITAL COUPONS' in text.upper() and not text.endswith(':'):
            current_section = 'digital_coupons'
            current_field = None
            continue

        # Handle Triple and Double Stacks
        if current_section in ['triple_stacks', 'double_stacks']:
            if text == 'Sale:':
                current_field = 'sale'
            elif text.startswith('Digital Coupon'):
                current_field = 'coupons'
            elif text == 'Buy:':
                current_field = 'buy'
            elif text == 'Why this works:':
                current_field = 'why'
            elif (text.startswith('-') or text.startswith('–') or text.startswith('•') or text.startswith(' ')) and current_deal and current_field:
                item = text.lstrip('-–•  ').strip()
                if current_field == 'why':
                    current_deal['why'] = item
                else:
                    current_deal[current_field].append(item)
            elif current_field == 'why' and current_deal and not text.startswith('-'):
                current_deal['why'] = text
                current_field = None
            elif not text.startswith('-') and current_field != 'why':
                if current_deal:
                    content[current_section].append(current_deal)
                current_deal = {
                    'name': text,
                    'sale': [],
                    'coupons': [],
                    'buy': [],
                    'why': ''
                }
                current_field = None

        # Handle BOGO Deals and Digital Coupons
        elif current_section in ['bogo_deals', 'digital_coupons']:
            if not text.startswith('-') and len(text) < 50 and not any(c in text for c in ['$', '—', 'Save', 'Buy', 'Free']):
                current_category = text
                if current_category not in content[current_section]:
                    content[current_section][current_category] = []
            elif text.startswith('-') and current_category:
                item = text.lstrip('- ').strip()
                content[current_section][current_category].append(item)

    if current_deal and current_section in ['triple_stacks', 'double_stacks']:
        content[current_section].append(current_deal)

    return content


def escape_js_string(s):
    """Escape a string for use in JavaScript."""
    return s.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n').replace('\r', '')


def generate_css():
    """Generate the styles.css file."""
    return '''/* SquatchyStack.com - Modern Deal Hunter Styles */
/* Robinhood-inspired: clean, confident, modern */

:root {
    --primary-green: #00d084;
    --primary-dark: #00875a;
    --accent-lime: #00ff9d;
    --accent-teal: #20c997;
    --bg-dark: #000000;
    --bg-card: #111111;
    --bg-elevated: #1a1a1a;
    --bg-hover: #222222;
    --text-primary: #ffffff;
    --text-secondary: #a0a0a0;
    --text-muted: #666666;
    --border-light: #2a2a2a;
    --border-medium: #333333;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
    --shadow-lg: 0 8px 24px rgba(0,0,0,0.5);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-full: 50px;
    --transition: all 0.2s ease;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #000000;
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
}

/* ===== SASQUATCH WATERMARK ===== */
.squatch-watermark {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 800px;
    height: 900px;
    opacity: 0.08;
    pointer-events: none;
    z-index: 0;
}

/* ===== HEADER ===== */
.header {
    position: sticky;
    top: 0;
    z-index: 1000;
    background: rgba(0, 0, 0, 0.9);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border-light);
    padding: 0 24px;
}

.header-inner {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 72px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    text-decoration: none;
    color: var(--text-primary);
}

.brand-icon {
    width: 42px;
    height: 42px;
}

.brand-text {
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--primary-green) 0%, var(--accent-lime) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.nav {
    display: flex;
    align-items: center;
    gap: 8px;
}

.nav-link {
    padding: 10px 18px;
    color: var(--text-secondary);
    text-decoration: none;
    font-weight: 500;
    font-size: 0.95rem;
    border-radius: var(--radius-full);
    transition: var(--transition);
}

.nav-link:hover {
    color: var(--primary-green);
    background: rgba(0, 135, 90, 0.08);
}

.nav-link.active {
    color: var(--primary-green);
    background: rgba(0, 135, 90, 0.1);
}

.last-updated {
    font-size: 0.85rem;
    color: var(--text-muted);
    padding: 6px 14px;
    background: var(--bg-hover);
    border-radius: var(--radius-full);
}

.mobile-menu-btn {
    display: none;
    background: none;
    border: none;
    padding: 8px;
    cursor: pointer;
    color: var(--text-primary);
}

/* ===== HERO SECTION ===== */
.hero {
    position: relative;
    padding: 80px 24px 60px;
    text-align: center;
    background: linear-gradient(180deg, #0a0a0a 0%, #000000 100%);
    border-bottom: 1px solid var(--border-light);
}

.hero-content {
    max-width: 800px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
}

.hero h1 {
    font-size: 3.5rem;
    font-weight: 800;
    color: var(--text-primary);
    margin-bottom: 16px;
    letter-spacing: -0.02em;
}

.hero h1 span {
    background: linear-gradient(135deg, var(--primary-green) 0%, var(--accent-lime) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-subtitle {
    font-size: 1.25rem;
    color: var(--text-secondary);
    margin-bottom: 40px;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

/* ===== SEARCH BAR ===== */
.search-container {
    max-width: 600px;
    margin: 0 auto 32px;
    position: relative;
}

.search-input {
    width: 100%;
    padding: 18px 24px 18px 56px;
    font-size: 1.1rem;
    border: 2px solid var(--border-medium);
    border-radius: var(--radius-full);
    background: var(--bg-card);
    color: var(--text-primary);
    transition: var(--transition);
    outline: none;
}

.search-input:focus {
    border-color: var(--primary-green);
    box-shadow: 0 0 0 4px rgba(0, 135, 90, 0.1);
}

.search-input::placeholder {
    color: var(--text-muted);
}

.search-icon {
    position: absolute;
    left: 20px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-muted);
    pointer-events: none;
}

.search-clear {
    position: absolute;
    right: 16px;
    top: 50%;
    transform: translateY(-50%);
    background: var(--border-light);
    border: none;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    cursor: pointer;
    display: none;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
    transition: var(--transition);
}

.search-clear.visible {
    display: flex;
}

.search-clear:hover {
    background: var(--border-medium);
}

/* ===== FILTER CHIPS ===== */
.filter-chips {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
}

.filter-chip {
    padding: 10px 20px;
    font-size: 0.9rem;
    font-weight: 600;
    border: 2px solid var(--border-medium);
    border-radius: var(--radius-full);
    background: var(--bg-card);
    color: var(--text-secondary);
    cursor: pointer;
    transition: var(--transition);
}

.filter-chip:hover {
    border-color: var(--primary-green);
    color: var(--primary-green);
}

.filter-chip.active {
    background: var(--primary-green);
    border-color: var(--primary-green);
    color: white;
}

.filter-chip.clear-filter {
    background: transparent;
    border-style: dashed;
}

.filter-chip.clear-filter:hover {
    background: rgba(0, 135, 90, 0.05);
}

/* ===== MAIN CONTENT ===== */
.main-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 24px;
    position: relative;
    z-index: 1;
}

/* ===== SECTION STYLES ===== */
.deals-section {
    margin-bottom: 48px;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 2px solid var(--border-light);
}

.section-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, var(--primary-green) 0%, var(--accent-teal) 100%);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
}

.section-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--text-primary);
}

.section-count {
    margin-left: auto;
    font-size: 0.9rem;
    color: var(--text-muted);
    background: var(--bg-hover);
    padding: 6px 14px;
    border-radius: var(--radius-full);
}

/* ===== DEALS LIST ===== */
.deals-list {
    background: var(--bg-card);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-light);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}

.deal-row {
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 16px;
    align-items: start;
    padding: 20px 24px;
    border-bottom: 1px solid var(--border-light);
    transition: var(--transition);
}

.deal-row:last-child {
    border-bottom: none;
}

.deal-row:hover {
    background: var(--bg-hover);
}

.deal-row:nth-child(even) {
    background: rgba(255, 255, 255, 0.02);
}

.deal-row:nth-child(even):hover {
    background: var(--bg-hover);
}

.deal-badge {
    padding: 6px 12px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-radius: var(--radius-sm);
    white-space: nowrap;
}

.badge-triple {
    background: linear-gradient(135deg, #ffd700 0%, #ffb700 100%);
    color: #5d4e00;
}

.badge-double {
    background: linear-gradient(135deg, #c0c0c0 0%, #a8a8a8 100%);
    color: #3d3d3d;
}

.badge-bogo {
    background: linear-gradient(135deg, var(--primary-green) 0%, var(--accent-teal) 100%);
    color: white;
}

.badge-coupon {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white;
}

.deal-content {
    min-width: 0;
}

.deal-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 6px;
}

.deal-details {
    font-size: 0.9rem;
    color: var(--text-secondary);
    line-height: 1.5;
}

.deal-details strong {
    color: var(--primary-green);
    font-weight: 600;
}

.deal-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 8px;
}

.deal-tag {
    font-size: 0.8rem;
    padding: 4px 10px;
    background: var(--bg-elevated);
    color: var(--text-muted);
    border-radius: var(--radius-sm);
}

.deal-actions {
    display: flex;
    gap: 8px;
}

.copy-btn {
    padding: 8px 14px;
    font-size: 0.85rem;
    font-weight: 500;
    background: var(--bg-elevated);
    border: 1px solid var(--border-medium);
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: var(--transition);
    color: var(--text-secondary);
    white-space: nowrap;
}

.copy-btn:hover {
    background: var(--primary-green);
    border-color: var(--primary-green);
    color: white;
}

.copy-btn.copied {
    background: var(--accent-lime);
    border-color: var(--accent-lime);
    color: var(--primary-dark);
}

/* ===== CATEGORY DIVIDER ===== */
.category-divider {
    padding: 14px 24px;
    background: linear-gradient(90deg, var(--primary-green) 0%, var(--accent-teal) 100%);
    color: white;
    font-weight: 600;
    font-size: 0.95rem;
    letter-spacing: 0.3px;
}

/* ===== STACK DEAL EXPANDED ===== */
.stack-deal-content {
    display: grid;
    gap: 12px;
}

.stack-section {
    display: flex;
    gap: 8px;
}

.stack-label {
    font-weight: 600;
    color: var(--primary-green);
    min-width: 100px;
    font-size: 0.85rem;
}

.stack-items {
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.stack-why {
    margin-top: 8px;
    padding: 12px 16px;
    background: rgba(245, 158, 11, 0.1);
    border-radius: var(--radius-sm);
    border-left: 3px solid #f59e0b;
    font-size: 0.9rem;
    color: #fbbf24;
}

/* ===== NO RESULTS ===== */
.no-results {
    text-align: center;
    padding: 60px 24px;
    color: var(--text-muted);
}

.no-results-icon {
    font-size: 3rem;
    margin-bottom: 16px;
}

.no-results h3 {
    font-size: 1.25rem;
    color: var(--text-secondary);
    margin-bottom: 8px;
}

/* ===== FOOTER ===== */
.footer {
    background: var(--bg-dark);
    color: white;
    padding: 60px 24px 40px;
    margin-top: 80px;
}

.footer-inner {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    gap: 48px;
}

.footer-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
}

.footer-brand-text {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--accent-lime);
}

.footer-tagline {
    color: rgba(255,255,255,0.7);
    margin-bottom: 24px;
    line-height: 1.6;
}

.footer-disclaimer {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.5);
    padding-top: 16px;
    border-top: 1px solid rgba(255,255,255,0.1);
}

.footer-section h4 {
    font-size: 0.9rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: rgba(255,255,255,0.5);
    margin-bottom: 20px;
}

.footer-links {
    list-style: none;
}

.footer-links li {
    margin-bottom: 12px;
}

.footer-links a {
    color: rgba(255,255,255,0.8);
    text-decoration: none;
    transition: var(--transition);
}

.footer-links a:hover {
    color: var(--accent-lime);
}

.footer-bottom {
    max-width: 1200px;
    margin: 40px auto 0;
    padding-top: 24px;
    border-top: 1px solid rgba(255,255,255,0.1);
    text-align: center;
    color: rgba(255,255,255,0.5);
    font-size: 0.85rem;
}

/* ===== ABOUT SECTION ===== */
.about-section {
    background: var(--bg-card);
    border-radius: var(--radius-lg);
    padding: 48px;
    margin-bottom: 48px;
    border: 1px solid var(--border-light);
    box-shadow: var(--shadow-sm);
}

.about-section h2 {
    font-size: 2rem;
    margin-bottom: 16px;
    color: var(--text-primary);
}

.about-section p {
    color: var(--text-secondary);
    font-size: 1.1rem;
    line-height: 1.8;
    max-width: 800px;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 1024px) {
    .footer-inner {
        grid-template-columns: 1fr 1fr;
    }

    .footer-brand-section {
        grid-column: span 2;
    }
}

@media (max-width: 768px) {
    .header-inner {
        height: 64px;
    }

    .nav {
        display: none;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: var(--bg-card);
        flex-direction: column;
        padding: 16px;
        border-bottom: 1px solid var(--border-light);
        box-shadow: var(--shadow-md);
    }

    .nav.open {
        display: flex;
    }

    .mobile-menu-btn {
        display: block;
    }

    .last-updated {
        display: none;
    }

    .hero {
        padding: 48px 16px 40px;
    }

    .hero h1 {
        font-size: 2.25rem;
    }

    .hero-subtitle {
        font-size: 1rem;
    }

    .search-input {
        padding: 14px 20px 14px 48px;
        font-size: 1rem;
    }

    .filter-chips {
        gap: 8px;
    }

    .filter-chip {
        padding: 8px 14px;
        font-size: 0.85rem;
    }

    .main-content {
        padding: 24px 16px;
    }

    .deal-row {
        grid-template-columns: 1fr;
        gap: 12px;
        padding: 16px;
    }

    .deal-badge {
        justify-self: start;
    }

    .deal-actions {
        justify-self: start;
    }

    .section-header {
        flex-wrap: wrap;
    }

    .section-count {
        margin-left: 0;
        width: 100%;
        text-align: center;
    }

    .footer-inner {
        grid-template-columns: 1fr;
        gap: 32px;
    }

    .footer-brand-section {
        grid-column: span 1;
    }

    .about-section {
        padding: 32px 24px;
    }

    .squatch-watermark {
        width: 400px;
        height: 450px;
    }
}

@media (max-width: 480px) {
    .brand-text {
        font-size: 1.25rem;
    }

    .hero h1 {
        font-size: 1.85rem;
    }

    .filter-chip {
        padding: 8px 12px;
        font-size: 0.8rem;
    }

    .stack-section {
        flex-direction: column;
        gap: 4px;
    }

    .stack-label {
        min-width: auto;
    }
}

/* ===== ANIMATIONS ===== */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.deal-row {
    animation: fadeIn 0.3s ease forwards;
}

/* ===== ACCESSIBILITY ===== */
.visually-hidden {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

:focus-visible {
    outline: 2px solid var(--primary-green);
    outline-offset: 2px;
}

/* ===== PRINT STYLES ===== */
@media print {
    .header, .hero, .footer, .squatch-watermark, .copy-btn, .filter-chips, .search-container {
        display: none !important;
    }

    .main-content {
        padding: 0;
    }

    .deals-list {
        box-shadow: none;
        border: 1px solid #ccc;
    }
}
'''


def generate_js():
    """Generate the script.js file."""
    return '''// SquatchyStack.com - Deal Hunter Scripts

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const searchInput = document.getElementById('search-input');
    const searchClear = document.getElementById('search-clear');
    const filterChips = document.querySelectorAll('.filter-chip:not(.clear-filter)');
    const clearFilterBtn = document.querySelector('.filter-chip.clear-filter');
    const dealRows = document.querySelectorAll('.deal-row');
    const sections = document.querySelectorAll('.deals-section');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const nav = document.getElementById('main-nav');

    let activeFilter = null;

    // Mobile menu toggle
    if (mobileMenuBtn && nav) {
        mobileMenuBtn.addEventListener('click', function() {
            nav.classList.toggle('open');
            const isOpen = nav.classList.contains('open');
            mobileMenuBtn.setAttribute('aria-expanded', isOpen);
        });
    }

    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();

            // Show/hide clear button
            if (searchClear) {
                searchClear.classList.toggle('visible', query.length > 0);
            }

            filterDeals();
        });
    }

    // Search clear button
    if (searchClear) {
        searchClear.addEventListener('click', function() {
            searchInput.value = '';
            searchClear.classList.remove('visible');
            filterDeals();
            searchInput.focus();
        });
    }

    // Filter chips
    filterChips.forEach(chip => {
        chip.addEventListener('click', function() {
            const filter = this.dataset.filter;

            // Toggle active state
            if (activeFilter === filter) {
                activeFilter = null;
                this.classList.remove('active');
            } else {
                filterChips.forEach(c => c.classList.remove('active'));
                this.classList.add('active');
                activeFilter = filter;
            }

            filterDeals();
        });
    });

    // Clear filters
    if (clearFilterBtn) {
        clearFilterBtn.addEventListener('click', function() {
            activeFilter = null;
            filterChips.forEach(c => c.classList.remove('active'));
            searchInput.value = '';
            if (searchClear) searchClear.classList.remove('visible');
            filterDeals();
        });
    }

    // Filter deals function
    function filterDeals() {
        const query = searchInput ? searchInput.value.toLowerCase().trim() : '';

        dealRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const type = row.dataset.type;

            const matchesSearch = !query || text.includes(query);
            const matchesFilter = !activeFilter || type === activeFilter;

            row.style.display = matchesSearch && matchesFilter ? '' : 'none';
        });

        // Update section visibility and counts
        sections.forEach(section => {
            const visibleRows = section.querySelectorAll('.deal-row[style=""], .deal-row:not([style])');
            const visibleCount = Array.from(section.querySelectorAll('.deal-row'))
                .filter(row => row.style.display !== 'none').length;

            const countEl = section.querySelector('.section-count');
            if (countEl) {
                countEl.textContent = visibleCount + ' deals';
            }

            // Hide section if no visible deals
            const dealsList = section.querySelector('.deals-list');
            if (dealsList) {
                const hasVisible = Array.from(dealsList.querySelectorAll('.deal-row'))
                    .some(row => row.style.display !== 'none');
                section.style.display = hasVisible ? '' : 'none';
            }
        });

        // Show no results message
        updateNoResults();
    }

    // No results message
    function updateNoResults() {
        let noResultsEl = document.getElementById('no-results');
        const anyVisible = Array.from(dealRows).some(row => row.style.display !== 'none');

        if (!anyVisible) {
            if (!noResultsEl) {
                noResultsEl = document.createElement('div');
                noResultsEl.id = 'no-results';
                noResultsEl.className = 'no-results';
                noResultsEl.innerHTML = `
                    <div class="no-results-icon">🔍</div>
                    <h3>No deals found</h3>
                    <p>Try adjusting your search or filters</p>
                `;
                document.querySelector('.main-content').appendChild(noResultsEl);
            }
            noResultsEl.style.display = '';
        } else if (noResultsEl) {
            noResultsEl.style.display = 'none';
        }
    }

    // Copy to clipboard functionality
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            const dealRow = this.closest('.deal-row');
            const dealText = dealRow.dataset.copyText || dealRow.querySelector('.deal-content').textContent.trim();

            try {
                await navigator.clipboard.writeText(dealText);

                const originalText = this.textContent;
                this.textContent = 'Copied!';
                this.classList.add('copied');

                setTimeout(() => {
                    this.textContent = originalText;
                    this.classList.remove('copied');
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        });
    });

    // Smooth scroll for nav links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = target.offsetTop - headerHeight - 20;
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                if (nav) nav.classList.remove('open');
            }
        });
    });

    // Keyboard navigation for chips
    filterChips.forEach(chip => {
        chip.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
});
'''


def generate_html(content):
    """Generate the HTML website from parsed content."""

    # Build Triple Stacks rows
    triple_rows = ""
    for deal in content['triple_stacks']:
        sale_text = ', '.join(deal['sale']) if deal['sale'] else ''
        coupon_text = ', '.join(deal['coupons']) if deal['coupons'] else ''
        buy_text = ', '.join(deal['buy']) if deal['buy'] else ''
        copy_text = f"{deal['name']} - Sale: {sale_text} | Coupons: {coupon_text} | Buy: {buy_text}"

        triple_rows += f'''
        <div class="deal-row" data-type="triple" data-copy-text="{escape_js_string(copy_text)}">
            <span class="deal-badge badge-triple">Triple</span>
            <div class="deal-content">
                <div class="deal-title">{deal['name']}</div>
                <div class="stack-deal-content">
                    <div class="stack-section">
                        <span class="stack-label">Sale:</span>
                        <span class="stack-items">{sale_text}</span>
                    </div>
                    <div class="stack-section">
                        <span class="stack-label">Coupons:</span>
                        <span class="stack-items">{coupon_text}</span>
                    </div>
                    <div class="stack-section">
                        <span class="stack-label">Buy:</span>
                        <span class="stack-items">{buy_text}</span>
                    </div>
                    {f'<div class="stack-why"><strong>Why:</strong> {deal["why"]}</div>' if deal['why'] else ''}
                </div>
            </div>
            <div class="deal-actions">
                <button class="copy-btn" aria-label="Copy deal to clipboard">Copy</button>
            </div>
        </div>'''

    # Build Double Stacks rows
    double_rows = ""
    for deal in content['double_stacks']:
        sale_text = ', '.join(deal['sale']) if deal['sale'] else ''
        coupon_text = ', '.join(deal['coupons']) if deal['coupons'] else ''
        buy_text = ', '.join(deal['buy']) if deal['buy'] else ''
        copy_text = f"{deal['name']} - Sale: {sale_text} | Coupons: {coupon_text} | Buy: {buy_text}"

        double_rows += f'''
        <div class="deal-row" data-type="double" data-copy-text="{escape_js_string(copy_text)}">
            <span class="deal-badge badge-double">Double</span>
            <div class="deal-content">
                <div class="deal-title">{deal['name']}</div>
                <div class="stack-deal-content">
                    <div class="stack-section">
                        <span class="stack-label">Sale:</span>
                        <span class="stack-items">{sale_text}</span>
                    </div>
                    <div class="stack-section">
                        <span class="stack-label">Coupons:</span>
                        <span class="stack-items">{coupon_text}</span>
                    </div>
                    <div class="stack-section">
                        <span class="stack-label">Buy:</span>
                        <span class="stack-items">{buy_text}</span>
                    </div>
                </div>
            </div>
            <div class="deal-actions">
                <button class="copy-btn" aria-label="Copy deal to clipboard">Copy</button>
            </div>
        </div>'''

    # Build BOGO rows
    bogo_rows = ""
    for category, items in content['bogo_deals'].items():
        if not items:
            continue
        bogo_rows += f'<div class="category-divider">{category}</div>'
        for item in items:
            parts = item.split('—')
            name = parts[0].strip() if parts else item
            details = ' — '.join(parts[1:]).strip() if len(parts) > 1 else ''
            copy_text = item

            bogo_rows += f'''
            <div class="deal-row" data-type="bogo" data-copy-text="{escape_js_string(copy_text)}">
                <span class="deal-badge badge-bogo">BOGO</span>
                <div class="deal-content">
                    <div class="deal-title">{name}</div>
                    <div class="deal-details">{details}</div>
                </div>
                <div class="deal-actions">
                    <button class="copy-btn" aria-label="Copy deal to clipboard">Copy</button>
                </div>
            </div>'''

    # Build Digital Coupons rows
    coupon_rows = ""
    for category, items in content['digital_coupons'].items():
        if not items:
            continue
        coupon_rows += f'<div class="category-divider">{category}</div>'
        for item in items:
            parts = item.split('—')
            name = parts[0].strip() if parts else item
            details = ' — '.join(parts[1:]).strip() if len(parts) > 1 else ''
            copy_text = item

            coupon_rows += f'''
            <div class="deal-row" data-type="coupon" data-copy-text="{escape_js_string(copy_text)}">
                <span class="deal-badge badge-coupon">Coupon</span>
                <div class="deal-content">
                    <div class="deal-title">{name}</div>
                    <div class="deal-details">{details}</div>
                </div>
                <div class="deal-actions">
                    <button class="copy-btn" aria-label="Copy deal to clipboard">Copy</button>
                </div>
            </div>'''

    # Counts
    triple_count = len(content['triple_stacks'])
    double_count = len(content['double_stacks'])
    bogo_count = sum(len(items) for items in content['bogo_deals'].values())
    coupon_count = sum(len(items) for items in content['digital_coupons'].values())

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="SquatchyStack - Your friendly deal hunter for Publix savings. Find triple stacks, double stacks, BOGO deals, and digital coupons.">
    <title>SquatchyStack - Stack Smarter, Save Bigger</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <!-- Sasquatch Watermark -->
    <svg class="squatch-watermark" viewBox="0 0 400 500" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <ellipse cx="200" cy="320" rx="95" ry="130" fill="#00d084"/>
        <ellipse cx="200" cy="145" rx="75" ry="85" fill="#00d084"/>
        <ellipse cx="200" cy="185" rx="40" ry="50" fill="#00875a"/>
        <rect x="172" y="158" width="12" height="18" rx="2" fill="#00ff9d"/>
        <rect x="188" y="155" width="12" height="22" rx="2" fill="#00ff9d"/>
        <rect x="208" y="158" width="12" height="18" rx="2" fill="#00ff9d"/>
        <ellipse cx="160" cy="110" rx="18" ry="12" fill="#00ff9d"/>
        <ellipse cx="240" cy="110" rx="18" ry="12" fill="#00ff9d"/>
        <ellipse cx="160" cy="110" rx="10" ry="6" fill="#00ffaa"/>
        <ellipse cx="240" cy="110" rx="10" ry="6" fill="#00ffaa"/>
        <ellipse cx="60" cy="210" rx="50" ry="110" fill="#00d084" transform="rotate(-35 60 210)"/>
        <ellipse cx="340" cy="210" rx="50" ry="110" fill="#00d084" transform="rotate(35 340 210)"/>
        <circle cx="20" cy="110" r="40" fill="#00d084"/>
        <circle cx="380" cy="110" r="40" fill="#00d084"/>
        <ellipse cx="145" cy="460" rx="45" ry="90" fill="#00d084"/>
        <ellipse cx="255" cy="460" rx="45" ry="90" fill="#00d084"/>
        <ellipse cx="135" cy="495" rx="55" ry="22" fill="#00875a"/>
        <ellipse cx="265" cy="495" rx="55" ry="22" fill="#00875a"/>
    </svg>

    <!-- Header -->
    <header class="header">
        <div class="header-inner">
            <a href="#" class="brand">
                <svg class="brand-icon" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="50" cy="38" r="28" fill="#00875a"/>
                    <ellipse cx="50" cy="44" rx="20" ry="16" fill="#00d084"/>
                    <ellipse cx="40" cy="38" rx="6" ry="7" fill="white"/>
                    <ellipse cx="60" cy="38" rx="6" ry="7" fill="white"/>
                    <circle cx="41" cy="39" r="3.5" fill="#1a1a1a"/>
                    <circle cx="61" cy="39" r="3.5" fill="#1a1a1a"/>
                    <ellipse cx="50" cy="48" rx="5" ry="4" fill="#004d40"/>
                    <path d="M 40 56 Q 50 64 60 56" stroke="#004d40" stroke-width="2.5" fill="none" stroke-linecap="round"/>
                    <ellipse cx="50" cy="78" rx="22" ry="24" fill="#00875a"/>
                </svg>
                <span class="brand-text">SquatchyStack</span>
            </a>

            <nav class="nav" id="main-nav" role="navigation" aria-label="Main navigation">
                <a href="#" class="nav-link active">Home</a>
                <a href="#deals" class="nav-link">Deals</a>
                <a href="#triple-stacks" class="nav-link">Stacks</a>
                <a href="#about" class="nav-link">About</a>
            </nav>

            <span class="last-updated">Updated Weekly</span>

            <button class="mobile-menu-btn" id="mobile-menu-btn" aria-label="Toggle menu" aria-expanded="false">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="3" y1="6" x2="21" y2="6"></line>
                    <line x1="3" y1="12" x2="21" y2="12"></line>
                    <line x1="3" y1="18" x2="21" y2="18"></line>
                </svg>
            </button>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="hero">
        <div class="hero-content">
            <h1>Stack smarter. <span>Save bigger.</span></h1>
            <p class="hero-subtitle">Your friendly neighborhood deal hunter. Find the best Publix couponing stacks, BOGO deals, and digital coupons all in one place.</p>

            <div class="search-container">
                <svg class="search-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
                <input type="text" id="search-input" class="search-input" placeholder="Search deals, products, brands..." aria-label="Search deals">
                <button class="search-clear" id="search-clear" aria-label="Clear search">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>

            <div class="filter-chips" role="group" aria-label="Filter deals by type">
                <button class="filter-chip" data-filter="triple" tabindex="0">Triple Stack</button>
                <button class="filter-chip" data-filter="double" tabindex="0">Double Stack</button>
                <button class="filter-chip" data-filter="bogo" tabindex="0">BOGO</button>
                <button class="filter-chip" data-filter="coupon" tabindex="0">Digital Coupons</button>
                <button class="filter-chip clear-filter" tabindex="0">Clear All</button>
            </div>
        </div>
    </section>

    <!-- Main Content -->
    <main class="main-content" id="deals">

        <!-- Triple Stacks Section -->
        <section class="deals-section" id="triple-stacks">
            <div class="section-header">
                <div class="section-icon">🏆</div>
                <h2 class="section-title">Triple Stacks</h2>
                <span class="section-count">{triple_count} deals</span>
            </div>
            <div class="deals-list">
                {triple_rows}
            </div>
        </section>

        <!-- Double Stacks Section -->
        <section class="deals-section" id="double-stacks">
            <div class="section-header">
                <div class="section-icon">⭐</div>
                <h2 class="section-title">Double Stacks</h2>
                <span class="section-count">{double_count} deals</span>
            </div>
            <div class="deals-list">
                {double_rows}
            </div>
        </section>

        <!-- BOGO Deals Section -->
        <section class="deals-section" id="bogo-deals">
            <div class="section-header">
                <div class="section-icon">🛒</div>
                <h2 class="section-title">BOGO Deals</h2>
                <span class="section-count">{bogo_count} deals</span>
            </div>
            <div class="deals-list">
                {bogo_rows}
            </div>
        </section>

        <!-- Digital Coupons Section -->
        <section class="deals-section" id="digital-coupons">
            <div class="section-header">
                <div class="section-icon">📱</div>
                <h2 class="section-title">Digital Coupons</h2>
                <span class="section-count">{coupon_count} deals</span>
            </div>
            <div class="deals-list">
                {coupon_rows}
            </div>
        </section>

        <!-- About Section -->
        <section class="about-section" id="about">
            <h2>About SquatchyStack</h2>
            <p>SquatchyStack is your friendly deal-hunting companion, helping you navigate the forest of savings at Publix. We compile the best triple stacks, double stacks, BOGO deals, and digital coupons so you can maximize your savings without the hassle. Remember to clip your digital coupons in the Publix app before heading to the store!</p>
        </section>

    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="footer-inner">
            <div class="footer-brand-section">
                <div class="footer-brand">
                    <svg class="brand-icon" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="36" height="36">
                        <circle cx="50" cy="38" r="28" fill="#00d084"/>
                        <ellipse cx="50" cy="44" rx="20" ry="16" fill="#00ffaa"/>
                        <ellipse cx="40" cy="38" rx="6" ry="7" fill="white"/>
                        <ellipse cx="60" cy="38" rx="6" ry="7" fill="white"/>
                        <circle cx="41" cy="39" r="3.5" fill="#1a1a1a"/>
                        <circle cx="61" cy="39" r="3.5" fill="#1a1a1a"/>
                        <ellipse cx="50" cy="78" rx="22" ry="24" fill="#00d084"/>
                    </svg>
                    <span class="footer-brand-text">SquatchyStack</span>
                </div>
                <p class="footer-tagline">Stack smarter. Save bigger. Your friendly neighborhood deal hunter helping you find the best Publix savings.</p>
                <p class="footer-disclaimer">Not affiliated with Publix Super Markets, Inc. or any retailers mentioned. Deal information is provided for convenience and may change without notice.</p>
            </div>

            <div class="footer-section">
                <h4>Quick Links</h4>
                <ul class="footer-links">
                    <li><a href="#triple-stacks">Triple Stacks</a></li>
                    <li><a href="#double-stacks">Double Stacks</a></li>
                    <li><a href="#bogo-deals">BOGO Deals</a></li>
                    <li><a href="#digital-coupons">Digital Coupons</a></li>
                </ul>
            </div>

            <div class="footer-section">
                <h4>Resources</h4>
                <ul class="footer-links">
                    <li><a href="https://www.publix.com/savings/digital-coupons" target="_blank" rel="noopener">Publix Digital Coupons</a></li>
                    <li><a href="https://www.publix.com/savings/weekly-ad" target="_blank" rel="noopener">Weekly Ad</a></li>
                    <li><a href="#about">About Us</a></li>
                </ul>
            </div>
        </div>

        <div class="footer-bottom">
            <p>&copy; 2025 SquatchyStack. Made with 🦶 for deal hunters everywhere.</p>
        </div>
    </footer>

    <script src="script.js"></script>
</body>
</html>'''

    return html


def main():
    print("=" * 50)
    print("Publix Deals Website Generator")
    print("=" * 50)

    if not DOCX_PATH.exists():
        print(f"\nError: Could not find {DOCX_PATH}")
        print("Make sure Publix_Final.docx is in the same folder as this script.")
        if not CI_MODE:
            input("\nPress Enter to exit...")
        return

    print(f"\nReading: {DOCX_PATH}")
    content = parse_document()

    print(f"Found {len(content['triple_stacks'])} triple stack deals")
    print(f"Found {len(content['double_stacks'])} double stack deals")
    print(f"Found {sum(len(v) for v in content['bogo_deals'].values())} BOGO deals")
    print(f"Found {sum(len(v) for v in content['digital_coupons'].values())} digital coupons")

    # Generate HTML
    print(f"\nGenerating: {OUTPUT_HTML}")
    html = generate_html(content)
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)

    # Generate CSS
    print(f"Generating: {OUTPUT_CSS}")
    css = generate_css()
    with open(OUTPUT_CSS, 'w', encoding='utf-8') as f:
        f.write(css)

    # Generate JS
    print(f"Generating: {OUTPUT_JS}")
    js = generate_js()
    with open(OUTPUT_JS, 'w', encoding='utf-8') as f:
        f.write(js)

    print("\nWebsite generated successfully!")
    print(f"  - {OUTPUT_HTML}")
    print(f"  - {OUTPUT_CSS}")
    print(f"  - {OUTPUT_JS}")

    if not CI_MODE:
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
