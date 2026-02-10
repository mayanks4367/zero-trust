#!/usr/bin/env python3
"""
Black Box Vault - Mobile QR Code Application
A polished Kivy-based Android app for displaying QR codes to unlock the vault.
NO-DEPENDENCY VERSION (Removes Pillow/JPEG requirement)
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import qrcode

class VaultKeyApp(App):
    """Main application class for Black Box Vault key display."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.qr_data = "UNLOCK_MY_VAULT_NOW"
        self.title_text = "[b]BLACK BOX VAULT[/b]\n[color=#66ff66]Secure Key System[/color]"
        
    def build(self):
        """Build the main application UI."""
        # Main Layout (Vertical)
        layout = BoxLayout(
            orientation='vertical', 
            padding=[20, 40, 20, 40],  # Top, Right, Bottom, Left padding
            spacing=25
        )
        
        # 1. Title Label with enhanced styling
        title = Label(
            text=self.title_text,
            markup=True, 
            font_size='28sp',
            size_hint=(1, None),
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1),  # White text
            text_size=(None, None),
            line_height=1.2
        )
        
        # 2. QR Code Image Holder with border
        qr_container = BoxLayout(
            size_hint=(1, 0.6),
            padding=10
        )
        
        # Note: allow_stretch=True allows it to scale up while keeping pixel sharpness
        self.qr_image = Image(
            size_hint=(0.8, 0.8),
            allow_stretch=True,
            keep_ratio=True
        )
        
        qr_container.add_widget(self.qr_image)
        
        # 3. Status Label with enhanced styling
        self.status = Label(
            text="[color=#ffff00]● GENERATING TOKEN...[/color]",
            markup=True,
            font_size='18sp',
            size_hint=(1, None),
            halign='center',
            color=(1, 1, 0, 1),  # Yellow text
            bold=True
        )
        
        # 4. Instructions Label
        instructions = Label(
            text="[color=#888888]Show this QR code to the vault guard system[/color]",
            markup=True,
            font_size='14sp',
            size_hint=(1, None),
            halign='center',
            color=(0.8, 0.8, 0.8, 1),  # Gray text
            text_size=(None, None)
        )
        
        # Add widgets to layout
        layout.add_widget(title)
        layout.add_widget(qr_container)
        layout.add_widget(self.status)
        layout.add_widget(instructions)
        
        # Generate QR Code immediately
        Clock.schedule_once(self.generate_qr, 0.1)
        
        return layout

    def generate_qr(self, dt=None):
        """Generate and display QR code using raw matrix (No Pillow needed)."""
        try:
            # 1. Generate the QR Matrix (List of True/False)
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=1, # We handle scaling via Texture, so 1 is fine here
                border=2
            )
            qr.add_data(self.qr_data)
            qr.make(fit=True)
            matrix = qr.get_matrix()
            
            # 2. Convert Matrix to Raw Pixels
            # We build a byte array: White=[255,255,255], Black=[0,0,0]
            # 3 bytes per pixel (RGB)
            buff = bytearray()
            for row in matrix:
                for val in row:
                    if val:
                        # True = Black (The data)
                        buff.extend([0, 0, 0])
                    else:
                        # False = White (The background)
                        buff.extend([255, 255, 255])
            
            # 3. Create a Kivy Texture
            # The size is simply the number of modules (dots) in the QR code
            matrix_dim = len(matrix)
            texture = Texture.create(size=(matrix_dim, matrix_dim), colorfmt='rgb')
            
            # 4. Load the data into the texture
            texture.blit_buffer(bytes(buff), colorfmt='rgb', bufferfmt='ubyte')
            
            # 5. Make it sharp (Nearest Neighbor scaling)
            # This is crucial! It keeps the QR code crisp like pixel art
            # instead of blurry when scaled up on a phone screen.
            texture.mag_filter = 'nearest' 
            texture.min_filter = 'nearest'
            
            # 6. Apply to Image
            self.qr_image.texture = texture
            
            # Update status
            self.status.text = "[color=#00ff00]✓ TOKEN ACTIVE[/color]\n[color=#888888]Ready for scanning[/color]"
            print(f"[+] QR Code generated successfully: {self.qr_data}")
            
        except Exception as e:
            error_msg = f"QR Generation Error: {str(e)}"
            self.status.text = f"[color=#ff4444]✗ ERROR[/color]\n[color=#888888]{error_msg}[/color]"
            print(f"[!] {error_msg}")
            import traceback
            traceback.print_exc()

    def on_start(self):
        print("[*] Black Box Vault Mobile App Started")

    def on_resume(self):
        print("[*] App resumed")
        Clock.schedule_once(self.generate_qr, 0.1)

if __name__ == '__main__':
    VaultKeyApp().run()
