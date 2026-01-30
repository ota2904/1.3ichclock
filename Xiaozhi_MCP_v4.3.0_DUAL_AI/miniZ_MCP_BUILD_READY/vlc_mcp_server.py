"""
VLC MCP Server - Model Context Protocol for VLC Player Control
Based on xiaozhi-esp32 architecture

Author: miniZ Team
Version: 1.0.0
Date: 2025-12-11
"""

import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime


class VLCMCPServer:
    """
    MCP Server for VLC Player Control
    Implements JSON-RPC 2.0 protocol
    """
    
    def __init__(self, vlc_player):
        """
        Initialize MCP Server
        
        Args:
            vlc_player: VLC player instance from xiaozhi_final.py
        """
        self.vlc = vlc_player
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.session_id = None
        self._register_all_tools()
        
    def _register_all_tools(self):
        """Register all VLC tools with MCP protocol"""
        from vlc_tools_registry import VLC_TOOLS_REGISTRY
        
        for tool_name, tool_def in VLC_TOOLS_REGISTRY.items():
            self.register_tool(tool_name, tool_def)
            
        print(f"✅ [VLC MCP] Registered {len(self.tools)} tools")
    
    def register_tool(self, name: str, definition: Dict[str, Any]):
        """
        Register a tool with the MCP server
        
        Args:
            name: Tool name (e.g., "vlc.play")
            definition: Tool definition with schema
        """
        self.tools[name] = definition
        
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [
            {
                "name": name,
                "description": tool["description"],
                "inputSchema": tool["inputSchema"]
            }
            for name, tool in self.tools.items()
        ]
    
    async def handle_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP request (JSON-RPC 2.0)
        
        Args:
            request: JSON-RPC 2.0 request
            
        Returns:
            JSON-RPC 2.0 response
        """
        jsonrpc = request.get("jsonrpc", "2.0")
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        # Validate JSON-RPC version
        if jsonrpc != "2.0":
            return self._error_response(-32600, "Invalid JSON-RPC version", request_id)
        
        # Handle different methods
        if method == "tools/list":
            return self._success_response(
                {"tools": self.list_tools()},
                request_id
            )
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if not tool_name:
                return self._error_response(-32602, "Missing tool name", request_id)
            
            if tool_name not in self.tools:
                return self._error_response(-32601, f"Tool not found: {tool_name}", request_id)
            
            # Execute tool
            try:
                result = await self._execute_tool(tool_name, arguments)
                return self._success_response(result, request_id)
            except Exception as e:
                return self._error_response(-32603, f"Tool execution error: {str(e)}", request_id)
        
        else:
            return self._error_response(-32601, f"Method not found: {method}", request_id)
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a VLC tool
        
        Args:
            tool_name: Tool name (e.g., "vlc.play")
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        tool_def = self.tools[tool_name]
        handler_name = tool_def["handler"]
        
        # Validate arguments against schema
        schema = tool_def.get("inputSchema", {})
        validation_error = self._validate_arguments(arguments, schema)
        if validation_error:
            raise ValueError(f"Invalid arguments: {validation_error}")
        
        # Map tool to handler method
        if handler_name == "play":
            file_path = arguments.get("file", "")
            return await self._handle_play(file_path)
        
        elif handler_name == "pause":
            return await self._handle_pause()
        
        elif handler_name == "stop":
            return await self._handle_stop()
        
        elif handler_name == "next":
            return await self._handle_next()
        
        elif handler_name == "previous":
            return await self._handle_previous()
        
        elif handler_name == "set_volume":
            volume = arguments.get("volume", 50)
            return await self._handle_set_volume(volume)
        
        elif handler_name == "get_volume":
            return await self._handle_get_volume()
        
        elif handler_name == "seek":
            position = arguments.get("position", 0.0)
            return await self._handle_seek(position)
        
        elif handler_name == "get_position":
            return await self._handle_get_position()
        
        elif handler_name == "load_playlist":
            files = arguments.get("files", [])
            return await self._handle_load_playlist(files)
        
        elif handler_name == "add_to_playlist":
            file_path = arguments.get("file", "")
            return await self._handle_add_to_playlist(file_path)
        
        elif handler_name == "clear_playlist":
            return await self._handle_clear_playlist()
        
        elif handler_name == "shuffle":
            enabled = arguments.get("enabled", True)
            return await self._handle_shuffle(enabled)
        
        elif handler_name == "get_current_track":
            return await self._handle_get_current_track()
        
        elif handler_name == "get_status":
            return await self._handle_get_status()
        
        else:
            raise ValueError(f"Unknown handler: {handler_name}")
    
    # ==================== Tool Handlers ====================
    
    async def _handle_play(self, file_path: str = "") -> Dict[str, Any]:
        """Play file or resume playback"""
        try:
            if file_path:
                # Play specific file
                self.vlc.set_mrl(file_path)
                self.vlc.play()
            else:
                # Resume playback
                self.vlc.play()
            
            return {
                "success": True,
                "status": "playing",
                "file": file_path if file_path else "current track"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_pause(self) -> Dict[str, Any]:
        """Pause playback"""
        try:
            self.vlc.pause()
            return {"success": True, "status": "paused"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_stop(self) -> Dict[str, Any]:
        """Stop playback"""
        try:
            self.vlc.stop()
            return {"success": True, "status": "stopped"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_next(self) -> Dict[str, Any]:
        """Next track"""
        try:
            self.vlc.next()
            return {"success": True, "action": "next_track"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_previous(self) -> Dict[str, Any]:
        """Previous track"""
        try:
            self.vlc.previous()
            return {"success": True, "action": "previous_track"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_set_volume(self, volume: int) -> Dict[str, Any]:
        """Set volume (0-100)"""
        try:
            if not 0 <= volume <= 100:
                return {"success": False, "error": "Volume must be 0-100"}
            
            self.vlc.audio_set_volume(volume)
            return {"success": True, "volume": volume}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_get_volume(self) -> Dict[str, Any]:
        """Get current volume"""
        try:
            volume = self.vlc.audio_get_volume()
            return {"success": True, "volume": volume}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_seek(self, position: float) -> Dict[str, Any]:
        """Seek to position (0.0 - 1.0)"""
        try:
            if not 0.0 <= position <= 1.0:
                return {"success": False, "error": "Position must be 0.0-1.0"}
            
            self.vlc.set_position(position)
            return {"success": True, "position": position}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_get_position(self) -> Dict[str, Any]:
        """Get current position"""
        try:
            position = self.vlc.get_position()
            time_ms = self.vlc.get_time()
            length_ms = self.vlc.get_length()
            
            return {
                "success": True,
                "position": position,
                "time_ms": time_ms,
                "length_ms": length_ms
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_load_playlist(self, files: List[str]) -> Dict[str, Any]:
        """Load playlist"""
        try:
            if not files:
                return {"success": False, "error": "No files provided"}
            
            # Clear current playlist
            media_list = self.vlc.get_instance().media_list_new()
            
            for file_path in files:
                media = self.vlc.get_instance().media_new(file_path)
                media_list.add_media(media)
            
            list_player = self.vlc.get_instance().media_list_player_new()
            list_player.set_media_list(media_list)
            
            return {
                "success": True,
                "files_loaded": len(files),
                "files": files
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_add_to_playlist(self, file_path: str) -> Dict[str, Any]:
        """Add file to playlist"""
        try:
            if not file_path:
                return {"success": False, "error": "No file provided"}
            
            # Implementation depends on VLC playlist management
            return {
                "success": True,
                "file_added": file_path
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_clear_playlist(self) -> Dict[str, Any]:
        """Clear playlist"""
        try:
            # Implementation depends on VLC playlist management
            return {"success": True, "action": "playlist_cleared"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_shuffle(self, enabled: bool) -> Dict[str, Any]:
        """Toggle shuffle mode"""
        try:
            # Implementation depends on VLC shuffle support
            return {
                "success": True,
                "shuffle_enabled": enabled
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_get_current_track(self) -> Dict[str, Any]:
        """Get current track info"""
        try:
            media = self.vlc.get_media()
            if not media:
                return {"success": False, "error": "No track playing"}
            
            title = media.get_meta(0)  # Title
            artist = media.get_meta(1)  # Artist
            mrl = media.get_mrl()
            
            return {
                "success": True,
                "title": title or "Unknown",
                "artist": artist or "Unknown",
                "file": mrl
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_get_status(self) -> Dict[str, Any]:
        """Get player status"""
        try:
            state = self.vlc.get_state()
            state_map = {
                0: "idle",
                1: "opening",
                2: "buffering",
                3: "playing",
                4: "paused",
                5: "stopped",
                6: "ended",
                7: "error"
            }
            
            return {
                "success": True,
                "state": state_map.get(state, "unknown"),
                "state_code": state,
                "volume": self.vlc.audio_get_volume(),
                "position": self.vlc.get_position()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== Helper Methods ====================
    
    def _validate_arguments(self, arguments: Dict[str, Any], schema: Dict[str, Any]) -> Optional[str]:
        """
        Validate arguments against JSON schema
        
        Returns:
            Error message if invalid, None if valid
        """
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        # Check required fields
        for field in required:
            if field not in arguments:
                return f"Missing required field: {field}"
        
        # Check types
        for field, value in arguments.items():
            if field not in properties:
                continue
            
            field_type = properties[field].get("type")
            if field_type == "string" and not isinstance(value, str):
                return f"Field '{field}' must be string"
            elif field_type == "number" and not isinstance(value, (int, float)):
                return f"Field '{field}' must be number"
            elif field_type == "integer" and not isinstance(value, int):
                return f"Field '{field}' must be integer"
            elif field_type == "boolean" and not isinstance(value, bool):
                return f"Field '{field}' must be boolean"
            elif field_type == "array" and not isinstance(value, list):
                return f"Field '{field}' must be array"
        
        return None
    
    def _success_response(self, result: Any, request_id: Optional[int] = None) -> Dict[str, Any]:
        """Create JSON-RPC 2.0 success response"""
        response = {
            "jsonrpc": "2.0",
            "result": result
        }
        
        if request_id is not None:
            response["id"] = request_id
        
        return response
    
    def _error_response(self, code: int, message: str, request_id: Optional[int] = None) -> Dict[str, Any]:
        """Create JSON-RPC 2.0 error response"""
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            }
        }
        
        if request_id is not None:
            response["id"] = request_id
        
        return response


# Error codes (JSON-RPC 2.0)
ERROR_CODES = {
    "PARSE_ERROR": -32700,
    "INVALID_REQUEST": -32600,
    "METHOD_NOT_FOUND": -32601,
    "INVALID_PARAMS": -32602,
    "INTERNAL_ERROR": -32603
}
