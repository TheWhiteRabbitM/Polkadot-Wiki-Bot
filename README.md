# 🪐 Polkadot Wiki Bot

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-2CA5E0?logo=telegram)](https://t.me/)
[![Polkadot](https://img.shields.io/badge/Polkadot-Ecosystem-pink?logo=polkadot)](https://polkadot.network/)

> A professional Telegram bot for browsing and searching the official [Polkadot Wiki](https://wiki.polkadot.network) directly from Telegram.

![Bot Screenshot](assets/screenshot.png)

## ✨ Features

- 📚 **Browse Categories**: Navigate through Learn, Build, Maintain, and General sections
- 🔍 **Smart Search**: Search articles by keywords
- 📖 **Instant Previews**: Read article summaries without leaving Telegram
- 🎯 **Clean Interface**: User-friendly inline keyboard navigation
- ⚡ **Fast**: Optimized content extraction and caching
- 🔗 **Direct Links**: One-click access to full articles
- 📱 **Mobile Friendly**: Perfectly formatted for mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Internet connection

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/polkadot-wiki-bot.git
   cd polkadot-wiki-bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Telegram Bot Token:
   ```
   WIKI_BOT_TOKEN=your_bot_token_here
   ```

5. **Run the bot**
   ```bash
   python wikibot.py
   ```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Create a `.env` file**
   ```bash
   echo "WIKI_BOT_TOKEN=your_bot_token_here" > .env
   ```

2. **Start the container**
   ```bash
   docker-compose up -d
   ```

3. **View logs**
   ```bash
   docker-compose logs -f
   ```

### Using Docker directly

```bash
# Build the image
docker build -t polkadot-wiki-bot .

# Run the container
docker run -d \
  --name polkadot-wiki-bot \
  --restart unless-stopped \
  -e WIKI_BOT_TOKEN=your_bot_token_here \
  polkadot-wiki-bot
```

## 🎮 Usage

Once the bot is running, open Telegram and search for your bot username.

### Available Commands

| Command | Description |
|---------|-------------|
| `/start` | Show main menu with all sections |
| `/help` | Display help message |
| `/search <query>` | Search for articles (e.g., `/search staking`) |
| `/about` | Show bot information |

### Navigation

- **📚 Learn**: Core concepts, staking, governance, architecture
- **🔧 Build**: Development tools, smart contracts, parachains
- **⚙️ Maintain**: Node operations, validators, troubleshooting
- **🌐 General**: Community, FAQ, getting started

## 📁 Project Structure

```
polkadot-wiki-bot/
├── wikibot.py              # Main bot application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .env                   # Your configuration (not in git)
├── .gitignore            # Git ignore rules
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── README.md             # This file
├── LICENSE               # MIT License
└── assets/               # Screenshots and images
    └── screenshot.png
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WIKI_BOT_TOKEN` | ✅ Yes | - | Telegram Bot Token from @BotFather |

### Optional Settings

You can modify these constants in `wikibot.py`:

```python
MAX_PREVIEW = 500        # Characters shown in preview
REQUEST_TIMEOUT = 15     # HTTP request timeout (seconds)
```

## 🛠️ Development

### Running Tests

```bash
# Check if all wiki links are valid
python check_links.py
```

### Code Style

This project follows PEP 8 style guide. Format your code with:

```bash
pip install black
black wikibot.py
```

## 📊 Wiki Coverage

The bot includes **39 verified articles** across 4 categories:

- ✅ **Learn** (15 articles): Architecture, Accounts, DOT Token, Staking, etc.
- ✅ **Build** (9 articles): Development guides, tools, protocols
- ✅ **Maintain** (6 articles): Node setup, validation, troubleshooting
- ✅ **General** (9 articles): Getting started, community, FAQ

All links are verified and working as of March 2025.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Reporting Issues

If you find a broken link or bug, please open an issue with:
- Description of the problem
- Steps to reproduce
- Expected vs actual behavior

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Polkadot Wiki](https://wiki.polkadot.network) - Official Polkadot documentation
- [python-telegram-bot](https://python-telegram-bot.org/) - Telegram Bot API wrapper
- [Web3 Foundation](https://web3.foundation/) - For the amazing Polkadot ecosystem

## 🔗 Links

- 🌐 **Bot**: [@YourBotUsername](https://t.me/YourBotUsername)
- 📖 **Wiki**: https://wiki.polkadot.network
- 🐦 **Twitter**: [@thewhiterabbitM](https://x.com/thewhiterabbitM)
- 💻 **GitHub**: https://github.com/yourusername/polkadot-wiki-bot

## ⚠️ Disclaimer

This is an unofficial community project. It is not affiliated with or endorsed by the Web3 Foundation or Parity Technologies.

---

<p align="center">
  Made with ❤️ by <a href="https://x.com/thewhiterabbitM">@thewhiterabbitM</a>
</p>
