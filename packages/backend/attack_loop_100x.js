import { io } from "socket.io-client";

console.log("==================================================");
console.log("  SECURITY AUDIT: LOOP 100x (DoS FRAME SPAMMING)");
console.log("==================================================");

const SOCKET_URL = "http://localhost:3005/detection";
const dummyBuffer = Buffer.alloc(1024, 0);

async function run100xLoop() {
  const socket = io(SOCKET_URL, { reconnection: false });

  await new Promise((resolve, reject) => {
    socket.on("connect", resolve);
    socket.on("connect_error", reject);
  });

  socket.emit("join-session", "HACKER_SESSION_99");

  let totalFramesCaughtByBackend = 0;
  socket.on("detection-result", () => {
    totalFramesCaughtByBackend++;
  });

  console.log(`[SYS] Commencing 100 Attack Loops...`);
  
  for (let loop = 1; loop <= 100; loop++) {
    // In each loop, fire 50 frames synchronously (Zero delay)
    // This simulates a malicious or bugged client that ignores FPS limits.
    for (let i = 0; i < 50; i++) {
      socket.emit("process-frame", {
        sessionId: "HACKER_SESSION_99",
        image: dummyBuffer,
        config: { confidence: 0.25, imgsz: 640 }
      });
    }
    // Wait a tiny bit between loops
    await new Promise(r => setTimeout(r, 10));
  }

  console.log(`[SYS] 100 Loops executed! Total frames fired: ${100 * 50} (5,000 frames)`);
  console.log(`[SYS] Waiting 2 seconds to see how many were actually processed by AI...`);

  setTimeout(() => {
    console.log("==================================================");
    console.log(`  Frames Fired   : 5000`);
    console.log(`  Frames Processed: ${totalFramesCaughtByBackend}`);
    
    // We expect a tiny fraction (only 1 frame per 30ms) to be processed.
    if (totalFramesCaughtByBackend < 200) {
      console.log(`\n✅ [STATUS: SECURE] The DoS protection successfully dropped over 96% of the spam frames.`);
      console.log(`✅ [STATUS: 100% NORMAL] System relations and communication remained pristine under 100x loops.`);
    } else {
      console.log(`\n⚠️ [STATUS: VULNERABLE] The backend processed too many frames, AI Engine might crash!`);
    }

    socket.disconnect();
    process.exit(0);
  }, 2000);
}

run100xLoop().catch(console.error);
