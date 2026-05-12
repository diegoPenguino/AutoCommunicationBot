# AutoCommunicationBot

An automated, AI-powered broadcasting system that drafts official announcements via OpenAI and distributes them across Email, WhatsApp, and Telegram. Built with FastAPI and PostgreSQL.

## Prerequisites

Before installing, ensure you have the following on your machine:
- [Docker](https://www.docker.com/) and Docker Compose
- [Git](https://git-scm.com/)
- API Credentials for: Telegram Bot, OpenAI, Gmail (App Password), and Meta WhatsApp Cloud API.
- A tool like [ngrok](https://ngrok.com/) to expose your local server to the internet (required for Telegram Webhooks).

## Installation & Initialization

Follow these steps to get the project running on your local machine:

### 1. Clone the Repository
```bash
git clone https://github.com/diegoPenguino/AutoCommunicationBot.git
cd AutoCommunicationBot
```

### 2. Configure Environment Variables
The project relies on a `.env` file to securely load API keys and configuration.
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` in your text editor and fill in your actual credentials (tokens, chat IDs, email, etc.).

### 3. Prepare the Contacts List
1. The repository includes a `contacts.csv` file (or you can create one if it doesn't exist).
2. Ensure it has the following headers:
   ```csv
   name,lastname,mail_address
   ```
3. Add the people you want to broadcast emails to.

### 4. Start the Application
Since the application uses Docker, starting it is as simple as running:
```bash
docker-compose up --build -d
```
*Note: This command builds the FastAPI container, spins up the PostgreSQL database, automatically creates the required database tables, and starts the server on port 8000.*

### 5. Setup the Webhook (Local Development)
To allow Telegram to communicate with your local server, you must expose port 8000.
1. Run ngrok in a separate terminal:
   ```bash
   ngrok http 8000
   ```
2. Copy the `https://...` forwarding URL that ngrok provides.
3. Update the `WEBHOOK_URL` variable in your `.env` file with this new URL (do not add a trailing slash).
4. Restart the web container so it registers the new webhook with Telegram:
   ```bash
   docker-compose restart web
   ```

## Usage
Once running, simply send a message to your Telegram bot containing a URL and instructions. The bot will reply with a generated draft, giving you the option to approve and broadcast it to all configured channels.
