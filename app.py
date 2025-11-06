from flask import Flask, request, jsonify, render_template
import html

app = Flask(__name__)

# ---------- encode/decode functions (adapted from codul tău) ----------
def encode_text(text: str) -> str:
    encoded = ""
    for i in text:
        if i.lower() in "abcdefghijklmnopqrstuvwxyz":
            idx = "abcdefghijklmnopqrstuvwxyz".index(i.lower())
            code = "123"[idx // 9] + "123"[(idx % 9) // 3] + "123"[idx % 3]
            encoded += code
        elif i == " ":
            encoded += "0"
        elif i.isdigit():
            if i in "123456789":
                idx = "123456789".index(i)
                code = "123"[idx// 3] + "8" + "123"[idx % 3]
                encoded += code
            else:
                encoded += "118"
        elif i in ".?!,-;:@#/%$\\'\"()+-_*=^÷":
            punctuation_codes = {
                '.': '117', '?': '227', '!': '337', ',': '127', '-': '217',
                ';': '237', ':': '317', '@': '711', '#': '712', '/': '713',
                '%': '721', '$': '722', '\\': '723', "'": '171', '"': '272',
                '(': '373', ')': '474', '+': '811', '_': '812', '*': '813',
                '÷': '821', '=': '822', '^': '823'
            }
            encoded += punctuation_codes.get(i, '')
        else:
            # Unicode character encoding
            codepoint = f"{ord(i):X}"
            unicode_code = "791"
            for digit in codepoint:
                unicode_code += encode_text(digit)
            unicode_code += "791"
            encoded += unicode_code

    # Squish transformations
    encoded = encoded.replace("11", "4").replace("22", "5").replace("33", "6")
    return encoded

def decode_text(code: str) -> str:
    code = code.replace("4", "11").replace("5", "22").replace("6", "33").replace("0", "000")
    decoded = ""
    unimode = False
    unichar = ""
    i = 0
    while i < len(code):
        chunk = code[i:i+3]
        if chunk == "000":
            decoded += " "
        elif len(chunk) != 3:
            decoded += ' '
        elif chunk == "791":
            if unimode:
                unimode = False
                unichar = decode_text(unichar)
                try:
                    decoded += chr(int(unichar, 16))
                except:
                    decoded += '�'
                unichar = ""
            else:
                unimode = True
                unichar = ""
        elif unimode:
            unichar += chunk
        elif all(c in "123" for c in chunk):
            idx = (int(chunk[0]) - 1) * 9 + (int(chunk[1]) - 1) * 3 + (int(chunk[2]) - 1)
            if 0 <= idx < 26:
                decoded += "abcdefghijklmnopqrstuvwxyz"[idx]
            else:
                decoded += ' '
        elif chunk[1] == "8":
            idx = (int(chunk[0]) - 1) * 3 + (int(chunk[2]) - 1)
            if 0 <= idx < 9:
                decoded += "123456789"[idx]
            else:
                decoded += ' '
        elif chunk == "118":
            decoded += "0"
        elif chunk in ('117', '227', '337', '127', '217', '237', '317',
                       '711', '712', '713', '721', '722', '723', '171',
                       '272', '373', '474', '811', '812', '813', '821',
                       '822', '823'):
            punctuation_map = {
                '117': '.', '227': '?', '337': '!', '127': ',', '217': '-',
                '237': ';', '317': ':', '711': '@', '712': '#', '713': '/',
                '721': '%', '722': '$', '723': '\\', '171': "'", '272': '"',
                '373': '(', '474': ')', '811': '+', '812': '_', '813': '*',
                '821': '÷', '822': '=', '823': '^'
            }
            decoded += punctuation_map.get(chunk, ' ')
        else:
            decoded += ' '
        i += 3
    return decoded

# -------------------- Flask routes --------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/encode", methods=["POST"])
def api_encode():
    data = request.json or {}
    text = data.get("text", "")
    try:
        res = encode_text(text)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"encoded": res})

@app.route("/api/decode", methods=["POST"])
def api_decode():
    data = request.json or {}
    code = data.get("code", "")
    try:
        res = decode_text(code)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"decoded": res})

if __name__ == "__main__":
    # run local server
    app.run(host='0.0.0.0', port=5000, debug=False)