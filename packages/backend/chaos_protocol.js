import { io } from "socket.io-client";
import fs from "fs";
import path from "path";

console.log("==================================================");
console.log("  CHAOS ENGINEERING PROTOCOL - TIER 1");
console.log("  STRESS TEST: MULTI-CLIENT HIGH-FREQUENCY BINARY BOMBARDMENT");
console.log("==================================================");

const SOCKET_URL = "http://localhost:3005/detection";
const CLIENT_COUNT = 3; // 3 concurrent cameras
const DURATION_MS = 5000; // 5 seconds of bombardment
const FPS = 30;
const INTERVAL_MS = Math.floor(1000 / FPS);

let imageBuffer = Buffer.alloc(1024, 0);
try {
  const imgPath = path.resolve("../../durian tes.png");
  if(fs.existsSync(imgPath)){
      imageBuffer = fs.readFileSync(imgPath);
      console.log(`[SYS] Loaded binary ammunition: ${imageBuffer.length} bytes`);
  }
} catch(e) {
  console.log("[SYS] Using blank ammunition.");
}

let activeClients = 0;
let totalFramesSent = 0;
let totalDetectionsReceived = 0;
let connectionPromises = [];

function spawnClient(clientId) {
  return new Promise((resolve) => {
    const socket = io(SOCKET_URL, { reconnection: false });
    const sessionId = `CHAOS_CLIENT_${clientId}`;
    let framesSent = 0;
    let timer = null;

    socket.on("connect", () => {
      activeClients++;
      socket.emit("join-session", sessionId);
      
      // Start bombardment
      timer = setInterval(() => {
        socket.emit("process-frame", {
          sessionId,
          image: imageBuffer,
          config: { confidence: 0.25, imgsz: 640 }
        });
        framesSent++;
        totalFramesSent++;
      }, INTERVAL_MS);

      // Stop after DURATION_MS
      setTimeout(() => {
        clearInterval(timer);
        resolve({ clientId, socket, framesSent });
      }, DURATION_MS);
    });

    socket.on("detection-result", (result) => {
      totalDetectionsReceived++;
    });

    socket.on("connect_error", (err) => {
      console.error(`[CLIENT-${clientId}] Connection Error:`, err.message);
      resolve({ clientId, socket, framesSent: 0 });
    });
  });
}

async function runChaos() {
  console.log(`\n[1] Spawning ${CLIENT_COUNT} concurrent WebSocket clients...`);
  
  for (let i = 1; i <= CLIENT_COUNT; i++) {
    connectionPromises.push(spawnClient(i));
  }

  console.log(`[2] Commencing 30 FPS Binary Bombardment for ${DURATION_MS/1000} seconds...`);
  
  const results = await Promise.all(connectionPromises);
  
  console.log(`\n[3] Bombardment Complete! Waiting 3 seconds for Ring Buffer & Inference lag to settle...`);
  
  setTimeout(() => {
    console.log("\n==================================================");
    console.log("  CHAOS PROTOCOL RESULTS");
    console.log("==================================================");
    console.log(`  Target FPS per client   : ${FPS}`);
    console.log(`  Concurrent Clients      : ${CLIENT_COUNT}`);
    console.log(`  Total Frames Fired      : ${totalFramesSent}`);
    console.log(`  Total Inferences Caught : ${totalDetectionsReceived}`);
    
    const deliveryRate = (totalDetectionsReceived / totalFramesSent) * 100;
    console.log(`  System Resilience Score : ${deliveryRate.toFixed(2)}%`);

    if (deliveryRate > 80) {
      console.log("\n✅ [STATUS: INDESTRUCTIBLE] Server handled the extreme binary load beautifully.");
    } else {
      console.log("\n⚠️ [STATUS: STRESSED] System showed signs of bottlenecking under chaos.");
    }

    results.forEach(r => r.socket.disconnect());
    process.exit(0);
  }, 3000);
}

runChaos();
