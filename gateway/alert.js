function formatAlert(contractC) {
  const {
    process_name,
    runtime_seconds,
    prompt_text,
    recommendation,
    reason,
    confidence,
    risk
  } = contractC;

  const runtime_mins = Math.floor(runtime_seconds / 60);
  const riskEmoji = risk === "low" ? "🟢" : risk === "medium" ? "🟡" : "🔴";

  return (
    `⚠️ <b>DevSync — Input Required</b>\n` +
    `━━━━━━━━━━━━━━━\n` +
    `🔧 <b>Process:</b> ${process_name}\n` +
    `⏱️ <b>Running:</b> ${runtime_mins} mins\n` +
    `📍 <b>Prompt:</b> <code>${prompt_text}</code>\n\n` +
    `🤖 <b>Claude suggests:</b> ${recommendation}\n` +
    `💡 <b>Reason:</b> ${reason}\n` +
    `📊 <b>Confidence:</b> ${confidence} | ${riskEmoji} Risk: ${risk}`
  );
}

module.exports = { formatAlert };