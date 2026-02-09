from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import qrcode
from io import BytesIO

class VaultKeyApp(App):
    def build(self):
        # Main Layout (Vertical)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # 1. Title Label
        title = Label(text="[b]KERNEL VAULT KEY[/b]", markup=True, font_size='24sp', 
                      size_hint=(1, 0.1), color=(0, 1, 0, 1)) # Matrix Green
        
        # 2. QR Code Image Holder
        self.qr_image = Image(size_hint=(1, 0.7))
        
        # 3. Status Label
        self.status = Label(text="Generating Secure Token...", font_size='16sp',
                            size_hint=(1, 0.1), color=(1, 0, 0, 1)) # Red
        
        layout.add_widget(title)
        layout.add_widget(self.qr_image)
        layout.add_widget(self.status)
        
        # Generate the QR Code immediately
        self.generate_qr()
        
        return layout

    def generate_qr(self):
        # The Secret String (Must match your guard.py)
        data = "UNLOCK_MY_VAULT_NOW"
        
        # Generate QR using python-qrcode library
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to Kivy Texture
        buffer = BytesIO()
        img.save(buffer, format='png')
        buffer.seek(0)
        
        texture = Texture.create(size=img.size)
        texture.blit_buffer(buffer.getvalue(), colorfmt='rgb', bufferfmt='ubyte')
        texture.flip_vertical() # Kivy renders textures upside down by default
        
        self.qr_image.texture = texture
        self.status.text = "● TOKEN ACTIVE"

if __name__ == '__main__':
    VaultKeyApp().run()
