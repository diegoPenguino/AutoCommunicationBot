# Technical Specifications: AutoNotifications

## 1. Project Overview
AutoNotifications is an automated broadcasting system designed to simplify the generation and distribution of announcements for the IOI Team Bolivia. It uses an LLM to draft messages based on brief user inputs (a link and a comment) and distributes the approved drafts across multiple channels.

- **Backend Framework:** FastAPI (Python 3.11)
- **Database:** PostgreSQL 15
- **ORM:** SQLAlchemy (Async)
- **Containerization:** Docker & Docker Compose
- **Bot Framework:** `python-telegram-bot` (Webhook Mode)
- **AI Integration:** OpenAI (`gpt-4o-mini`)

## 2. System Architecture & Workflow

The system acts as a centralized webhook receiver that processes inputs from an authorized Telegram Admin, interacts with external APIs, and logs activities.

### 2.1 State Flow
1. **Input Phase:** Admin sends a text message to the Telegram bot containing a URL and instructions.
2. **Drafting Phase:** FastAPI receives the webhook update, routes it to the message handler, and calls the OpenAI API to generate a draft in Spanish.
3. **Review Phase:** The generated draft is sent back to the Admin via Telegram with an Inline Keyboard (`Accept`, `Regenerate`, `Cancel`). The draft state is temporarily held in the `python-telegram-bot`'s `user_data` context.
4. **Execution Phase:** Upon receiving an `Accept` callback query, the system:
   - Stores the message in the PostgreSQL database.
   - Triggers asynchronous broadcast functions to SMTP, WhatsApp API, and Telegram API.

## 3. Data Storage

### 3.1 Database (PostgreSQL)
The application connects asynchronously using `asyncpg` and automatically initializes tables via SQLAlchemy's declarative metadata on startup.

**Table:** `message_logs`
- `id` (Integer): Primary Key, Auto-increment.
- `message` (Text): The exact content of the broadcasted message.
- `timestamp` (DateTime): UTC timezone-aware timestamp of when the broadcast was initiated.

### 3.2 Local Filesystem
**File:** `contacts.csv`
- Mounted inside the Docker container.
- **Columns:** `name`, `lastname`, `mail_address`.
- Read via `pandas` during the email broadcasting phase.

## 4. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Health check endpoint. Returns a basic status message. |
| `POST` | `/webhook` | Ingests JSON payloads from Telegram. Updates are parsed and fed into `ptb_app.process_update()`. |

## 5. External Integrations

### 5.1 OpenAI (LLM Service)
- **Library:** `openai` (v1.0+ Async Client)
- **Model:** `gpt-4o-mini`
- **Temperature:** `0.7`
- **System Prompt:** Configured to act as a professional assistant for the IOI Team Bolivia, generating concise Spanish announcements incorporating the provided link.

### 5.2 Email Distribution (SMTP)
- **Library:** Built-in `smtplib`, `email.mime`
- **Server:** `smtp.gmail.com` (Port 587)
- **Authentication:** Gmail Account + App Password.
- **Logic:** Iterates over `contacts.csv`, generating a personalized `MIMEMultipart` text email (`Hola {name}, ...`) for each row.

### 5.3 WhatsApp Cloud API
- **Library:** `httpx` (Async)
- **Endpoint:** `https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages`
- **Payload:** JSON with `messaging_product: "whatsapp"` and `type: "text"`.
- **Authentication:** Bearer Token.

### 5.4 Telegram API
- **Library:** `httpx` (Async)
- **Endpoint:** `https://api.telegram.org/bot{BOT_TOKEN}/sendMessage`
- **Payload:** JSON with `chat_id` and `text`.
- **Target:** Static group ID provided in environment configuration.

## 6. Environment Configuration (`.env`)

Loaded via `pydantic-settings`.

- `TELEGRAM_BOT_TOKEN`: The bot token from BotFather.
- `TELEGRAM_GROUP_ID`: Target Chat ID for the final Telegram broadcast.
- `ADMIN_USER_ID`: Numeric Telegram User ID allowed to interact with the bot.
- `WEBHOOK_URL`: Base public URL for the FastAPI server (e.g., ngrok URL).
- `OPENAI_API_KEY`: Secret key for LLM drafting.
- `GMAIL_ADDRESS` & `GMAIL_APP_PASSWORD`: SMTP Credentials.
- `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_TARGET_GROUP_ID`: Meta Cloud API credentials.
- `DATABASE_URL`: Connection string (e.g., `postgresql+asyncpg://postgres:postgres@db:5432/autonotifications`).

## 7. Container Orchestration
Defined in `docker-compose.yml`.
- **`db` Service:** `postgres:15-alpine`. Exposes port 5432. Utilizes a Docker volume (`postgres_data`) for persistence.
- **`web` Service:** Builds from the local `Dockerfile`. Mounts local directory as `/app`. Depends on the `db` service. Exposes port 8000. Uses Uvicorn to serve the FastAPI app (`app.main:app`).
