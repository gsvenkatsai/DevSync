const TelegramBot = require("node-telegram-bot-api");
const { formatAlert } = require("./alert");

const TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;

if (!TOKEN || !CHAT_ID) {
  console.error("[devsync] ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set");
  process.exit(1);
}

const bot = new TelegramBot(TOKEN, { polling: true });

console.log("[devsync] Telegram bot started");

// Track process names by pid for Contract D
const pidToProcessName = {};

function sendAlert(contractC) {
  // Store process name so tap handler can build Contract D
  pidToProcessName[contractC.pid] = contractC.process_name;

  const message = formatAlert(contractC);
  const keyboard = {
    inline_keyboard: [
      [
        { text: "✅ Yes",     callback_data: JSON.stringify({ response: "Y",      pid: contractC.pid }) },
        { text: "❌ No",      callback_data: JSON.stringify({ response: "N",      pid: contractC.pid }) },
        { text: "✏️ Custom", callback_data: JSON.stringify({ response: "CUSTOM", pid: contractC.pid }) },
        { text: "🔒 Auto",   callback_data: JSON.stringify({ response: "AUTO",   pid: contractC.pid }) }
      ]
    ]
  };

  return bot.sendMessage(CHAT_ID, message, {
    parse_mode: "HTML",
    reply_markup: keyboard
  });
}

// Handle button taps — Layer 5
bot.on("callback_query", (query) => {
  const data = JSON.parse(query.data);
  console.log(`[devsync] button tapped: response=${data.response} pid=${data.pid}`);
  bot.answerCallbackQuery(query.id, { text: `Sent: ${data.response}` });

  // Lazy require to avoid circular dependency
  const { handleTap } = require("./server");
  const processName = pidToProcessName[data.pid] || "unknown";
  handleTap(data.response, data.pid, processName);
});

module.exports = { bot, CHAT_ID, sendAlert };