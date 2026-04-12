#!/usr/bin/env python3
"""
Emoji Steganography: Hide text messages within emoji sequences using zero-width characters.
"""

import sys
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import html

# Zero-width characters for encoding bits
ZWSP = '\u200B'  # Zero-width space (represents '0')
ZWNJ = '\u200C'  # Zero-width non-joiner (represents '1')

def text_to_binary(text):
    """Convert text to binary string using UTF-8 bytes."""
    return ''.join(format(b, '08b') for b in text.encode('utf-8'))

def binary_to_text(binary):
    """Convert binary string back to text using UTF-8 bytes."""
    byte_values = []
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            byte_values.append(int(byte, 2))
    return bytes(byte_values).decode('utf-8', errors='ignore')

def encode(message, cover=''):
    """
    Encode a message into a steganographic emoji string.
    
    Args:
        message (str): The text to hide
        cover (str): Base emoji string to hide in (optional)
    
    Returns:
        str: Steganographic string with hidden message
    """
    cover = cover or '😀'
    
    # Convert message to binary
    binary = text_to_binary(message)
    
    # Create hidden string from binary
    hidden = ''.join(ZWSP if bit == '0' else ZWNJ for bit in binary)
    
    # Distribute hidden characters between emojis
    emojis = list(cover)
    if not emojis:
        return hidden  # If no emojis, just return hidden (though not useful)
    
    result = emojis[0]
    hidden_per_gap = len(hidden) // (len(emojis) - 1) if len(emojis) > 1 else 0
    remainder = len(hidden) % (len(emojis) - 1) if len(emojis) > 1 else len(hidden)
    
    hidden_index = 0
    for i in range(1, len(emojis)):
        # Calculate how many hidden chars to insert here
        chunk_size = hidden_per_gap + (1 if remainder > 0 else 0)
        if remainder > 0:
            remainder -= 1
        
        chunk = hidden[hidden_index:hidden_index + chunk_size]
        hidden_index += chunk_size
        
        result += chunk + emojis[i]
    
    # If there are remaining hidden chars, append them at the end
    if hidden_index < len(hidden):
        result += hidden[hidden_index:]
    
    return result

def decode(stego_text):
    """
    Decode a hidden message from a steganographic emoji string.
    
    Args:
        stego_text (str): The steganographic string
    
    Returns:
        str: The hidden message
    """
    # Extract all zero-width characters
    hidden_bits = ''
    for char in stego_text:
        if char == ZWSP:
            hidden_bits += '0'
        elif char == ZWNJ:
            hidden_bits += '1'
    
    # Convert back to text
    return binary_to_text(hidden_bits)


def build_html_page(message='', cover='😀', encoded='', stego_text='', decoded='', error=''):
    safe_message = html.escape(message)
    safe_cover = html.escape(cover)
    safe_encoded = html.escape(encoded)
    safe_stego = html.escape(stego_text)
    safe_decoded = html.escape(decoded)
    safe_error = html.escape(error)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emoji Hide</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 24px; max-width: 900px; }}
        textarea, input[type=text] {{ width: 100%; font-size: 1rem; margin: 8px 0; padding: 10px; }}
        label {{ font-weight: bold; display: block; margin-top: 16px; }}
        .section {{ border: 1px solid #ddd; padding: 16px; border-radius: 8px; margin-bottom: 24px; }}
        button {{ padding: 10px 16px; font-size: 1rem; }}
        .hint {{ color: #555; font-size: 0.95rem; margin-top: -8px; }}
        .result {{ background: #f7f7f7; border: 1px solid #ddd; white-space: pre-wrap; word-break: break-all; padding: 10px; border-radius: 6px; min-height: 3rem; }}
    </style>
</head>
<body>
    <h1>Emoji Hide</h1>
    <p>Convert text into a single emoji string with hidden zero-width characters, or decode hidden text from an emoji string.</p>

    <div class="section">
        <h2>Encode text</h2>
        <form method="post" action="/encode">
            <label for="message">Text to hide</label>
            <textarea id="message" name="message" rows="4">{safe_message}</textarea>
            <label for="cover">Cover emoji (optional; default is 😀)</label>
            <input id="cover" name="cover" type="text" value="{safe_cover}" placeholder="😀" />
            <button type="submit">Encode</button>
        </form>
        <div class="hint">Copy the encoded output exactly from the box below. It contains hidden characters.</div>
        <div class="result">{safe_encoded}</div>
    </div>

    <div class="section">
        <h2>Decode emoji</h2>
        <form method="post" action="/decode">
            <label for="stego_text">Emoji text with hidden message</label>
            <textarea id="stego_text" name="stego_text" rows="4">{safe_stego}</textarea>
            <button type="submit">Decode</button>
        </form>
        <div class="result">{safe_decoded}</div>
    </div>

    <div class="hint">Open this page at <strong>http://localhost:3000</strong>.</div>
    <div class="hint" style="color:#a00;">{safe_error}</div>
</body>
</html>'''


class EmojiRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(build_html_page().encode('utf-8'))

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        form = parse_qs(body)
        path = urlparse(self.path).path
        try:
            if path == '/encode':
                message = form.get('message', [''])[0]
                cover = form.get('cover', [''])[0] or '😀'
                encoded = encode(message, cover)
                page = build_html_page(message=message, cover=cover, encoded=encoded)
            elif path == '/decode':
                stego_text = form.get('stego_text', [''])[0]
                decoded = decode(stego_text)
                page = build_html_page(stego_text=stego_text, decoded=decoded)
            else:
                self.send_error(404, 'Not found')
                return
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(page.encode('utf-8'))
        except Exception as exc:
            self.send_response(500)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(build_html_page(error=str(exc)).encode('utf-8'))

    def log_message(self, format, *args):
        return


def run_web_interface(port=3000):
    server = HTTPServer(('localhost', port), EmojiRequestHandler)
    print(f'Web interface running at http://localhost:{port}')
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description='Emoji Steganography Tool')
    subparsers = parser.add_subparsers(dest='action', required=True)

    encode_parser = subparsers.add_parser('encode', help='Encode a message')
    encode_parser.add_argument('message', help='Message to encode')
    encode_parser.add_argument('--cover', default='', help='Cover emoji string for encoding (optional)')

    decode_parser = subparsers.add_parser('decode', help='Decode a hidden message')
    decode_parser.add_argument('stego_text', help='Steganographic emoji text to decode')

    serve_parser = subparsers.add_parser('serve', help='Start the web interface on localhost:3000')
    serve_parser.add_argument('--port', type=int, default=3000, help='Port to use for the web interface')

    subparsers.add_parser('test', help='Run a self-test to verify encoding and decoding')

    args = parser.parse_args()

    if args.action == 'encode':
        result = encode(args.message, args.cover)
        print("Encoded message:")
        print(result)
    elif args.action == 'decode':
        result = decode(args.stego_text)
        print("Decoded message:")
        print(result)
    elif args.action == 'serve':
        run_web_interface(args.port)
    elif args.action == 'test':
        sample = 'Hello, emoji steganography!'
        encoded = encode(sample)
        decoded = decode(encoded)
        print('Self-test:')
        print('Original:', sample)
        print('Encoded:', encoded)
        print('Decoded:', decoded)
        if decoded == sample:
            print('Self-test passed.')
        else:
            print('Self-test failed.')

if __name__ == '__main__':
    main()
