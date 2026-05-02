const WebSocket = require("ws");
const { bot, CHAT_ID, sendAlert } = require("./bot");
const { sendSummary } = require("./summary");

const PORT = 8765;
const wss = new WebSocket.Server({ port: PORT });

console.log(`[devsync] WebSocket server listening on ws://localhost:${PORT}`);

const wrapperSessions = {};

wss.on("connection", (ws) => {
  console.log("[devsync] client connected");

  ws.on("message", (data) => {
    try {
      const msg = JSON.parse(data);

      // Wrapper registering itself
      if (msg.type === "REGISTER") {
        wrapperSessions[msg.pid] = ws;
        console.log(`[devsync] wrapper registered for pid=${msg.pid}`);
        return;
      }

      // Session complete — send summary to Telegram
      if (msg.type === "SESSION_COMPLETE") {
        console.log(`[devsync] session complete for pid=${msg.pid}`);
        sendSummary(msg)
          .then(() => console.log("[devsync] summary sent to Telegram"))
          .catch((err) => console.error("[devsync] summary error:", err.message));
        return;
      }

      // Contract C from reasoning engine
      if (msg.recommendation !== undefined) {
        console.log(`[devsync] Contract C received: process=${msg.process_name} pid=${msg.pid}`);
        wrapperSessions[`reasoning_${msg.pid}`] = ws;

        sendAlert(msg)
          .then(() => console.log("[devsync] alert sent to Telegram"))
          .catch((err) => console.error("[devsync] Telegram error:", err.message));
      }

    } catch (err) {
      console.error("[devsync] failed to parse message:", err.message);
    }
  });

  ws.on("close", () => {
    console.log("[devsync] client disconnected");
  });
});

function handleTap(response, pid, processName) {
  const contractD = {
    response: response,
    mode: response === "AUTO" ? "auto" : "manual",
    process_name: processName || "unknown",
    pid: pid,
    timestamp: new Date().toISOString()
  };

  console.log(`[devsync] Contract D built:`, JSON.stringify(contractD));

  const wrapperWs = wrapperSessions[pid];
  if (wrapperWs && wrapperWs.readyState === WebSocket.OPEN) {
    wrapperWs.send(JSON.stringify(contractD));
    console.log(`[devsync] Contract D sent to wrapper pid=${pid}`);
  } else {
    console.warn(`[devsync] no wrapper registered for pid=${pid}`);
  }

  return contractD;
}

module.exports = { wss, handleTap, wrapperSessions };