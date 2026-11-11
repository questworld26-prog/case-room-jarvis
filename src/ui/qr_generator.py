"""
QR Code generator utility for projecting the Gradio public URL on classroom screens.
"""

from pathlib import Path

import qrcode

OUTPUT_DIR = Path("./static")
QR_FILE = OUTPUT_DIR / "classroom_qr.png"


# [spec: ADMIN-001]
def generate_qr_code(url: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1E293B", back_color="#FFFFFF")
    img.save(QR_FILE)
    print(f"QR Code generated at: {QR_FILE.resolve()}")
    return QR_FILE
