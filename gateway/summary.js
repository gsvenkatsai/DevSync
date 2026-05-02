const { bot, CHAT_ID } = require("./bot");

function sendSummary(summaryData) {
  const {
    process_name,
    pid,
    duration_seconds,
    total_stdout_lines,
    silence_events,
    injections,
    errors_detected
  } = summaryData;

  const duration_mins = Math.floor(duration_seconds / 60);
  const duration_secs = Math.round(duration_seconds % 60);
  const resolved = injections ? injections.length : 0;
  const errors = errors_detected ? errors_detected.length : 0;
  const errorLine = errors > 0 ? `⚠️ <b>Errors:</b> ${errors} detected\n` : `✅ <b>Errors:</b> none\n`;

  const message =
    `✅ <b>DevSync — Job Complete</b>\n` +
    `━━━━━━━━━━━━━━━\n` +
    `📋 <b>Process:</b> ${process_name} (pid ${pid})\n` +
    `⏱️ <b>Duration:</b> ${duration_mins}m ${duration_secs}s\n` +
    `🔔 <b>Prompts resolved:</b> ${resolved}\n` +
    `📊 <b>Stdout lines:</b> ${total_stdout_lines}\n` +
    errorLine +
    `📁 <b>Log saved to:</b> <code>logs/${process_name}_${pid}.json</code>`;

  return bot.sendMessage(CHAT_ID, message, { parse_mode: "HTML" });
}

module.exports = { sendSummary };