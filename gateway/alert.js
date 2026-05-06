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

  const isHighRisk = risk === "high" || recommendation === "MANUAL_ONLY";

  const header = isHighRisk
    ? `🚨 <b>DevSync — HIGH RISK DETECTED</b>\n`
    : `⚠️ <b>DevSync — Input Required</b>\n`;

  const suggestionLine = isHighRisk
    ? `🚫 <b>Auto-approve BLOCKED.</b> Manual response required.\n`
    : `🤖 <b>Suggests:</b> ${recommendation}\n`;

  return (
    header +
    `━━━━━━━━━━━━━━━\n` +
    `🔧 <b>Process:</b> ${process_name}\n` +
    `⏱️ <b>Running:</b> ${runtime_mins} mins\n` +
    `📍 <b>Prompt:</b> <code>${prompt_text}</code>\n\n` +
    suggestionLine +
    `💡 <b>Reason:</b> ${reason}\n` +
    `📊 <b>Confidence:</b> ${confidence} | ${riskEmoji} Risk: ${risk}`
  );
}

module.exports = { formatAlert };