# Integrations Setup Guide

This guide provides step-by-step instructions on how to set up the external services required for your AutoNotifications project.

---

## 1. Telegram Bot (User Interface & Group Broadcast)

You need Telegram for two things: interacting with the bot (to send links and approve drafts) and sending the final broadcast to a Telegram group.

### A. Create the Bot
1. Open the Telegram app and search for **@BotFather**.
2. Start a chat and send the command `/newbot`.
3. Follow the prompts to choose a display name and a unique username (must end in `bot`).
4. BotFather will provide you with a **Bot Token** (e.g., `123456789:ABCdefGHIjklmNOPqrsTUVwxyz`).
   - *Save this as `TELEGRAM_BOT_TOKEN` in your `.env` file.*

### B. Add the Bot to Your Group
1. Open the Telegram Group where you want to send the announcements.
2. Go to the group settings and add your newly created bot as a member.
3. Promote the bot to **Administrator** so it has permissions to post messages.

### C. Get the Group Chat ID
1. To find the `TELEGRAM_GROUP_ID`, you can use a helper bot like **@RawDataBot** or **@myidbot**. Add one of these bots to your group, and it will print out the Chat ID.
2. Telegram Group IDs typically start with a minus sign (e.g., `-1001234567890`).
   - *Save this as `TELEGRAM_GROUP_ID` in your `.env` file.*

### D. Get Your Personal User ID (Admin ID)
1. Message **@userinfobot** or **@myidbot** from your personal Telegram account to get your numeric User ID.
   - *Save this as `ADMIN_USER_ID` in your `.env` file. This prevents strangers from using your bot.*

---

## 2. OpenAI API (LLM Drafter)

This service is used to automatically draft your announcements based on the links you provide.

1. Go to the [OpenAI Developer Platform](https://platform.openai.com/).
2. Sign in or create an account.
3. You will need to set up billing (add a credit card) to use the API. The `gpt-4o-mini` model used in the code is extremely cheap (fractions of a cent per message).
4. Navigate to **Dashboard > API Keys**.
5. Click **"Create new secret key"**. Give it a name like "AutoNotifications".
6. Copy the key immediately (it starts with `sk-...`). You won't be able to see it again.
   - *Save this as `OPENAI_API_KEY` in your `.env` file.*

---

## 3. Email via Gmail (SMTP)

To send emails using your standard Gmail account, you cannot use your normal password. You must generate an "App Password".

1. Go to your [Google Account Manage page](https://myaccount.google.com/).
2. Navigate to the **Security** tab on the left.
3. Under "How you sign in to Google", ensure **2-Step Verification** is turned **ON**. (You cannot create App Passwords without this).
4. Search for **App passwords** in the top search bar of your Google Account.
5. In the "Select app" dropdown, choose "Other (Custom name)" and type "AutoNotifications".
6. Click **Generate**.
7. Google will show you a 16-character password in a yellow box (e.g., `abcd efgh ijkl mnop`).
   - *Save your Gmail address as `GMAIL_ADDRESS` in your `.env` file.*
   - *Save the 16-character password (without spaces) as `GMAIL_APP_PASSWORD` in your `.env` file.*

---

## 4. WhatsApp (Official Meta Cloud API)

> [!WARNING]
> **Important Limitation:** The official Meta WhatsApp Cloud API is designed for Business-to-Consumer messaging. **It does not natively support sending automated messages to standard WhatsApp Groups.** 
> 
> With the official API, you must send messages to individual phone numbers (which requires them to opt-in, or you must use pre-approved templates). If you strictly need to send to a normal WhatsApp Group, you will need to switch to an unofficial library like `baileys` or `wwebjs` (which run a headless WhatsApp Web instance). 
> 
> The steps below assume you are setting up the official API to broadcast to individual users or a business broadcast list.

### A. Set up the Meta Developer App
1. Go to [Meta for Developers](https://developers.facebook.com/) and log in with your Facebook account.
2. Click **My Apps** -> **Create App**.
3. Select **Other** -> **Next**, then select **Business** as the app type.
4. Give your app a name (e.g., "IOI Bolivia Notifications") and click **Create app**.

### B. Configure WhatsApp
1. In the "Add products to your app" screen, find **WhatsApp** and click **Set up**.
2. Meta will ask you to select or create a Meta Business Account.
3. Once set up, navigate to **WhatsApp -> API Setup** on the left menu.
4. Here you will find:
   - A **Temporary Access Token** (valid for 24 hours). For a permanent token, you'll need to create a System User in your Business Settings.
   - A **Phone Number ID**.
   - *Save the token as `WHATSAPP_ACCESS_TOKEN` in your `.env` file.*
   - *Save the Phone Number ID as `WHATSAPP_PHONE_NUMBER_ID` in your `.env` file.*

### C. Sending Messages
1. In the "API Setup" section, Meta provides a test phone number you can use to send messages.
2. To send to real people, you must register a real phone number with the WhatsApp Business API.
3. *Set the target phone number (with country code, no `+`) as `WHATSAPP_TARGET_GROUP_ID` in your `.env` file.* (Note: the variable is named group ID based on initial plans, but it expects a phone number in the official API).

---

## 5. Exposing your Local App to the Internet (Webhook URL)

Telegram requires a public URL to send messages to your bot. If you are running this on your local laptop, you need a tunnel.

1. Download and install [ngrok](https://ngrok.com/).
2. Run the command: `ngrok http 8000`
3. Ngrok will give you a public URL (e.g., `https://a1b2c3d4.ngrok-free.app`).
4. *Save this URL (without a trailing slash) as `WEBHOOK_URL` in your `.env` file.*
5. Note: Every time you restart ngrok on the free tier, the URL changes, so you will need to update your `.env` and restart your Docker container. For a permanent solution, deploy the app to a VPS (like DigitalOcean or AWS) or use a static domain.
