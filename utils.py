import pandas as pd
import matplotlib.pyplot as plt
import io, base64

def encode_plot_to_base64(fig, format="png", max_bytes=95000):
    buf = io.BytesIO()
    fig.savefig(buf, format=format, bbox_inches='tight')
    buf.seek(0)
    img_bytes = buf.read()
    buf.close()
    # truncate if needed
    if len(img_bytes) > max_bytes:
        img_bytes = img_bytes[:max_bytes]
    base64_img = base64.b64encode(img_bytes).decode()
    return f"data:image/{format};base64,{base64_img}"
