# Copyright 2026 Sukti Ghosh and Prithis Samaddar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
