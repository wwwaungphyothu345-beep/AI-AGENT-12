import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- 🔒 ENV VARIABLES (Render Settings ထဲတွင် Key & Value ဖြည့်ပေးရန်) ---
# ကုဒ်ထဲမှာ တိုက်ရိုက်မရေးဘဲ OS Environment ကနေ လှမ်းဖတ်ခိုင်းထားပါတယ်
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# ----------------------------------------------------------------------

# 🤖 Gemini AI ထံ စာသားလှမ်းပို့ပြီး အဖြေတောင်းသည့် Function
def ask_gemini(user_message):
    if not GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY env variable is missing!")
        return "စနစ်အတွင်း API Key လိုအပ်နေပါသည်တဗျာ။"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [{"text": user_message}]
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        bot_response = response_data['candidates'][0]['content']['parts'][0]['text']
        return bot_response
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        return "ခဏလေးနော်ဗျာ၊ စနစ်အတွင်း အမှားအယွင်းတစ်ခု ရှိနေလို့ပါ။"

# 💬 Facebook Messenger ထံ စာပြန်ပို့သည့် Function
def send_fb_message(recipient_id, text_to_send):
    if not PAGE_ACCESS_TOKEN:
        print("❌ Error: PAGE_ACCESS_TOKEN env variable is missing!")
        return

    url = f"https://graph.facebook.com/v25.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text_to_send}
    }
    headers = {"Content-Type": "application/json"}
    try:
        res = requests.post(url, headers=headers, json=payload)
        print(f"📤 Responded to {recipient_id}: {res.status_code}")
    except Exception as e:
        print(f"❌ FB Send Error: {e}")

# 🌐 Webhook Endpoints
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # Facebook Webhook Setup စစ်ဆေးသည့်အပိုင်း (GET)
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode and token:
            if mode == 'subscribe' and token == VERIFY_TOKEN:
                print("✅ WEBHOOK VERIFIED SUCCESSFULLY!")
                return challenge, 200
            else:
                return "Verification token mismatch", 403
                
    # စာဝင်လာသည့်အခါ ဖတ်ပြီး AI ဖြင့် ပြန်ဖြေသည့်အပိုင်း (POST)
    elif request.method == 'POST':
        data = request.json
        print("\n📥 --- NEW MESSAGE RECEIVED ---")
        
        try:
            if data.get('object') == 'page':
                for entry in data.get('entry', []):
                    for messaging_event in entry.get('messaging', []):
                        if messaging_event.get('message') and messaging_event['message'].get('text'):
                            sender_id = messaging_event['sender']['id']
                            user_text = messaging_event['message']['text']
                            
                            print(f"💬 User Text: {user_text}")
                            
                            # Gemini ထံ စာသားပို့ပြီး အဖြေတောင်းခံခြင်း
                            ai_reply = ask_gemini(user_text)
                            
                            # ရလာသော အဖြေကို Facebook Messenger ထံ ပြန်ပို့ခြင်း
                            send_fb_message(sender_id, ai_reply)
                            
        except Exception as e:
            print(f"❌ Processing Error: {e}")
            
        return "EVENT_RECEIVED", 200

if __name__  == '__main__':
    # Render ပေါ်တွင် Run နိုင်ရန် port ကို dynamic ဖတ်ခိုင်းထားပါတယ်
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
