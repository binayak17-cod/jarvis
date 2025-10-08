# SynBi Process Manager

## Overview
The Process Manager allows SynBi to close applications, monitor system processes, and provide system statistics through voice commands.

## Voice Commands

### 🔒 **Close Applications**

#### Direct Application Closing
- **`"close chrome"`** - Closes Google Chrome
- **`"close firefox"`** - Closes Firefox browser
- **`"close spotify"`** - Closes Spotify
- **`"close discord"`** - Closes Discord
- **`"close notepad"`** - Closes Notepad
- **`"close calculator"`** - Closes Calculator
- **`"close youtube"`** - Closes browser tabs with YouTube open
- **`"close explorer"`** - Closes File Explorer

#### Flexible Application Closing
- **`"close application [app name]"`** - Close any application by name
- **`"close app [app name]"`** - Alternative command for closing apps

### 📊 **Process Monitoring**

#### List Running Processes
- **`"list processes"`** - Shows top 10 processes by memory usage
- **`"show processes"`** - Alternative command
- **`"running processes"`** - Another way to request process list

#### System Statistics  
- **`"system stats"`** - Get CPU, memory, and process statistics
- **`"system status"`** - Alternative command
- **`"performance"`** - Shows system performance metrics

## Supported Applications

### 🌐 **Browsers**
- Chrome, Firefox, Edge, Opera, Safari, Brave

### 🎵 **Media & Entertainment**
- Spotify, VLC, Media Player, YouTube (web-based)

### 💬 **Communication**
- Discord, Telegram, WhatsApp, Skype, Zoom, Microsoft Teams

### 📝 **Productivity**
- Notepad, Notepad++, Microsoft Word, Excel, PowerPoint, Outlook

### 💻 **Development**
- VS Code, Visual Studio, PyCharm, Atom, Sublime Text

### 🎮 **Gaming**
- Steam, Epic Games, Origin, Uplay

### 🔧 **System Tools**
- Task Manager, Calculator, Paint, Command Prompt, PowerShell, File Explorer

## Features

### 🎯 **Smart Application Detection**
- Recognizes multiple names for the same application
- Handles both executable names and common aliases
- Special handling for web-based applications like YouTube

### ⚡ **Graceful Process Termination**
- First attempts graceful shutdown
- Falls back to force termination if needed
- Provides detailed feedback on success/failure

### 📈 **System Monitoring**
- Real-time CPU usage
- Memory usage statistics
- Process count and details
- Top memory-consuming processes

### 🌐 **Web Application Support**
- Can close browsers running specific websites
- Handles YouTube, Gmail, Facebook, Twitter, etc.
- Identifies web apps by URL patterns

## Example Usage

### Closing Applications
```
User: "Close Chrome"
SynBi: "Closing chrome... Chrome has been closed successfully."

User: "Close application notepad"
SynBi: "Attempting to close notepad... Notepad has been closed."
```

### System Monitoring
```
User: "System stats"
SynBi: "System Status: CPU usage is 15.3%, Memory usage is 67.2% (10.8 GB of 16.0 GB used), Total running processes: 247"

User: "List processes"
SynBi: "Found 247 processes. Here are the top 10 by memory usage: Chrome using 850.2 megabytes, Firefox using 423.1 megabytes, Discord using 312.7 megabytes..."
```

## Technical Details

### Process Detection
- Uses `psutil` library for cross-platform process management
- Searches by process name and command line arguments
- Maps common application names to their executable files

### Safety Features
- Prevents closing critical system processes
- Provides detailed error messages
- Logs all process management activities

### Performance
- Efficient process enumeration
- Minimal system impact
- Fast application identification and termination

## Error Handling

### Common Scenarios
- **Application not found**: "No running processes found for 'application_name'"
- **Permission denied**: Automatically attempts force termination
- **Application already closed**: Gracefully handles non-existent processes

### Troubleshooting
- Check if application is actually running
- Ensure SynBi has sufficient permissions
- Try the flexible "close application [name]" command for unlisted apps

## Configuration

### Adding New Applications
Edit `process_manager.py` and add entries to the `app_mappings` dictionary:

```python
'myapp': ['myapp.exe', 'my application'],
```

### Web Applications
Add entries to the `web_apps` dictionary for browser-based applications:

```python
'mysite': ['mysite.com', 'www.mysite.com'],
```

## Limitations

- Web applications require the entire browser to be closed (cannot close individual tabs)
- Some system-protected processes may require administrator privileges
- Process detection depends on standard naming conventions

---

## Benefits

✅ **Voice Control**: Close applications hands-free  
✅ **System Monitoring**: Keep track of system performance  
✅ **Multiple Applications**: Support for 30+ common applications  
✅ **Smart Detection**: Handles various names for the same application  
✅ **Safe Operations**: Graceful termination with fallback options  
✅ **Real-time Stats**: Current system performance metrics