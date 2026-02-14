#!/usr/bin/env python3
"""
Black Box Vault - Polished UI Version
Look-and-feel update matching the provided target image.
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.lang import Builder
import qrcode
import time
import hmac
import hashlib
import struct

# --- CONFIGURATION ---
SHARED_SECRET = b"MY_SUPER_SECRET_VAULT_KEY"

# --- Kivy Language Styling (KV) ---
# This defines the look and feel: colors, rounded corners, and layout structure.
KV_STYLES = """
#:import hex kivy.utils.get_color_from_hex

# Define Theme Colors
#:set color_bg_dark hex('#1a1c23')
#:set color_bg_light hex('#2b2e3b')
#:set color_white hex('#ffffff')
#:set color_gray hex('#8a8a8a')
#:set color_accent hex('#f5c542') # Yellow/Gold

<RootLayout>:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: color_bg_dark
        Rectangle:
            pos: self.pos
            size: self.size

# Custom Label optimized for the dark theme
<DarkThemeLabel@Label>:
    color: color_white
    markup: True

<SubTextLabel@Label>:
    color: color_gray
    font_size: '14sp'

# The white rounded container for the QR code
<QRContainer@AnchorLayout>:
    anchor_x: 'center'
    anchor_y: 'center'
    padding: dp(20)
    canvas.before:
        Color:
            rgba: color_white
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(15),]

# The visual "scanner brackets" overlay
<ScannerOverlay@Widget>:
    canvas:
        Color:
            rgba: color_accent
        Line:
            width: dp(2)
            # Top Left corner
            points: [self.x, self.top - dp(20), self.x, self.top, self.x + dp(20), self.top]
        Line:
            width: dp(2)
            # Top Right corner
            points: [self.right - dp(20), self.top, self.right, self.top, self.right, self.top - dp(20)]
        Line:
            width: dp(2)
            # Bottom Left corner
            points: [self.x, self.y + dp(20), self.x, self.y, self.x + dp(20), self.y]
        Line:
            width: dp(2)
            # Bottom Right corner
            points: [self.right - dp(20), self.y, self.right, self.y, self.right, self.y + dp(20)]

# Bottom Navigation Item style
<NavItem@BoxLayout>:
    orientation: 'vertical'
    icon_text: ''
    label_text: ''
    is_active: False
    DarkThemeLabel:
        text: root.icon_text
        font_size: '20sp'
        color: color_accent if root.is_active else color_gray
        size_hint_y: 0.6
    DarkThemeLabel:
        text: root.label_text
        font_size: '11sp'
        color: color_accent if root.is_active else color_gray
        size_hint_y: 0.4

# ================= MAIN UI STRUCTURE =================
<MainUI>:
    orientation: 'vertical'
    spacing: dp(10)
    
    # --- TOP SPACER / HEADER ---
    BoxLayout:
        size_hint_y: 0.15
        DarkThemeLabel:
            text: "Place QR Code in the frame"
            font_size: '16sp'
            valign: 'bottom'

    # --- MIDDLE CONTENT (QR AREA) ---
    AnchorLayout:
        size_hint_y: 0.6
        anchor_x: 'center'
        anchor_y: 'center'
        
        # The white rounded box
        QRContainer:
            size_hint: None, None
            size: dp(280), dp(280)
            
            # The actual QR image inside the white box
            Image:
                id: qr_image_widget
                allow_stretch: True
                keep_ratio: True
                size_hint: 0.9, 0.9
                
            # The yellow brackets overlay
            ScannerOverlay:
                size_hint: 0.95, 0.95

    # --- STATUS TEXT AREA ---
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.15
        padding: dp(10)
        DarkThemeLabel:
            id: token_label_widget
            text: "---"
            font_size: '32sp'
            bold: True
        SubTextLabel:
            id: timer_label_widget
            text: "Refreshing..."

    # --- BOTTOM NAVIGATION BAR ---
    BoxLayout:
        size_hint_y: 0.1
        padding: dp(10)
        canvas.before:
            Color:
                rgba: color_bg_light
            Rectangle:
                pos: self.pos
                size: self.size
                
        NavItem:
            icon_text: '[b]L[/b]' # Using fake text icons for simplicity
            label_text: 'Screen'
            is_active: True
        NavItem:
            icon_text: 'G'
            label_text: 'Generate'
        NavItem:
            icon_text: 'H'
            label_text: 'History'
        NavItem:
            icon_text: 'S'
            label_text: 'Settings'
"""
# Load style definitions
Builder.load_string(KV_STYLES)

class RootLayout(BoxLayout):
    pass

class MainUI(RootLayout):
    """The main application layout defined in KV structure above"""
    pass

class VaultKeyApp(App):
    def build(self):
        # Set window size for desktop testing to match phone aspect ratio
        # Window.size = (350, 700) 
        
        # Initialize the main UI defined in KV
        self.root_widget = MainUI()
        
        # Get references to the widgets we need to update via their IDs in KV
        self.qr_image = self.root_widget.ids.qr_image_widget
        self.token_label = self.root_widget.ids.token_label_widget
        self.timer_label = self.root_widget.ids.timer_label_widget
        
        self.last_generated_time_block = 0
        
        # Run the update loop every 1 second
        Clock.schedule_interval(self.update_state, 1)
        # Generate immediately on start
        self.update_state(0)
        
        return self.root_widget

    # --- LOGIC (Same as before) ---
    def get_totp_token(self):
        """Generates a time-based hash valid for 30 seconds"""
        time_block = int(time.time() // 30)
        if time_block == self.last_generated_time_block:
            return None
        self.last_generated_time_block = time_block
        msg = struct.pack(">Q", time_block)
        h = hmac.new(SHARED_SECRET, msg, hashlib.sha256).hexdigest()
        return h[:8].upper()

    def update_state(self, dt):
        # Update Timer Text
        seconds_remaining = 30 - (int(time.time()) % 30)
        self.timer_label.text = f"Refreshing token in: {seconds_remaining}s"
        
        # Check for new token block
        new_token = self.get_totp_token()
        if new_token:
            self.generate_qr(new_token)
            # Update main token text
            self.token_label.text = new_token

    def generate_qr(self, data):
        # Standard "No-Dependency" QR Generation
        # IMPORTANT: border=0 because we are putting it inside a white frame anyway
        qr = qrcode.QRCode(box_size=1, border=0) 
        qr.add_data(data)
        qr.make(fit=True)
        matrix = qr.get_matrix()
        
        buff = bytearray()
        for row in matrix:
            for val in row:
                # Black pixels for data, White for background
                buff.extend([0, 0, 0] if val else [255, 255, 255])
        
        size = len(matrix)
        texture = Texture.create(size=(size, size), colorfmt='rgb')
        texture.blit_buffer(bytes(buff), colorfmt='rgb', bufferfmt='ubyte')
        # Nearest neighbor for sharp pixel look
        texture.mag_filter = 'nearest' 
        self.qr_image.texture = texture

if __name__ == '__main__':
    VaultKeyApp().run()
