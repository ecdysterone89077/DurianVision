import asyncio
import aiohttp
import json
import base64
import time
import random
import traceback

INFERENCE_URL = "http://localhost:8001"
BACKEND_URL = "http://localhost:3005"

async def fuzz_inference(session):
    # Fuzz /predict/base64
    payloads = [
        {"image": ""}, # empty
        {"image": "not-a-base-64"},
        {"image": base64.b64encode(b"random-bytes").decode('utf-8')},
        {"image": base64.b64encode(b"dummy"*1000).decode('utf-8'), "confidence": -1.5, "iou": 2.5, "imgsz": "not-an-int"},
        {}, # missing required fields
        {"image": "a"*1000000} # massive payload
    ]
    
    for i, payload in enumerate(payloads):
        try:
            async with session.post(f"{INFERENCE_URL}/predict/base64", data=payload) as resp:
                status = resp.status
                # As long as it doesn't crash the server (server returns 4xx or 500 but stays alive)
                print(f"[Inference Fuzz] Payload {i} -> Status {status}")
        except Exception as e:
            print(f"[Inference Fuzz] Payload {i} -> Exception {e}")

async def blast_backend(session):
    # Blast backend with concurrent unauth requests
    for i in range(50):
        try:
            async with session.get(f"{BACKEND_URL}/api/settings") as resp:
                pass
        except:
            pass
    print("[Backend Blast] Completed 50 unauth rapid requests.")

async def main():
    print("Starting EXTREME FUZZ TEST...")
    async with aiohttp.ClientSession() as session:
        # Run concurrently
        tasks = [
            fuzz_inference(session),
            blast_backend(session),
            fuzz_inference(session)
        ]
        await asyncio.gather(*tasks)
    print("EXTREME FUZZ TEST FINISHED.")

if __name__ == "__main__":
    asyncio.run(main())
