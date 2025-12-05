#!/bin/bash

APP_NAME="TextTyper"
APP_DIR="/Applications/$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

PYTHON_PATH="/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
PROJECT_PATH="/Users/captainatw/Documents/GitHub/texttyper"

rm -rf "$APP_DIR"

mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

cat > "$MACOS_DIR/launcher" << EOF
#!/bin/bash
export PATH="/Library/Frameworks/Python.framework/Versions/3.12/bin:\$PATH"
cd "$PROJECT_PATH"
exec "$PYTHON_PATH" main.py
EOF

chmod +x "$MACOS_DIR/launcher"

cat > "$CONTENTS_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.texttyper.app</string>
    <key>CFBundleName</key>
    <string>TextTyper</string>
    <key>CFBundleDisplayName</key>
    <string>TextTyper</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>LSUIElement</key>
    <false/>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

echo "✅ TextTyper.app created in /Applications"
echo "You can now drag it to your Dock!"
echo ""
echo "To test, run: open /Applications/TextTyper.app"
