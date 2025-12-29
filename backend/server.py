from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import List, Optional
from pydantic import BaseModel
import asyncio
import json
from datetime import datetime

# Import core modules
from core.adapter import WiFiAdapter
from core.scanner import WiFiScanner
from core.deauth import DeauthAttack
from core.handshake import HandshakeCapture

app = FastAPI(title="WiFi Red Team Tool API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.wifi_tool

# Initialize modules
wifi_adapter = WiFiAdapter()
wifi_scanner = WiFiScanner()
deauth_attack = DeauthAttack()
handshake_capture = HandshakeCapture()

# WebSocket connections for real-time updates
active_connections: List[WebSocket] = []

# Pydantic models
class AdapterInfo(BaseModel):
    interface: str
    mode: str
    status: str

class ScanRequest(BaseModel):
    interface: str
    duration: int = 10

class DeauthRequest(BaseModel):
    interface: str
    target_bssid: str
    target_client: Optional[str] = None
    packets: int = 50

class HandshakeRequest(BaseModel):
    interface: str
    target_bssid: str
    channel: int
    duration: int = 60

@app.get("/")
async def root():
    return {
        "status": "online",
        "tool": "WiFi Red Team All-in-One",
        "version": "1.0.0"
    }

# ============ WiFi Adapter Management ============

@app.get("/api/adapter/list")
async def list_adapters():
    """List all available WiFi adapters"""
    try:
        adapters = wifi_adapter.list_interfaces()
        return {"success": True, "adapters": adapters}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/adapter/info/{interface}")
async def get_adapter_info(interface: str):
    """Get information about a specific adapter"""
    try:
        info = wifi_adapter.get_interface_info(interface)
        return {"success": True, "info": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/adapter/monitor/enable/{interface}")
async def enable_monitor_mode(interface: str):
    """Enable monitor mode on adapter"""
    try:
        result = wifi_adapter.enable_monitor_mode(interface)
        return {"success": True, "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/adapter/monitor/disable/{interface}")
async def disable_monitor_mode(interface: str):
    """Disable monitor mode on adapter"""
    try:
        result = wifi_adapter.disable_monitor_mode(interface)
        return {"success": True, "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ Network Scanning ============

@app.post("/api/scan/start")
async def start_scan(scan_request: ScanRequest):
    """Start WiFi network scan"""
    try:
        # Start scan in background
        scan_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Run scan
        networks = wifi_scanner.scan_networks(
            scan_request.interface,
            scan_request.duration
        )
        
        # Store in database
        scan_result = {
            "scan_id": scan_id,
            "timestamp": datetime.now(),
            "interface": scan_request.interface,
            "networks": networks,
            "total_networks": len(networks)
        }
        await db.scans.insert_one(scan_result)
        
        return {
            "success": True,
            "scan_id": scan_id,
            "networks": networks,
            "total": len(networks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scan/history")
async def get_scan_history(limit: int = 10):
    """Get scan history"""
    try:
        scans = await db.scans.find().sort("timestamp", -1).limit(limit).to_list(limit)
        # Convert ObjectId to string
        for scan in scans:
            scan["_id"] = str(scan["_id"])
            scan["timestamp"] = scan["timestamp"].isoformat()
        return {"success": True, "scans": scans}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ Deauthentication Attack ============

@app.post("/api/attack/deauth")
async def deauth_attack_endpoint(request: DeauthRequest):
    """Execute deauthentication attack"""
    try:
        result = deauth_attack.execute(
            interface=request.interface,
            target_bssid=request.target_bssid,
            target_client=request.target_client,
            packet_count=request.packets
        )
        
        # Store attack log
        attack_log = {
            "type": "deauth",
            "timestamp": datetime.now(),
            "interface": request.interface,
            "target_bssid": request.target_bssid,
            "target_client": request.target_client,
            "packets_sent": request.packets,
            "result": result
        }
        await db.attacks.insert_one(attack_log)
        
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ Handshake Capture ============

@app.post("/api/capture/handshake")
async def capture_handshake_endpoint(request: HandshakeRequest):
    """Capture WPA/WPA2 handshake"""
    try:
        result = handshake_capture.capture(
            interface=request.interface,
            target_bssid=request.target_bssid,
            channel=request.channel,
            duration=request.duration
        )
        
        # Store capture log
        capture_log = {
            "type": "handshake",
            "timestamp": datetime.now(),
            "interface": request.interface,
            "target_bssid": request.target_bssid,
            "channel": request.channel,
            "result": result
        }
        await db.captures.insert_one(capture_log)
        
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ WebSocket for Real-time Updates ============

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
            await websocket.send_text(json.dumps({"status": "connected"}))
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_update(message: dict):
    """Broadcast updates to all connected clients"""
    for connection in active_connections:
        try:
            await connection.send_text(json.dumps(message))
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)