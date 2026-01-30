#!/usr/bin/env python3
"""
MCP Endpoint Manager - Cải thiện kết nối với auto-save và ghi nhớ endpoint
Tham khảo từ: https://github.com/78/mcp-calculator
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from typing import Optional, Callable, Dict, Any, List
import websockets

logger = logging.getLogger(__name__)

# ============================================================
# CONNECTION STATE MANAGEMENT
# ============================================================
class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"  
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"

@dataclass
class EndpointConfig:
    """Cấu hình cho một endpoint"""
    name: str = "Thiết bị 1"
    token: str = ""
    enabled: bool = False
    ws_url: str = "wss://api.xiaozhi.me/mcp/"
    # Connection settings
    connect_timeout: float = 10.0
    ping_interval: int = 20
    ping_timeout: int = 10
    max_retries: int = 5
    initial_retry_delay: float = 1.0
    max_retry_delay: float = 15.0
    # Auto reconnect
    auto_reconnect: bool = True
    fast_retry_count: int = 3
    fast_retry_delay: float = 0.5

@dataclass  
class ConnectionStats:
    """Thống kê kết nối"""
    total_connects: int = 0
    total_disconnects: int = 0
    total_errors: int = 0
    last_connected: Optional[str] = None
    last_disconnected: Optional[str] = None
    last_error: Optional[str] = None
    uptime_seconds: float = 0

# ============================================================
# PERSISTENT CONFIG STORAGE
# ============================================================
class EndpointStorage:
    """Lưu trữ persistent cho endpoint config"""
    
    def __init__(self, config_file: str = "xiaozhi_endpoints.json"):
        # Xác định đường dẫn file config
        if getattr(sys, 'frozen', False):
            self.config_path = Path(sys.executable).parent / config_file
        else:
            self.config_path = Path(__file__).parent / config_file
        
        self.backup_path = self.config_path.with_suffix('.json.bak')
        self._cache: Dict[str, Any] = {}
        self._last_saved: Optional[str] = None
        
    def load(self) -> Dict[str, Any]:
        """Load config từ file với fallback"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
                print(f"✅ [Storage] Loaded config from {self.config_path.name}")
                return self._cache
            elif self.backup_path.exists():
                # Fallback to backup
                print(f"⚠️ [Storage] Main config missing, loading from backup")
                with open(self.backup_path, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
                # Restore main file
                self.save(self._cache)
                return self._cache
        except Exception as e:
            print(f"❌ [Storage] Load error: {e}")
        
        # Return default config
        return self._create_default()
    
    def save(self, data: Dict[str, Any], force: bool = False) -> bool:
        """Save config với backup tự động"""
        try:
            # Thêm timestamp
            data['last_saved'] = datetime.now().isoformat()
            
            # So sánh để tránh ghi không cần thiết
            if not force and self._cache:
                # Bỏ qua timestamp khi so sánh
                old_data = {k: v for k, v in self._cache.items() if k != 'last_saved'}
                new_data = {k: v for k, v in data.items() if k != 'last_saved'}
                if old_data == new_data:
                    return True  # Không có thay đổi
            
            # Backup file cũ trước
            if self.config_path.exists():
                import shutil
                shutil.copy2(self.config_path, self.backup_path)
            
            # Ghi file mới
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self._cache = data
            self._last_saved = data['last_saved']
            print(f"💾 [Storage] Saved config to {self.config_path.name}")
            return True
            
        except Exception as e:
            print(f"❌ [Storage] Save error: {e}")
            return False
    
    def get(self, key: str, default=None):
        """Get config value"""
        if not self._cache:
            self.load()
        return self._cache.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set và auto-save"""
        if not self._cache:
            self.load()
        self._cache[key] = value
        self.save(self._cache)
    
    def _create_default(self) -> Dict[str, Any]:
        """Tạo config mặc định"""
        return {
            'endpoints': [
                {"name": "Thiết bị 1", "token": "", "enabled": False},
                {"name": "Thiết bị 2", "token": "", "enabled": False},
                {"name": "Thiết bị 3", "token": "", "enabled": False}
            ],
            'active_index': 0,
            'gemini_api_key': '',
            'openai_api_key': '',
            'serper_api_key': '',
            'connection_stats': {},
            'auto_connect_on_start': True,
            'remember_last_endpoint': True,
            'last_saved': None
        }

# ============================================================
# MCP ENDPOINT CONNECTION MANAGER
# ============================================================
class MCPEndpointManager:
    """
    Quản lý kết nối MCP endpoint với:
    - Auto-reconnect thông minh
    - Ghi nhớ endpoint khi khởi động lại
    - Connection stats tracking
    - Event callbacks
    """
    
    def __init__(self, max_devices: int = 3):
        self.storage = EndpointStorage()
        self.max_devices = max_devices
        
        # Connection state per device
        self.connections: Dict[int, Any] = {}
        self.states: Dict[int, ConnectionState] = {}
        self.stats: Dict[int, ConnectionStats] = {}
        self.should_reconnect: Dict[int, bool] = {}
        self._tasks: Dict[int, asyncio.Task] = {}
        
        # Initialize
        for i in range(max_devices):
            self.connections[i] = None
            self.states[i] = ConnectionState.DISCONNECTED
            self.stats[i] = ConnectionStats()
            self.should_reconnect[i] = False
        
        # Event callbacks
        self._on_connect: List[Callable] = []
        self._on_disconnect: List[Callable] = []
        self._on_message: List[Callable] = []
        self._on_error: List[Callable] = []
        
        # Load saved config
        self._load_config()
        
    def _load_config(self):
        """Load config và khôi phục state"""
        config = self.storage.load()
        
        # Load endpoints
        self.endpoints = config.get('endpoints', [])
        self.active_index = config.get('active_index', 0)
        
        # Load connection stats nếu có
        saved_stats = config.get('connection_stats', {})
        for idx, stats in saved_stats.items():
            idx = int(idx)
            if idx < self.max_devices:
                self.stats[idx] = ConnectionStats(**stats)
        
        # Auto-connect flag
        self.auto_connect = config.get('auto_connect_on_start', True)
        self.remember_endpoint = config.get('remember_last_endpoint', True)
        
        print(f"📋 [Manager] Loaded {len(self.endpoints)} endpoints, active: {self.active_index}")
    
    def save_config(self):
        """Save config hiện tại"""
        config = {
            'endpoints': self.endpoints,
            'active_index': self.active_index,
            'gemini_api_key': self.storage.get('gemini_api_key', ''),
            'openai_api_key': self.storage.get('openai_api_key', ''),
            'serper_api_key': self.storage.get('serper_api_key', ''),
            'connection_stats': {
                str(idx): asdict(stats) 
                for idx, stats in self.stats.items()
            },
            'auto_connect_on_start': self.auto_connect,
            'remember_last_endpoint': self.remember_endpoint
        }
        self.storage.save(config)
    
    # ============================================================
    # EVENT HANDLERS
    # ============================================================
    def on_connect(self, callback: Callable):
        """Register connect callback"""
        self._on_connect.append(callback)
        
    def on_disconnect(self, callback: Callable):
        """Register disconnect callback"""
        self._on_disconnect.append(callback)
        
    def on_message(self, callback: Callable):
        """Register message callback"""
        self._on_message.append(callback)
        
    def on_error(self, callback: Callable):
        """Register error callback"""
        self._on_error.append(callback)
    
    async def _emit_event(self, callbacks: List[Callable], *args, **kwargs):
        """Emit event to all callbacks"""
        for cb in callbacks:
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(*args, **kwargs)
                else:
                    cb(*args, **kwargs)
            except Exception as e:
                logger.error(f"Event callback error: {e}")
    
    # ============================================================
    # CONNECTION MANAGEMENT
    # ============================================================
    def get_endpoint(self, index: int) -> Optional[Dict]:
        """Get endpoint config by index"""
        if 0 <= index < len(self.endpoints):
            return self.endpoints[index]
        return None
    
    def set_endpoint(self, index: int, token: str, name: str = None, enabled: bool = True):
        """Set endpoint config"""
        while len(self.endpoints) <= index:
            self.endpoints.append({"name": f"Thiết bị {len(self.endpoints)+1}", "token": "", "enabled": False})
        
        self.endpoints[index]['token'] = token
        self.endpoints[index]['enabled'] = enabled
        if name:
            self.endpoints[index]['name'] = name
        
        # Auto-save
        self.save_config()
        print(f"💾 [Manager] Endpoint {index} updated and saved")
    
    def set_active(self, index: int):
        """Set active endpoint và trigger reconnect"""
        if 0 <= index < len(self.endpoints):
            old_index = self.active_index
            self.active_index = index
            
            # Save để nhớ lần sau khởi động
            self.save_config()
            print(f"🔄 [Manager] Active endpoint changed: {old_index} → {index}")
            
            # Trigger reconnect cho endpoint mới
            self.should_reconnect[index] = True
    
    def is_connected(self, index: int = None) -> bool:
        """Check connection status"""
        if index is None:
            index = self.active_index
        return self.states.get(index) == ConnectionState.CONNECTED
    
    async def connect(self, index: int = None, message_handler: Callable = None) -> bool:
        """Connect to endpoint"""
        if index is None:
            index = self.active_index
            
        ep = self.get_endpoint(index)
        if not ep or not ep.get('token'):
            print(f"⚠️ [Manager] Endpoint {index} has no token")
            return False
        
        # Cancel existing task if any
        if index in self._tasks and not self._tasks[index].done():
            self._tasks[index].cancel()
            try:
                await self._tasks[index]
            except asyncio.CancelledError:
                pass
        
        # Start new connection task
        self._tasks[index] = asyncio.create_task(
            self._connection_loop(index, message_handler)
        )
        return True
    
    async def disconnect(self, index: int = None):
        """Disconnect from endpoint"""
        if index is None:
            index = self.active_index
        
        self.should_reconnect[index] = False
        
        # Cancel task
        if index in self._tasks and not self._tasks[index].done():
            self._tasks[index].cancel()
            try:
                await self._tasks[index]
            except asyncio.CancelledError:
                pass
        
        # Close connection
        if self.connections[index]:
            try:
                await self.connections[index].close()
            except Exception:
                pass
            self.connections[index] = None
        
        self.states[index] = ConnectionState.DISCONNECTED
        self.stats[index].total_disconnects += 1
        self.stats[index].last_disconnected = datetime.now().isoformat()
        
        # Save stats
        self.save_config()
        
        await self._emit_event(self._on_disconnect, index)
        print(f"🔌 [Manager] Disconnected from endpoint {index}")
    
    async def _connection_loop(self, index: int, message_handler: Callable = None):
        """Main connection loop với smart retry"""
        retry = 0
        connect_start = None
        
        # Config
        config = EndpointConfig()
        
        while True:
            try:
                ep = self.get_endpoint(index)
                if not ep or not ep.get('enabled') or not ep.get('token'):
                    await asyncio.sleep(5)
                    continue
                
                ws_url = f"{config.ws_url}?token={ep['token']}"
                retry += 1
                self.states[index] = ConnectionState.CONNECTING
                
                # Log
                if retry <= config.fast_retry_count:
                    print(f"📡 [Manager] Fast connecting {ep['name']}... ({retry}/{config.fast_retry_count})")
                else:
                    print(f"📡 [Manager] Connecting {ep['name']}... (retry {retry})")
                
                # Connect
                async with websockets.connect(
                    ws_url,
                    ping_interval=config.ping_interval,
                    ping_timeout=config.ping_timeout,
                    close_timeout=5,
                    open_timeout=config.connect_timeout,
                    max_size=10 * 1024 * 1024
                ) as ws:
                    # Success!
                    self.connections[index] = ws
                    self.states[index] = ConnectionState.CONNECTED
                    self.should_reconnect[index] = False
                    retry = 0
                    connect_start = datetime.now()
                    
                    # Update stats
                    self.stats[index].total_connects += 1
                    self.stats[index].last_connected = connect_start.isoformat()
                    
                    # Save state
                    self.save_config()
                    
                    # Emit event
                    await self._emit_event(self._on_connect, index, ep['name'])
                    print(f"✅ [Manager] Connected to {ep['name']} [Device {index + 1}]")
                    
                    # Send initialize
                    init_msg = {
                        "jsonrpc": "2.0",
                        "method": "initialize",
                        "params": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {},
                            "clientInfo": {"name": "xiaozhi-mcp", "version": "4.3.0"}
                        },
                        "id": 1
                    }
                    await ws.send(json.dumps(init_msg))
                    
                    # Message loop
                    async for msg in ws:
                        # Check reconnect flag
                        if self.should_reconnect[index]:
                            print(f"🔄 [Manager] Reconnecting {ep['name']}...")
                            await ws.close()
                            break
                        
                        try:
                            data = json.loads(msg)
                            
                            # Emit message event
                            await self._emit_event(self._on_message, index, data)
                            
                            # Call handler if provided
                            if message_handler:
                                response = await message_handler(data)
                                if response:
                                    await ws.send(json.dumps({
                                        "jsonrpc": "2.0",
                                        "id": data.get("id"),
                                        "result": response
                                    }))
                                    
                        except json.JSONDecodeError as e:
                            logger.warning(f"JSON decode error: {e}")
                        except Exception as e:
                            logger.error(f"Message handling error: {e}")
                    
                    # Connection ended - calculate uptime
                    if connect_start:
                        uptime = (datetime.now() - connect_start).total_seconds()
                        self.stats[index].uptime_seconds += uptime
                        
            except asyncio.CancelledError:
                print(f"⚠️ [Manager] Connection task cancelled ({index})")
                break
                
            except websockets.exceptions.WebSocketException as e:
                self.states[index] = ConnectionState.ERROR
                self.connections[index] = None
                self.stats[index].total_errors += 1
                self.stats[index].last_error = str(e)
                
                await self._emit_event(self._on_error, index, e)
                
                # Smart retry delay
                if retry <= config.fast_retry_count:
                    wait = config.fast_retry_delay
                else:
                    wait = min(
                        config.initial_retry_delay * (2 ** min(retry - config.fast_retry_count, 4)),
                        config.max_retry_delay
                    )
                print(f"❌ [Manager] WebSocket error: {e} (retry in {wait}s)")
                await asyncio.sleep(wait)
                
            except Exception as e:
                self.states[index] = ConnectionState.ERROR
                self.connections[index] = None
                self.stats[index].total_errors += 1
                self.stats[index].last_error = str(e)
                
                await self._emit_event(self._on_error, index, e)
                
                # Smart retry delay
                if retry <= config.fast_retry_count:
                    wait = config.fast_retry_delay
                else:
                    wait = min(
                        config.initial_retry_delay * (2 ** min(retry - config.fast_retry_count, 4)),
                        config.max_retry_delay
                    )
                print(f"❌ [Manager] Error: {e} (retry in {wait}s)")
                await asyncio.sleep(wait)
        
        # Cleanup
        self.states[index] = ConnectionState.DISCONNECTED
        self.connections[index] = None
    
    async def send(self, index: int, data: dict) -> bool:
        """Send data to endpoint"""
        if not self.is_connected(index):
            return False
        
        try:
            await self.connections[index].send(json.dumps(data))
            return True
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False
    
    # ============================================================
    # STARTUP / SHUTDOWN
    # ============================================================
    async def start_all(self, message_handler: Callable = None):
        """Start all enabled endpoints"""
        print(f"🚀 [Manager] Starting all endpoints...")
        
        for i in range(self.max_devices):
            ep = self.get_endpoint(i)
            if ep and ep.get('enabled') and ep.get('token'):
                await self.connect(i, message_handler)
                # Stagger connections
                await asyncio.sleep(0.5)
        
        print(f"✅ [Manager] All endpoints started")
    
    async def stop_all(self):
        """Stop all connections"""
        print(f"🛑 [Manager] Stopping all endpoints...")
        
        for i in range(self.max_devices):
            await self.disconnect(i)
        
        # Save final stats
        self.save_config()
        print(f"✅ [Manager] All endpoints stopped")
    
    def get_status(self) -> Dict:
        """Get current status of all endpoints"""
        status = {
            'active_index': self.active_index,
            'endpoints': []
        }
        
        for i, ep in enumerate(self.endpoints):
            status['endpoints'].append({
                'index': i,
                'name': ep.get('name', f'Device {i+1}'),
                'enabled': ep.get('enabled', False),
                'has_token': bool(ep.get('token')),
                'state': self.states.get(i, ConnectionState.DISCONNECTED).value,
                'stats': asdict(self.stats.get(i, ConnectionStats()))
            })
        
        return status


# ============================================================
# SINGLETON INSTANCE
# ============================================================
_manager: Optional[MCPEndpointManager] = None

def get_endpoint_manager() -> MCPEndpointManager:
    """Get global endpoint manager instance"""
    global _manager
    if _manager is None:
        _manager = MCPEndpointManager()
    return _manager


# ============================================================
# TEST
# ============================================================
async def test():
    """Test endpoint manager"""
    manager = get_endpoint_manager()
    
    print("\n📋 Current status:")
    print(json.dumps(manager.get_status(), indent=2, default=str))
    
    # Test callbacks
    def on_connect(index, name):
        print(f"🔔 CALLBACK: Connected to {name}")
    
    def on_error(index, error):
        print(f"🔔 CALLBACK: Error on {index}: {error}")
    
    manager.on_connect(on_connect)
    manager.on_error(on_error)
    
    # Start if has token
    if manager.endpoints and manager.endpoints[0].get('token'):
        print("\n🚀 Starting connection...")
        await manager.start_all()
        
        # Wait a bit
        await asyncio.sleep(10)
        
        # Stop
        await manager.stop_all()
    else:
        print("\n⚠️ No token configured. Set token first.")

if __name__ == "__main__":
    asyncio.run(test())
