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
            # Save last deal from previous section if exists
            if current_deal and current_section in ['triple_stacks', 'double_stacks']:
                content[current_section].append(current_deal)
                current_deal = None
            current_section = 'triple_stacks'
            current_field = None
            continue
        elif 'DOUBLE STACKS' in text.upper():
            # Save last deal from previous section if exists
            if current_deal and current_section in ['triple_stacks', 'double_stacks']:
                content[current_section].append(current_deal)
                current_deal = None
            current_section = 'double_stacks'
            current_field = None
            continue
        elif 'BOGO DEALS' in text.upper():
            # Save last deal from previous section if exists
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
            # Check for field headers
            if text == 'Sale:':
                current_field = 'sale'
            elif text.startswith('Digital Coupon'):
                current_field = 'coupons'
            elif text == 'Buy:':
                current_field = 'buy'
            elif text == 'Why this works:':
                current_field = 'why'
            # List items start with "-", "–" (en dash), "•" (bullet), or spaces
            elif (text.startswith('-') or text.startswith('–') or text.startswith('•') or text.startswith(' ')) and current_deal and current_field:
                item = text.lstrip('-–•  ').strip()
                if current_field == 'why':
                    current_deal['why'] = item
                else:
                    current_deal[current_field].append(item)
            # "Why this works" explanation (no dash, after "Why this works:" header)
            elif current_field == 'why' and current_deal and not text.startswith('-'):
                current_deal['why'] = text
                current_field = None  # Reset so next paragraph is treated as new deal
            # New deal name (not a field header, not a list item, not a "why" continuation)
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
    <title>Squatchy Stacks - Publix Deals</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #0a1f0a;
            min-height: 100vh;
            color: #333;
            overflow-x: hidden;
        }}

        /* Forest Background Container */
        .forest-bg {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 0;
            overflow: hidden;
        }}

        /* Sky gradient */
        .forest-bg::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(180deg,
                #1a0a2e 0%,
                #16213e 15%,
                #1a3a1a 40%,
                #0d260d 70%,
                #051005 100%);
        }}

        /* Moon */
        .moon {{
            position: absolute;
            top: 8%;
            right: 15%;
            width: 80px;
            height: 80px;
            background: radial-gradient(circle, #fffde7 0%, #fff9c4 50%, #ffecb3 100%);
            border-radius: 50%;
            box-shadow: 0 0 60px 20px rgba(255, 253, 231, 0.3), 0 0 100px 40px rgba(255, 253, 231, 0.1);
        }}

        /* Stars */
        .stars {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 40%;
            background-image:
                radial-gradient(2px 2px at 20px 30px, white, transparent),
                radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.8), transparent),
                radial-gradient(1px 1px at 90px 40px, white, transparent),
                radial-gradient(2px 2px at 130px 80px, rgba(255,255,255,0.6), transparent),
                radial-gradient(1px 1px at 160px 120px, white, transparent),
                radial-gradient(2px 2px at 200px 50px, rgba(255,255,255,0.7), transparent),
                radial-gradient(1px 1px at 250px 160px, white, transparent),
                radial-gradient(2px 2px at 300px 90px, rgba(255,255,255,0.5), transparent),
                radial-gradient(1px 1px at 350px 30px, white, transparent),
                radial-gradient(2px 2px at 400px 100px, rgba(255,255,255,0.8), transparent);
            background-size: 400px 200px;
            animation: twinkle 4s ease-in-out infinite;
        }}

        @keyframes twinkle {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}

        /* Distant mountains/hills */
        .hills {{
            position: absolute;
            bottom: 20%;
            left: 0;
            right: 0;
            height: 300px;
        }}

        .hills::before {{
            content: '';
            position: absolute;
            bottom: 0;
            left: -10%;
            width: 60%;
            height: 100%;
            background: #0d1f0d;
            border-radius: 50% 50% 0 0;
            transform: scaleX(1.5);
        }}

        .hills::after {{
            content: '';
            position: absolute;
            bottom: 0;
            right: -10%;
            width: 70%;
            height: 80%;
            background: #0a1a0a;
            border-radius: 50% 50% 0 0;
            transform: scaleX(1.4);
        }}

        /* Pine Trees */
        .trees {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 45%;
            display: flex;
            justify-content: space-around;
            align-items: flex-end;
            padding: 0 20px;
        }}

        .tree {{
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}

        .tree-back {{ opacity: 0.3; transform: scale(0.6); margin-bottom: -50px; }}
        .tree-mid {{ opacity: 0.5; transform: scale(0.8); margin-bottom: -30px; }}
        .tree-front {{ opacity: 0.8; }}

        /* GIANT ROARING SASQUATCH */
        .giant-squatch {{
            position: absolute;
            bottom: 5%;
            left: 50%;
            transform: translateX(-50%);
            width: 600px;
            height: 700px;
            opacity: 0.15;
            z-index: 1;
        }}

        /* Mist/fog effect */
        .mist {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 30%;
            background: linear-gradient(180deg, transparent 0%, rgba(10, 31, 10, 0.5) 50%, rgba(10, 31, 10, 0.9) 100%);
            pointer-events: none;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            position: relative;
            z-index: 1;
        }}

        header {{
            text-align: center;
            padding: 30px 20px 40px;
            color: white;
        }}

        .mascot {{
            width: 150px;
            height: 150px;
            margin: 0 auto 20px;
            animation: bounce 3s ease-in-out infinite;
        }}

        .mascot-small {{
            width: 80px;
            height: 80px;
            margin: 0 auto 15px;
            animation: bounce 3s ease-in-out infinite;
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
        }}

        .mascot-small svg {{
            width: 100%;
            height: 100%;
        }}

        @keyframes bounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-10px); }}
        }}

        .logo-text {{
            font-family: 'Fredoka', sans-serif;
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #90EE90 0%, #FFD700 50%, #FFA500 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: none;
            filter: drop-shadow(3px 3px 6px rgba(0,0,0,0.4));
            margin-bottom: 8px;
        }}

        header .tagline {{
            font-family: 'Fredoka', sans-serif;
            font-size: 1.3rem;
            color: #98FB98;
            font-weight: 500;
            margin-bottom: 20px;
        }}

        .valid-dates {{
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            color: #1a3d15;
            padding: 12px 24px;
            border-radius: 50px;
            display: inline-block;
            font-weight: 600;
            font-family: 'Fredoka', sans-serif;
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        }}

        nav {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 15px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            position: sticky;
            top: 10px;
            z-index: 100;
            border: 1px solid rgba(255,255,255,0.2);
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
            padding: 12px 24px;
            background: linear-gradient(135deg, #2d5a27 0%, #1a3d15 100%);
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            font-family: 'Fredoka', sans-serif;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(45, 90, 39, 0.3);
        }}

        nav a:hover {{
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 6px 20px rgba(45, 90, 39, 0.4);
        }}

        section {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.15);
            border: 1px solid rgba(255,255,255,0.2);
        }}

        section h2 {{
            font-family: 'Fredoka', sans-serif;
            color: #1a3d15;
            font-size: 2rem;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 4px solid;
            border-image: linear-gradient(90deg, #2d5a27, #FFD700) 1;
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        section h2::before {{
            font-size: 1.5rem;
        }}

        #triple-stacks h2::before {{ content: '🏆'; }}
        #double-stacks h2::before {{ content: '⭐'; }}
        #bogo-deals h2::before {{ content: '🛒'; }}
        #digital-coupons h2::before {{ content: '📱'; }}

        .stack-deal {{
            background: linear-gradient(135deg, #f0fff0 0%, #e8f5e9 100%);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            border-left: 6px solid #2d5a27;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            transition: transform 0.3s ease;
        }}

        .stack-deal:hover {{
            transform: translateX(5px);
        }}

        .stack-deal h4 {{
            font-family: 'Fredoka', sans-serif;
            color: #1a3d15;
            font-size: 1.3rem;
            margin-bottom: 18px;
        }}

        .stack-deal .sale-items,
        .stack-deal .coupons,
        .stack-deal .buy-list,
        .stack-deal .why-works {{
            margin-bottom: 15px;
        }}

        .stack-deal strong {{
            color: #2d5a27;
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
        }}

        .stack-deal ul {{
            list-style: none;
            padding-left: 0;
        }}

        .stack-deal li {{
            padding: 8px 0 8px 28px;
            position: relative;
        }}

        .stack-deal li:before {{
            content: "🌿";
            position: absolute;
            left: 0;
            font-size: 0.9rem;
        }}

        .why-works {{
            background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%);
            padding: 16px 20px;
            border-radius: 12px;
            border-left: 4px solid #FFD700;
        }}

        .why-works strong {{
            color: #856404 !important;
        }}

        .bogo-grid, .coupon-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
        }}

        .deal-card {{
            background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
            border-radius: 16px;
            padding: 20px;
            transition: all 0.3s ease;
            border: 2px solid #e9ecef;
            position: relative;
            overflow: hidden;
        }}

        .deal-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #2d5a27, #90EE90, #FFD700);
        }}

        .deal-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.15);
            border-color: #2d5a27;
        }}

        .deal-card h5 {{
            font-family: 'Fredoka', sans-serif;
            color: #1a3d15;
            font-size: 1.1rem;
            margin-bottom: 12px;
            margin-top: 8px;
        }}

        .deal-card .offer {{
            background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
            color: white;
            padding: 6px 14px;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 10px;
            box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3);
        }}

        .deal-card .savings {{
            color: #2d5a27;
            font-weight: 700;
            font-size: 1rem;
        }}

        .deal-card .valid {{
            color: #6c757d;
            font-size: 0.85rem;
            margin-top: 8px;
        }}

        .coupon-card {{
            background: linear-gradient(145deg, #fffef5 0%, #fff9e6 100%);
            border: 2px dashed #2d5a27;
        }}

        .coupon-card::before {{
            background: linear-gradient(90deg, #FFD700, #FFA500, #2d5a27);
        }}

        .coupon-card .savings-amount {{
            background: linear-gradient(135deg, #2d5a27 0%, #1a3d15 100%);
            color: white;
            padding: 6px 14px;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 10px;
        }}

        .coupon-card .description {{
            color: #555;
            font-size: 0.9rem;
            margin-top: 8px;
            line-height: 1.5;
        }}

        .coupon-card .expires {{
            color: #dc3545;
            font-size: 0.85rem;
            margin-top: 8px;
            font-weight: 600;
        }}

        .category-header {{
            background: linear-gradient(135deg, #2d5a27 0%, #1a3d15 100%);
            padding: 14px 24px;
            border-radius: 12px;
            margin: 30px 0 20px 0;
            font-weight: 600;
            color: white;
            font-family: 'Fredoka', sans-serif;
            font-size: 1.1rem;
            box-shadow: 0 4px 12px rgba(45, 90, 39, 0.3);
        }}

        footer {{
            text-align: center;
            padding: 40px 20px;
            color: #98FB98;
        }}

        footer p {{
            margin-bottom: 8px;
        }}

        .footer-squatch {{
            font-size: 2rem;
            margin-bottom: 10px;
        }}

        @media (max-width: 768px) {{
            .logo-text {{
                font-size: 2.5rem;
            }}

            .mascot {{
                width: 120px;
                height: 120px;
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
                border-radius: 16px;
            }}
        }}
    </style>
</head>
<body>
    <!-- FOREST BACKGROUND -->
    <div class="forest-bg">
        <div class="stars"></div>
        <div class="moon"></div>
        <div class="hills"></div>

        <!-- GIANT ROARING SASQUATCH SILHOUETTE -->
        <svg class="giant-squatch" viewBox="0 0 400 500" xmlns="http://www.w3.org/2000/svg">
            <!-- Muscular Body -->
            <ellipse cx="200" cy="320" rx="90" ry="120" fill="#0d1a0d"/>
            <!-- Head tilted back roaring -->
            <ellipse cx="200" cy="140" rx="70" ry="80" fill="#0d1a0d"/>
            <!-- Open roaring mouth -->
            <ellipse cx="200" cy="180" rx="35" ry="45" fill="#050a05"/>
            <!-- Teeth -->
            <rect x="175" y="155" width="10" height="15" rx="2" fill="#1a2a1a"/>
            <rect x="190" y="152" width="10" height="18" rx="2" fill="#1a2a1a"/>
            <rect x="205" y="155" width="10" height="15" rx="2" fill="#1a2a1a"/>
            <!-- Fierce eyes -->
            <ellipse cx="165" cy="110" rx="15" ry="10" fill="#1a3a1a"/>
            <ellipse cx="235" cy="110" rx="15" ry="10" fill="#1a3a1a"/>
            <!-- Glowing eye effect -->
            <ellipse cx="165" cy="110" rx="8" ry="5" fill="#2a4a2a"/>
            <ellipse cx="235" cy="110" rx="8" ry="5" fill="#2a4a2a"/>
            <!-- Raised arms in power pose -->
            <ellipse cx="70" cy="200" rx="45" ry="100" fill="#0d1a0d" transform="rotate(-30 70 200)"/>
            <ellipse cx="330" cy="200" rx="45" ry="100" fill="#0d1a0d" transform="rotate(30 330 200)"/>
            <!-- Fists -->
            <circle cx="30" cy="120" r="35" fill="#0d1a0d"/>
            <circle cx="370" cy="120" r="35" fill="#0d1a0d"/>
            <!-- Legs -->
            <ellipse cx="150" cy="450" rx="40" ry="80" fill="#0d1a0d"/>
            <ellipse cx="250" cy="450" rx="40" ry="80" fill="#0d1a0d"/>
            <!-- Big feet -->
            <ellipse cx="140" cy="490" rx="50" ry="20" fill="#0a150a"/>
            <ellipse cx="260" cy="490" rx="50" ry="20" fill="#0a150a"/>
            <!-- Fur texture lines -->
            <path d="M 130 280 Q 140 260 150 280" stroke="#1a2a1a" stroke-width="3" fill="none"/>
            <path d="M 180 270 Q 190 250 200 270" stroke="#1a2a1a" stroke-width="3" fill="none"/>
            <path d="M 230 280 Q 240 260 250 280" stroke="#1a2a1a" stroke-width="3" fill="none"/>
            <!-- Chest fur -->
            <path d="M 160 300 L 200 340 L 240 300" stroke="#1a2a1a" stroke-width="4" fill="none"/>
        </svg>

        <div class="mist"></div>
    </div>

    <div class="container">
        <header>
            <!-- Small mascot icon -->
            <div class="mascot-small">
                <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="50" cy="40" r="25" fill="#5D4037"/>
                    <ellipse cx="50" cy="45" rx="18" ry="15" fill="#8D6E63"/>
                    <ellipse cx="42" cy="40" rx="5" ry="6" fill="white"/>
                    <ellipse cx="58" cy="40" rx="5" ry="6" fill="white"/>
                    <circle cx="43" cy="41" r="3" fill="#1a1a1a"/>
                    <circle cx="59" cy="41" r="3" fill="#1a1a1a"/>
                    <ellipse cx="50" cy="48" rx="4" ry="3" fill="#4E342E"/>
                    <path d="M 42 55 Q 50 62 58 55" stroke="#4E342E" stroke-width="2" fill="none" stroke-linecap="round"/>
                    <ellipse cx="50" cy="75" rx="20" ry="22" fill="#5D4037"/>
                </svg>
            </div>
            <h1 class="logo-text">Squatchy Stacks</h1>
            <p class="tagline">Your Friendly Neighborhood Deal Hunter</p>
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
            <div class="footer-squatch">🦶</div>
            <p><strong>Squatchy Stacks</strong> - Helping you save big on Publix deals!</p>
            <p>Clip digital coupons in the Publix app before shopping</p>
            <p style="margin-top: 15px; font-size: 0.85rem; opacity: 0.7;">squatchystacks.com</p>
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
