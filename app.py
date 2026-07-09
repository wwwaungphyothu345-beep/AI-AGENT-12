from flask import Flask, request, Response

app = Flask(__name__)

VERIFY_TOKEN = "aung_phyo_thu_12"

# 🌐 Facebook က လှမ်းစစ်မည့် GET Route
@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified successfully!")
        return challenge, 200
    return "Verification token mismatch", 403

# 📥 စာဝင်လာရင် လက်ခံမည့် POST Route (လောလောဆယ် ဘာမှမလုပ်ဘဲ 200 OK ပဲ ပြန်ထားပါမည်)
@app.route('/webhook', methods=['POST'])
def webhook():
    return Response(status=200)

if name == ' __main__ ':
 app.run(host='0.0.0.0', port=5000)
