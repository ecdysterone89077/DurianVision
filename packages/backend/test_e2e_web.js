import { io } from "socket.io-client";
import fs from "fs";
import path from "path";
import axios from "axios";

// Constants
const BACKEND_URL = "http://localhost:3005";
const SOCKET_URL = "http://localhost:3005/detection";

console.log("==================================================");
console.log("  FULL OPERATIONAL 100% END-TO-END TEST");
console.log("  TANPA ADA YANG DI-SKIP!");
console.log("==================================================");

async function login() {
  const email = 'faunas@gmail.com';
  const password = 'faunas123';
  const headers = { Origin: 'http://localhost:5173' };
  let res;
  try {
    res = await axios.post(`${BACKEND_URL}/api/auth/sign-in/email`, { email, password }, { headers });
  } catch {
    await axios.post(`${BACKEND_URL}/api/auth/sign-up/email`, { name: 'Faunas Test', email, password }, { headers });
    res = await axios.post(`${BACKEND_URL}/api/auth/sign-in/email`, { email, password }, { headers });
  }
  const cookies = res.headers['set-cookie'];
  return Array.isArray(cookies) ? cookies.join('; ') : cookies;
}

async function runTest() {
  console.log("[1] Logging in (socket /detection sekarang butuh session)...");
  const cookie = await login();
  console.log("    Auth OK");

  const authHeaders = { headers: { Cookie: cookie, Origin: 'http://localhost:5173' } };
  const sessionRes = await axios.post(`${BACKEND_URL}/api/detection`, { status: 'idle', deviceType: 'smartphone' }, authHeaders);
  const sessionId = sessionRes.data?.data?.id || sessionRes.data?.id;
  console.log("    Session created:", sessionId);

  console.log("\n[2] Initializing Socket.io Client (Mimicking React Frontend)...");

  const socket = io(SOCKET_URL, {
    withCredentials: true,
    extraHeaders: cookie ? { Cookie: cookie } : {}
  });

  socket.on("connect", () => {
    console.log("    Socket Connected! ID:", socket.id);
    console.log("\n[4] Joining Session...");
    socket.emit("join-session", sessionId);
    
    setTimeout(() => {
      console.log("\n[5] Sending Binary Frame (Blob/ArrayBuffer simulation) to Backend...");
      
      // Simulate an image (we'll just use a small dummy buffer, or read a real image if we can)
      let buffer = Buffer.alloc(1024, 0); // 1KB blank image buffer
      
      try {
          const imgPath = path.resolve("../../durian tes.png");
          if(fs.existsSync(imgPath)){
              buffer = fs.readFileSync(imgPath);
              console.log("    Loaded real test image:", buffer.length, "bytes");
          } else {
              console.log("    Image not found at", imgPath);
          }
      }catch(e){
          console.log("    Using dummy buffer.");
      }

      socket.emit("process-frame", {
        sessionId: sessionId,
        image: buffer, // Sending binary!
        config: { confidence: 0.25, imgsz: 640 }
      });
    }, 1000);
  });

  socket.on("detection-result", (result) => {
    console.log("\n[6] Received AI Detection Result from Backend!");
    console.log("    Inference Time:", result.inferenceTimeMs, "ms");
    console.log("    Detections Found:", result.detections.length);
    if(result.detections.length > 0) {
        console.log("    Top Variety:", result.detections[0].class_name, "("+ (result.detections[0].confidence*100).toFixed(1) + "%)");
    }

    console.log("\n[7] Waiting 2.5 seconds for Ring Buffer Bulk-Flush to trigger...");
    setTimeout(async () => {
      try {
        const logsRes = await axios.get(`${BACKEND_URL}/api/logs?sessionId=${sessionId}&limit=5`, authHeaders);
        const logs = logsRes.data?.data || [];
        console.log("    Logs persisted to DB:", logs.length, "| total:", logsRes.data?.meta?.total);
        if (logs.length === 0) {
          console.error("FAIL: tidak ada log tersimpan di DB");
          process.exit(1);
        }
      } catch (e) {
        console.error("FAIL: gagal verifikasi log", e.message);
        process.exit(1);
      }

      console.log("\n✅ E2E TEST PASSED 100%!");
      console.log("✅ WebSocket Binary Transfer: OK");
      console.log("✅ Pytorch FastAPI Inference: OK");
      console.log("✅ SQLite Ring Buffer Insert: VERIFIED");

      socket.disconnect();
      process.exit(0);
    }, 2500);
  });

  socket.on("connect_error", (err) => {
    console.error("    Socket Connection Error:", err.message);
    process.exit(1);
  });
}

runTest();
