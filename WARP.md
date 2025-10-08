# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview
Synbi is a voice-controlled personal assistant built in Python that provides multimedia control, task management, file operations, and system utilities through speech recognition. The assistant uses a modular architecture with specialized modules for different functionalities.

## Core Architecture

### Main Components
- **`Synbi.py`** - Main orchestrator and voice command processing loop
- **`task_manager.py`** - JSON-based task management system with priority handling
- **`spotify_control.py`** - Spotify Web API integration for music control
- **`file_manager.py`** - File system operations with voice confirmation
- **`user.py`** - User credentials and API keys storage
- **Utility modules** - Specialized modules for weather, system control, camera, etc.

### Voice Processing Flow
1. Continuous listening loop in `main_process()`
2. Speech recognition via Google Speech API
3. Natural language command parsing using keyword matching
4. Module delegation based on command type
5. Text-to-speech feedback using pyttsx3

### External API Integrations
- **Spotify Web API** - Music playback control with OAuth2 authentication
- **OpenWeatherMap API** - Weather information retrieval
- **WhatsApp Web** - Automated messaging via Selenium WebDriver
- **Google Speech Recognition** - Voice input processing

## Common Development Commands

### Running the Application
```powershell
python Synbi.py
```

### Installing Dependencies
```powershell
pip install -r requirements.txt
```

### Testing Individual Modules
```powershell
# Test task manager functionality
python -c "from task_manager import *; print(add_task('test task'))"

# Test Spotify integration
python -c "from spotify_control import SpotifyController; sp = SpotifyController(); print(sp.current_playing())"

# Test weather module
python -c "from weather import get_weather; print(get_weather('London'))"
```

### Development Setup
The application requires several API keys to be configured in `user.py`:
- Spotify Client ID/Secret for music control
- OpenWeatherMap API key for weather data
- Gemini API key for potential AI features

## Key Implementation Details

### Task Management System
- Uses JSON persistence in `tasks.json`
- Supports priority levels (high, medium, low)
- Task operations: add, delete, complete, search
- Automatic task ID assignment and completion tracking

### WhatsApp Integration
- Dual approach: Windows app automation + Web-based Selenium
- Complex window focusing logic for reliable automation
- Multiple fallback methods for opening and controlling WhatsApp
- Character-by-character typing for reliability

### File Operations
- Voice confirmation for destructive operations
- Path validation and permission checking
- Support for common folder shortcuts (desktop, documents, etc.)
- Handles both files and directories

### Spotify Control
- OAuth2 authentication flow with redirect handling
- Device detection and active device management
- Complete playback control (play, pause, skip, shuffle, repeat)
- Search functionality for songs and playlists

## Voice Command Categories

### Media Control
- YouTube playback via pywhatkit
- Spotify integration with full control
- Camera operations (photo, video)
- Screenshot capture

### System Operations
- Brightness and volume control
- Battery and system information
- Internet speed testing
- File system operations

### Communication
- WhatsApp messaging automation
- Email client integration
- Contact management via voice

### Productivity
- Task management with priorities
- Calendar integration potential
- Wikipedia and web search
- Voice-activated application launching

## Development Considerations

### Error Handling Patterns
- Multiple retry mechanisms for speech recognition
- Graceful degradation for API failures
- User-friendly error messages via voice feedback
- Fallback methods for automation failures

### Windows-Specific Implementation
- Uses Windows-specific paths for WhatsApp detection
- PowerShell integration for system commands
- Win32 API calls for window management
- Screen automation via pyautogui

### Security Notes
- API keys stored in plaintext in `user.py`
- Spotify credentials embedded in source
- Voice confirmation required for destructive file operations
- No encryption for task data storage

## Testing Strategy
- Manual voice testing is primary validation method
- Individual module testing via Python imports
- API integration testing requires valid credentials
- System automation testing needs active desktop session

## Troubleshooting Common Issues

### Speech Recognition Problems
- Check microphone permissions and default device
- Verify Google Speech API connectivity
- Adjust timeout and phrase limits in `command()` function

### Spotify Integration Issues
- Verify OAuth2 redirect URI configuration
- Check for active Spotify application/device
- Ensure proper scopes in SCOPE constant

### WhatsApp Automation Failures
- Verify WhatsApp Desktop installation path
- Check screen resolution compatibility
- Test window focusing mechanisms individually

### File Operation Permissions
- Run with appropriate user permissions
- Verify path accessibility before operations
- Handle UAC prompts for system operations