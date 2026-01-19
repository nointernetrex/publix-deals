"""
Publix Deals Website Generator
Double-click update_website.bat to run this script.
It reads Publix_Final.docx and generates index.html for GitHub Pages.
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
OUTPUT_PATH = SCRIPT_DIR / "index.html"


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
            current_section = 'triple_stacks'
            continue
        elif 'DOUBLE STACKS' in text.upper():
            current_section = 'double_stacks'
            continue
        elif 'BOGO DEALS' in text.upper():
            current_section = 'bogo_deals'
            continue
        elif 'DIGITAL COUPONS' in text.upper():
            current_section = 'digital_coupons'
            continue

        # Handle Triple and Double Stacks
        if current_section in ['triple_stacks', 'double_stacks']:
            # New deal starts with a name containing ":"
            if ':' in text and not text.startswith('-') and not text.startswith('Sale') and not text.startswith('Digital') and not text.startswith('Buy') and not text.startswith('Why'):
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
            elif text.startswith('Sale:'):
                current_field = 'sale'
            elif text.startswith('Digital Coupon'):
                current_field = 'coupons'
            elif text.startswith('Buy:'):
                current_field = 'buy'
            elif text.startswith('Why this works:'):
                current_field = 'why'
            elif text.startswith('-') and current_deal and current_field:
                item = text.lstrip('- ').strip()
                if current_field == 'why':
                    current_deal['why'] = item
                else:
                    current_deal[current_field].append(item)
            elif current_field == 'why' and current_deal and not text.startswith('-'):
                current_deal['why'] = text

        # Handle BOGO Deals and Digital Coupons (categorized lists)
        elif current_section in ['bogo_deals', 'digital_coupons']:
            # Category headers (single words or short phrases without dashes)
            if not text.startswith('-') and len(text) < 50 and not any(c in text for c in ['$', '—', 'Save', 'Buy', 'Free']):
                current_category = text
                if current_category not in content[current_section]:
                    content[current_section][current_category] = []
            # Deal items
            elif text.startswith('-') and current_category:
                item = text.lstrip('- ').strip()
                content[current_section][current_category].append(item)

    # Don't forget the last deal
    if current_deal and current_section in ['triple_stacks', 'double_stacks']:
        content[current_section].append(current_deal)

    return content


def parse_bogo_item(item):
    """Parse a BOGO deal line into components."""
    # Format: "Product Name — Buy 1 Get 1 Free — Save Up To $X.XX — Valid X/XX - X/XX"
    parts = item.split('—')
    result = {
        'name': parts[0].strip() if len(parts) > 0 else item,
        'offer': parts[1].strip() if len(parts) > 1 else 'Buy 1 Get 1 Free',
        'savings': parts[2].strip() if len(parts) > 2 else '',
        'valid': parts[3].strip() if len(parts) > 3 else ''
    }
    return result


def parse_coupon_item(item):
    """Parse a digital coupon line into components."""
    # Format: "Brand — Save $X.XX — Description — Expires XX/XX"
    parts = item.split('—')
    result = {
        'name': parts[0].strip() if len(parts) > 0 else item,
        'savings': parts[1].strip() if len(parts) > 1 else '',
        'description': parts[2].strip() if len(parts) > 2 else '',
        'expires': parts[3].strip() if len(parts) > 3 else ''
    }
    return result


def generate_html(content):
    """Generate the HTML website from parsed content."""

    # Generate Triple Stacks HTML
    triple_stacks_html = ""
    for deal in content['triple_stacks']:
        sale_items = ''.join(f'<li>{item}</li>' for item in deal['sale'])
        coupon_items = ''.join(f'<li>{item}</li>' for item in deal['coupons'])
        buy_items = ''.join(f'<li>{item}</li>' for item in deal['buy'])

        triple_stacks_html += f'''
            <div class="stack-deal">
                <h4>{deal['name']}</h4>
                <div class="sale-items">
                    <strong>Sale:</strong>
                    <ul>{sale_items}</ul>
                </div>
                <div class="coupons">
                    <strong>Digital Coupons:</strong>
                    <ul>{coupon_items}</ul>
                </div>
                <div class="buy-list">
                    <strong>Buy:</strong>
                    <ul>{buy_items}</ul>
                </div>
                <div class="why-works">
                    <strong>Why this works:</strong> {deal['why']}
                </div>
            </div>
        '''

    # Generate Double Stacks HTML
    double_stacks_html = ""
    for deal in content['double_stacks']:
        sale_items = ''.join(f'<li>{item}</li>' for item in deal['sale'])
        coupon_items = ''.join(f'<li>{item}</li>' for item in deal['coupons'])
        buy_items = ''.join(f'<li>{item}</li>' for item in deal['buy'])

        double_stacks_html += f'''
            <div class="stack-deal">
                <h4>{deal['name']}</h4>
                <div class="sale-items">
                    <strong>Sale:</strong>
                    <ul>{sale_items}</ul>
                </div>
                <div class="coupons">
                    <strong>Digital Coupon:</strong>
                    <ul>{coupon_items}</ul>
                </div>
                <div class="buy-list">
                    <strong>Buy:</strong>
                    <ul>{buy_items}</ul>
                </div>
            </div>
        '''

    # Generate BOGO Deals HTML
    bogo_html = ""
    for category, items in content['bogo_deals'].items():
        if not items:
            continue
        cards = ""
        for item in items:
            parsed = parse_bogo_item(item)
            savings_html = f'<div class="savings">{parsed["savings"]}</div>' if parsed["savings"] else ''
            cards += f'''
                <div class="deal-card">
                    <h5>{parsed['name']}</h5>
                    <span class="offer">{parsed['offer']}</span>
                    {savings_html}
                    <div class="valid">{parsed['valid']}</div>
                </div>
            '''
        bogo_html += f'''
            <div class="category-header">{category}</div>
            <div class="bogo-grid">{cards}</div>
        '''

    # Generate Digital Coupons HTML
    coupons_html = ""
    for category, items in content['digital_coupons'].items():
        if not items:
            continue
        cards = ""
        for item in items:
            parsed = parse_coupon_item(item)
            desc_html = f'<div class="description">{parsed["description"]}</div>' if parsed["description"] else ''
            cards += f'''
                <div class="deal-card coupon-card">
                    <h5>{parsed['name']}</h5>
                    <span class="savings-amount">{parsed['savings']}</span>
                    {desc_html}
                    <div class="expires">{parsed['expires']}</div>
                </div>
            '''
        coupons_html += f'''
            <div class="category-header">{category}</div>
            <div class="coupon-grid">{cards}</div>
        '''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Publix Couponing Cheat Sheet</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a5f2a 0%, #2d8f47 100%);
            min-height: 100vh;
            color: #333;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        header {{
            text-align: center;
            padding: 40px 20px;
            color: white;
        }}

        header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}

        .valid-dates {{
            background: #fff3cd;
            color: #856404;
            padding: 10px 20px;
            border-radius: 8px;
            display: inline-block;
            margin-top: 15px;
            font-weight: 600;
        }}

        nav {{
            background: white;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            position: sticky;
            top: 10px;
            z-index: 100;
        }}

        nav ul {{
            list-style: none;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
        }}

        nav a {{
            display: block;
            padding: 10px 20px;
            background: #1a5f2a;
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}

        nav a:hover {{
            background: #2d8f47;
            transform: translateY(-2px);
        }}

        section {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}

        section h2 {{
            color: #1a5f2a;
            font-size: 1.8rem;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #1a5f2a;
        }}

        .stack-deal {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 5px solid #1a5f2a;
        }}

        .stack-deal h4 {{
            color: #1a5f2a;
            font-size: 1.2rem;
            margin-bottom: 15px;
        }}

        .stack-deal .sale-items,
        .stack-deal .coupons,
        .stack-deal .buy-list,
        .stack-deal .why-works {{
            margin-bottom: 15px;
        }}

        .stack-deal strong {{
            color: #333;
            display: block;
            margin-bottom: 8px;
        }}

        .stack-deal ul {{
            list-style: none;
            padding-left: 0;
        }}

        .stack-deal li {{
            padding: 5px 0 5px 20px;
            position: relative;
        }}

        .stack-deal li:before {{
            content: "\\2022";
            color: #2d8f47;
            font-weight: bold;
            position: absolute;
            left: 0;
        }}

        .why-works {{
            background: #e8f5e9;
            padding: 12px 15px;
            border-radius: 8px;
            font-style: italic;
        }}

        .bogo-grid, .coupon-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 15px;
        }}

        .deal-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            transition: all 0.3s ease;
            border: 1px solid #e9ecef;
        }}

        .deal-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}

        .deal-card h5 {{
            color: #1a5f2a;
            font-size: 1rem;
            margin-bottom: 8px;
        }}

        .deal-card .offer {{
            background: #ff6b35;
            color: white;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 8px;
        }}

        .deal-card .savings {{
            color: #28a745;
            font-weight: 600;
            font-size: 0.95rem;
        }}

        .deal-card .valid {{
            color: #6c757d;
            font-size: 0.85rem;
            margin-top: 5px;
        }}

        .coupon-card {{
            background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
            border: 2px dashed #1a5f2a;
        }}

        .coupon-card .savings-amount {{
            background: #28a745;
            color: white;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 8px;
        }}

        .coupon-card .description {{
            color: #555;
            font-size: 0.9rem;
            margin-top: 8px;
        }}

        .coupon-card .expires {{
            color: #dc3545;
            font-size: 0.8rem;
            margin-top: 5px;
            font-weight: 500;
        }}

        .category-header {{
            background: #e8f5e9;
            padding: 12px 20px;
            border-radius: 8px;
            margin: 25px 0 15px 0;
            font-weight: 600;
            color: #1a5f2a;
        }}

        footer {{
            text-align: center;
            padding: 30px;
            color: white;
        }}

        @media (max-width: 768px) {{
            header h1 {{
                font-size: 1.8rem;
            }}

            nav ul {{
                flex-direction: column;
                align-items: center;
            }}

            .bogo-grid, .coupon-grid {{
                grid-template-columns: 1fr;
            }}

            section {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Publix Couponing Cheat Sheet</h1>
            <p>Your Complete Guide to Saving Big</p>
            <div class="valid-dates">Updated Weekly</div>
        </header>

        <nav>
            <ul>
                <li><a href="#triple-stacks">Triple Stacks</a></li>
                <li><a href="#double-stacks">Double Stacks</a></li>
                <li><a href="#bogo-deals">BOGO Deals</a></li>
                <li><a href="#digital-coupons">Digital Coupons</a></li>
            </ul>
        </nav>

        <section id="triple-stacks">
            <h2>Triple Stacks (Checkout-Safe)</h2>
            {triple_stacks_html}
        </section>

        <section id="double-stacks">
            <h2>Double Stacks (Specific)</h2>
            {double_stacks_html}
        </section>

        <section id="bogo-deals">
            <h2>BOGO Deals - Buy One Get One Free</h2>
            {bogo_html}
        </section>

        <section id="digital-coupons">
            <h2>Digital Coupons</h2>
            {coupons_html}
        </section>

        <footer>
            <p>Data sourced from Publix Weekly Ad</p>
            <p>Clip digital coupons in the Publix app before shopping!</p>
        </footer>
    </div>

    <script>
        document.querySelectorAll('nav a').forEach(anchor => {{
            anchor.addEventListener('click', function(e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }});
        }});
    </script>
</body>
</html>
'''
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

    print(f"\nGenerating: {OUTPUT_PATH}")
    html = generate_html(content)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print("\nWebsite generated successfully!")
    print(f"Output: {OUTPUT_PATH}")
    if not CI_MODE:
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
