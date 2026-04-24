# Metube desktop edition
Windows adapted Metube, with `yt-dlp` version `2026.3.17`

## Dependencies

Make sure you have `Node.js` and `Python >= 3.11` installed.

```bash
# Install python dependencies
pip install -r .requirements.txt

# Install node dependencies from original Metube
cd ui
npm install
```
## Building

```bash
# On folder 'ui'
npm run build
```

```bash
# Once built the ui run `build_ui.py` on root folder
python build_ui.py

# Build python executable
pyinstaller --onefile --hidden-import=engineio.async_drivers.aiohttp app/main.py
```

### Development notes

 The above works on Windows and macOS as well as Linux.
 
 FFMPEG is required to be installed on the system.