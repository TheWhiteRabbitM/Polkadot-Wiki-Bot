"""
Polkadot Wiki Bot
Lets users browse and search the official Polkadot Wiki directly from Telegram
using interactive inline buttons.

Created by @thewhiterabbitM  —  x.com/thewhiterabbitM
"""

import os
import html
import re
import logging

from dotenv import load_dotenv
load_dotenv()

import requests
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION  —  edit or set via environment variables
# ══════════════════════════════════════════════════════════════════════════════
BOT_TOKEN       = os.getenv('WIKI_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE').strip()
WIKI_BASE       = "https://wiki.polkadot.network/docs/"
REQUEST_TIMEOUT = 15     # seconds
MAX_PREVIEW     = 500    # characters shown in Telegram before "Read more"

# ══════════════════════════════════════════════════════════════════════════════
#  NAVIGATION TREE  —  (section → topics)
#  slug  = last part of the wiki URL, e.g. "learn-accounts"
#          → https://wiki.polkadot.network/docs/learn-accounts
# ══════════════════════════════════════════════════════════════════════════════
SECTIONS: dict[str, dict] = {
    'learn': {
        'emoji': '📚',
        'label': 'Learn',
        'topics': [
            ('learn-architecture',                      'Architecture'),
            ('learn-accounts',                          'Accounts'),
            ('learn-DOT',                               'DOT Token'),
            ('learn-consensus',                         'Consensus'),
            ('learn-governance',                        'Governance'),
            ('learn-parachains',                        'Parachains'),
            ('learn-xcm',                               'Cross-Chain Messaging (XCM)'),
            ('learn-staking',                           'Staking'),
            ('learn-nominator',                         'Nominators'),
            ('learn-validator',                         'Validators'),
            ('learn-bridges',                           'Bridges'),
            ('learn-cryptography',                      'Cryptography'),
            ('learn-transaction-fees',                  'Transaction Fees'),
            ('learn-identity',                          'Identity'),
            ('learn-treasury',                          'Treasury'),
        ],
    },
    'build': {
        'emoji': '🔧',
        'label': 'Build',
        'topics': [
            ('build-index',                             'Build Index'),
            ('build-smart-contracts',                   'Smart Contracts'),
            ('build-parachains',                        'Parachain Development'),
            ('build-pdk',                               'Parachain Dev Kit (PDK)'),
            ('build-tools-index',                       'Tools & Libraries'),
            ('build-integration-guide',                 'Integration Guide'),
            ('build-node-management',                   'Node Management'),
            ('build-protocol-info',                     'Protocol Info'),
            ('build-ss58-registry',                     'SS58 Registry'),
        ],
    },
    'maintain': {
        'emoji': '⚙️',
        'label': 'Maintain',
        'topics': [
            ('maintain-sync',                           'Sync a Node'),
            ('maintain-guides-how-to-validate-polkadot','Become a Validator'),
            ('maintain-guides-how-to-nominate-polkadot','Nominate (Staking)'),
            ('maintain-guides-how-to-join-council',     'Join the Council'),
            ('maintain-guides-democracy',               'Democracy / Referenda'),
            ('maintain-errors',                         'Common Errors'),
        ],
    },
    'general': {
        'emoji': '🌐',
        'label': 'General',
        'topics': [
            ('general/getting-started',                 'Getting Started'),
            ('general/web3-and-polkadot',               'Web3 & Polkadot'),
            ('general/polkadot-direction',              'Polkadot Direction'),
            ('general/fundamentals',                    'Fundamentals'),
            ('general/community',                       'Community'),
            ('general/contributing',                    'How to Contribute'),
            ('general/faq',                             'FAQ'),
            ('general/scams',                           'Stay Safe (Scams)'),
            ('general/funding',                         'Grants & Funding'),
        ],
    },
}

# ══════════════════════════════════════════════════════════════════════════════
#  LOGGING
# ══════════════════════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
#  WIKI FETCHER
# ══════════════════════════════════════════════════════════════════════════════
def clean_text(text: str) -> str:
    """
    Clean extracted text by removing Docusaurus UI elements and formatting.
    """
    # Remove Docusaurus utility phrases
    noise_patterns = [
        r'Copy page\s*',
        r'View page in Markdown\s*',
        r'Download page in Markdown\s*',
        r'Open in ChatGPT\s*',
        r'Open in Claude\s*',
        r'Edit this page\s*',
        r'Table of contents\s*',
        r'On this page\s*',
        r'Jump to top\s*',
        r'Â¶',  # Special character that appears as ¶
        r'¶\s*',  # Paragraph symbol
        r'\s*¶\s*',
        r'\[.*?\]',  # Remove bracket references like [1], [2]
        r'^\d+\s+',  # Remove leading numbers
        r'\s+',  # Normalize whitespace
    ]
    
    for pattern in noise_patterns:
        text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
    
    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def fetch_article(slug: str) -> tuple[str, str]:
    """
    Fetch a wiki article and return (clean_preview_text, canonical_url).
    Extracts main content, removes UI elements, and creates readable preview.
    """
    url = f"{WIKI_BASE}{slug}"
    try:
        resp = requests.get(
            url, timeout=REQUEST_TIMEOUT,
            headers={'User-Agent': 'Mozilla/5.0 PolkadotWikiBot/1.0'},
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Remove ALL noise elements including Docusaurus UI
        for tag in soup.find_all([
            'nav', 'footer', 'aside', 'script', 'style', 'header', 'form',
            'button', 'svg', 'path', 'g',  # Remove icons and buttons
            '.theme-doc-toc', '.table-of-contents', '.docSidebarContainer',
            '.theme-doc-sidebar-menu', '.breadcrumbs', '.pagination-nav'
        ]):
            tag.decompose()
        
        # Also remove elements by class names commonly used for UI
        for class_name in [
            'theme-doc-toc', 'table-of-contents', 'docSidebarContainer',
            'theme-doc-sidebar-menu', 'breadcrumbs', 'pagination-nav',
            'theme-edit-this-page', 'theme-doc-footer', 'theme-doc-version-badge'
        ]:
            for tag in soup.find_all(class_=class_name):
                tag.decompose()

        # Get main content area - try multiple selectors
        body = (
            soup.find('article') or
            soup.find(class_='theme-doc-markdown') or
            soup.find(class_='markdown') or
            soup.find(role='main') or
            soup.find('main')
        )
        
        if body:
            raw = body.get_text(separator=' ', strip=True)
        else:
            raw = soup.get_text(separator=' ', strip=True)
        
        # Clean the text
        text = clean_text(raw)
        
        # Truncate intelligently
        if len(text) > MAX_PREVIEW:
            # Try to end at a sentence
            truncated = text[:MAX_PREVIEW]
            last_sentence = truncated.rfind('.')
            if last_sentence > MAX_PREVIEW * 0.7:  # If we have a good sentence ending
                text = truncated[:last_sentence + 1] + '..'
            else:
                text = truncated.rsplit(' ', 1)[0] + '…'

        return text or '📄 Article available. Tap "Read Full Article" to view.', url

    except requests.exceptions.ConnectionError:
        return '⚠️ No internet connection.', url
    except requests.exceptions.Timeout:
        return '⚠️ Request timed out. Try again.', url
    except Exception as e:
        logger.warning(f"fetch_article({slug}): {e}")
        return '⚠️ Could not load preview. Tap "Read full article" to open the wiki.', url


# ══════════════════════════════════════════════════════════════════════════════
#  KEYBOARD BUILDERS
# ══════════════════════════════════════════════════════════════════════════════
def _btn(label: str, data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(label, callback_data=data)


def _url_btn(label: str, url: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(label, url=url)


def kb_main_menu() -> InlineKeyboardMarkup:
    """Build the main menu keyboard with enhanced styling"""
    rows = []
    # Add header row
    rows.append([_btn("📖 BROWSE SECTIONS", "noop")])
    
    for key, sec in SECTIONS.items():
        rows.append([_btn(f"{sec['emoji']} {sec['label']}", f"section:{key}")])
    
    # Quick actions row
    rows.append([_url_btn("🔗 Open Wiki", "https://wiki.polkadot.network")])
    rows.append([
        _btn("🔍 Search", "search_prompt"),
        _btn("ℹ️ About", "about")
    ])
    return InlineKeyboardMarkup(rows)


def kb_section(section_key: str) -> InlineKeyboardMarkup:
    """Build section menu with enhanced layout"""
    topics = SECTIONS[section_key]['topics']
    sec = SECTIONS[section_key]
    rows = []
    
    # Section header
    rows.append([_btn(f"{sec['emoji']} {sec['label']} Topics", "noop")])
    
    # Topics - 2 per row for compactness
    for i in range(0, len(topics), 2):
        pair = topics[i:i + 2]
        rows.append([
            _btn(label, f"topic:{section_key}:{slug}")
            for slug, label in pair
        ])
    
    # Navigation
    rows.append([_btn("◀️ Back to Menu", 'back:main')])
    return InlineKeyboardMarkup(rows)


def kb_article(section_key: str, slug: str) -> InlineKeyboardMarkup:
    """Build article view keyboard"""
    url = f"{WIKI_BASE}{slug}"
    return InlineKeyboardMarkup([
        [_url_btn('📖 Read Full Article', url)],
        [_btn('◀️ Back to Section', f"section:{section_key}"),
         _btn('🏠 Main Menu', 'back:main')],
    ])


def kb_search_results(results: list) -> InlineKeyboardMarkup:
    """Build search results keyboard"""
    rows = [
        [_btn(f"{SECTIONS[sk]['emoji']} {label}", f"topic:{sk}:{slug}")]
        for sk, slug, label in results
    ]
    rows.append([_btn('🏠 Back to Menu', 'back:main')])
    return InlineKeyboardMarkup(rows)


# ══════════════════════════════════════════════════════════════════════════════
#  STATIC TEXT & GRAPHICS
# ══════════════════════════════════════════════════════════════════════════════
HEADER_EMOJI = "🪐"
FOOTER_TEXT = "✨ Powered by <a href='https://x.com/thewhiterabbitM'>@thewhiterabbitM</a>"

WELCOME = (
    f"{HEADER_EMOJI} <b>Polkadot Wiki Bot</b> {HEADER_EMOJI}\n\n"
    "<blockquote>Your gateway to the Polkadot ecosystem</blockquote>\n\n"
    "🔍 <b>What you can do:</b>\n"
    "  • Browse the official <a href='https://wiki.polkadot.network'>Polkadot Wiki</a>\n"
    "  • Read article previews instantly\n"
    "  • Search topics with /search\n\n"
    "📚 <b>Available Sections:</b>\n"
    "  📚 Learn — Core concepts & fundamentals\n"
    "  🔧 Build — Development tools & guides\n"
    "  ⚙️ Maintain — Node operations & staking\n"
    "  🌐 General — Community & resources\n\n"
    "💡 <i>Tip: Use /search staking to find staking-related articles</i>\n\n"
    f"{FOOTER_TEXT}"
)


# ══════════════════════════════════════════════════════════════════════════════
#  COMMAND HANDLERS
# ══════════════════════════════════════════════════════════════════════════════
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        WELCOME, parse_mode='HTML',
        reply_markup=kb_main_menu(),
        disable_web_page_preview=True,
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        WELCOME, parse_mode='HTML',
        reply_markup=kb_main_menu(),
        disable_web_page_preview=True,
    )


ABOUT_TEXT = (
    f"{HEADER_EMOJI} <b>About Polkadot Wiki Bot</b> {HEADER_EMOJI}\n\n"
    "<b>Version:</b> 2.0\n"
    "<b>Created by:</b> @thewhiterabbitM\n"
    "<b>Twitter:</b> x.com/thewhiterabbitM\n\n"
    "This bot provides instant access to the official Polkadot Wiki, "
    "allowing users to browse documentation, search topics, and read "
    "articles directly from Telegram.\n\n"
    "📚 <b>Total Articles:</b> 36\n"
    "🔄 <b>Last Updated:</b> March 2025\n\n"
    f"{FOOTER_TEXT}"
)


async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show about information"""
    await update.message.reply_text(
        ABOUT_TEXT, parse_mode='HTML',
        reply_markup=kb_main_menu(),
        disable_web_page_preview=True,
    )


async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enhanced search with better formatting"""
    query = ' '.join(context.args).strip()
    if not query:
        await update.message.reply_text(
            '🔍 <b>Search Wiki Articles</b>\n\n'
            '<i>Usage:</i> <code>/search staking</code>\n\n'
            '<i>Popular searches:</i> staking, parachain, governance, DOT',
            parse_mode='HTML',
        )
        return

    q       = query.lower()
    results = []
    for sec_key, sec in SECTIONS.items():
        for slug, label in sec['topics']:
            if q in label.lower() or q in slug.lower():
                results.append((sec_key, slug, label))

    if not results:
        await update.message.reply_text(
            f'❌ No results for "<b>{html.escape(query)}</b>"\n\n'
            '💡 <i>Try different keywords or browse with /start</i>',
            parse_mode='HTML',
        )
        return

    await update.message.reply_text(
        f'🔍 <b>{len(results)} result{"s" if len(results) > 1 else ""} for "{html.escape(query)}"</b>:',
        parse_mode='HTML',
        reply_markup=kb_search_results(results[:10]),
    )


# ══════════════════════════════════════════════════════════════════════════════
#  CALLBACK HANDLER  (inline button presses)
# ══════════════════════════════════════════════════════════════════════════════
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q    = update.callback_query
    data = q.data
    await q.answer()

    # ── Ignore noop buttons (headers) ───────────────────────────────────────
    if data == 'noop':
        return

    # ── Main menu ─────────────────────────────────────────────────────────────
    if data == 'back:main':
        await q.edit_message_text(
            WELCOME, parse_mode='HTML',
            reply_markup=kb_main_menu(),
            disable_web_page_preview=True,
        )

    # ── About page ────────────────────────────────────────────────────────────
    elif data == 'about':
        await q.edit_message_text(
            ABOUT_TEXT, parse_mode='HTML',
            reply_markup=kb_main_menu(),
            disable_web_page_preview=True,
        )

    # ── Section listing ───────────────────────────────────────────────────────
    elif data.startswith('section:'):
        sec_key = data.split(':', 1)[1]
        sec     = SECTIONS.get(sec_key)
        if not sec:
            return
        text = (
            f"{sec['emoji']} <b>{sec['label']}</b>\n\n"
            "<i>Select a topic below:</i>"
        )
        await q.edit_message_text(
            text, parse_mode='HTML',
            reply_markup=kb_section(sec_key),
        )

    # ── Article preview ───────────────────────────────────────────────────────
    elif data.startswith('topic:'):
        _, sec_key, slug = data.split(':', 2)
        sec   = SECTIONS.get(sec_key, {})
        label = next((l for s, l in sec.get('topics', []) if s == slug), slug)

        # Show loading state
        await q.edit_message_text(
            f"⏳ <b>Loading {html.escape(label)}…</b>",
            parse_mode='HTML',
        )

        preview, url = fetch_article(slug)

        text = (
            f"{sec.get('emoji', '')} <b>{html.escape(label)}</b>\n\n"
            f"{html.escape(preview)}"
        )
        await q.edit_message_text(
            text, parse_mode='HTML',
            reply_markup=kb_article(sec_key, slug),
        )


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
def validate_token() -> bool:
    """Validate that bot token is properly configured."""
    if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        logger.error("❌ WIKI_BOT_TOKEN not configured!")
        logger.error("Please set WIKI_BOT_TOKEN in your .env file")
        logger.error("Get your token from @BotFather on Telegram")
        return False
    if len(BOT_TOKEN) < 20 or ':' not in BOT_TOKEN:
        logger.error("❌ WIKI_BOT_TOKEN appears to be invalid!")
        logger.error("Token format should be: 123456789:ABCdefGHIjklMNOpqrSTUvwxyz")
        return False
    return True


def main() -> None:
    logger.info("🪐 Polkadot Wiki Bot starting…")
    
    # Validate configuration before starting
    if not validate_token():
        exit(1)
    
    logger.info("✅ Configuration validated")
    logger.info(f"📚 Loaded {sum(len(sec['topics']) for sec in SECTIONS.values())} articles")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start',  cmd_start))
    app.add_handler(CommandHandler('help',   cmd_help))
    app.add_handler(CommandHandler('about',  cmd_about))
    app.add_handler(CommandHandler('search', cmd_search))
    app.add_handler(CallbackQueryHandler(on_callback))

    logger.info("🚀 Bot is running! Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
