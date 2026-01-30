"""
VLC Tools Registry - JSON Schema Definitions for MCP
Based on xiaozhi-esp32 tool registration pattern

Author: miniZ Team
Version: 1.0.0
Date: 2025-12-11
"""

VLC_TOOLS_REGISTRY = {
    "vlc.play": {
        "description": "Play a file or resume playback",
        "handler": "play",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "Path to media file (optional, if empty will resume current)"
                }
            },
            "required": []
        }
    },
    
    "vlc.pause": {
        "description": "Pause current playback",
        "handler": "pause",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    
    "vlc.stop": {
        "description": "Stop playback completely",
        "handler": "stop",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    
    "vlc.next": {
        "description": "Skip to next track in playlist",
        "handler": "next",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    
    "vlc.previous": {
        "description": "Go back to previous track",
        "handler": "previous",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    
    "vlc.set_volume": {
        "description": "Set volume level (0-100)",
        "handler": "set_volume",
        "inputSchema": {
            "type": "object",
            "properties": {
                "volume": {
                    "type": "integer",
                    "description": "Volume level from 0 (mute) to 100 (max)",
                    "minimum": 0,
                    "maximum": 100
                }
            },
            "required": ["volume"]
        }
    },
    
    "vlc.get_volume": {
        "description": "Get current volume level",
        "handler": "get_volume",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    
    "vlc.seek": {
        "description": "Seek to specific position in track (0.0 = start, 1.0 = end)",
        "handler": "seek",
        "inputSchema": {
            "type": "object",
            "properties": {
                "position": {
                    "type": "number",
                    "description": "Position from 0.0 (start) to 1.0 (end)",
                    "minimum": 0.0,
                    "maximum": 1.0
                }
            },
            "required": ["position"]
        }
    },
    
    "vlc.get_position": {
        "description": "Get current playback position and time",
        "handler": "get_position",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    
    "vlc.load_playlist": {
        "description": "Load multiple files into playlist",
        "handler": "load_playlist",
        "inputSchema": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "description": "Array of file paths to load",
                    "items": {
                        "type": "string"
                    },
                    "minItems": 1
                }
            },
            "required": ["files"]
        }
    },
    
    "vlc.add_to_playlist": {
        "description": "Add single file to current playlist",
        "handler": "add_to_playlist",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "Path to media file to add"
                }
            },
            "required": ["file"]
        }
    },
    
    "vlc.clear_playlist": {
        "description": "Clear all items from playlist",
        "handler": "clear_playlist",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    
    "vlc.shuffle": {
        "description": "Enable or disable shuffle mode",
        "handler": "shuffle",
        "inputSchema": {
            "type": "object",
            "properties": {
                "enabled": {
                    "type": "boolean",
                    "description": "True to enable shuffle, False to disable"
                }
            },
            "required": ["enabled"]
        }
    },
    
    "vlc.get_current_track": {
        "description": "Get information about currently playing track",
        "handler": "get_current_track",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    
    "vlc.get_status": {
        "description": "Get complete player status (state, volume, position)",
        "handler": "get_status",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}


def get_tool_for_gemini(tool_name: str) -> dict:
    """
    Convert tool definition to Gemini function calling format
    
    Args:
        tool_name: Tool name from registry
        
    Returns:
        Gemini-compatible tool definition
    """
    if tool_name not in VLC_TOOLS_REGISTRY:
        return None
    
    tool = VLC_TOOLS_REGISTRY[tool_name]
    
    return {
        "name": tool_name.replace(".", "_"),  # Gemini doesn't like dots in names
        "description": tool["description"],
        "parameters": tool["inputSchema"]
    }


def get_all_tools_for_gemini() -> list:
    """Get all VLC tools in Gemini format"""
    return [
        get_tool_for_gemini(tool_name)
        for tool_name in VLC_TOOLS_REGISTRY.keys()
    ]


# Tool categories for better organization
TOOL_CATEGORIES = {
    "playback": ["vlc.play", "vlc.pause", "vlc.stop", "vlc.next", "vlc.previous"],
    "volume": ["vlc.set_volume", "vlc.get_volume"],
    "seeking": ["vlc.seek", "vlc.get_position"],
    "playlist": ["vlc.load_playlist", "vlc.add_to_playlist", "vlc.clear_playlist", "vlc.shuffle"],
    "info": ["vlc.get_current_track", "vlc.get_status"]
}


def get_tools_by_category(category: str) -> list:
    """Get tools filtered by category"""
    return TOOL_CATEGORIES.get(category, [])
