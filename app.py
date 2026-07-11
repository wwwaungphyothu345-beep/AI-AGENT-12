import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- 🔒 ENV VARIABLES ---
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# 🤖 OpenAI ထံ စာသားလှမ်းပို့သည့် Function (စောင့်စရာမလို၊ 429 မရှိ)
def ask_openai(user_message):
    current_key = os.environ.get("OPENAI_API_KEY")
    if not current_key:
        return "စနစ်အတွင်း API key လိုအပ်နေပါသည်"

    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {current_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o-mini",  # အမြန်ဆုံးနှင့် အငြိမ်ဆုံး မော်ဒယ်
        "messages": [
            {
                "role": "user",
                "content": str(user_message)
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        
        if 'error' in response_data:
            print(f"❌ OpenAI API raw error: {response_data['error']}")
            return "OpenAI API System Error ဖြစ်ပွားနေပါသည်။"
            
        bot_response = response_data['choices'][0]['message']['content']
        return bot_response
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
        return "ခဏလေးနော်ဗျာ၊ စနစ်အတွင်း အမှားအယွင်းတစ်ခု ရှိနေလို့ပါ။"

# 💬 Facebook Messenger ထံ စာပြန်ပို့သည့် Function
def send_fb_message(recipient_id, text_to_send):
    if not PAGE_ACCESS_TOKEN:
        return
    url = f"https://graph.facebook.com/v25.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text_to_send}}
    headers = {"Content-Type": "application/json"}
    try:
        res = requests.post(url, headers=headers, json=payload)
        print(f"📤 Responded to {recipient_id}: {res.status_code}")
    except Exception as e:
        print(f"❌ FB Send Error: {e}")

# 🌐 Webhook Endpoints
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    current_verify = os.environ.get("VERIFY_TOKEN")
    
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if not mode and not token:
            return "Server is Live! Waiting for Facebook Webhook...", 200
            
        if mode and token:
            if mode == 'subscribe' and token == current_verify:
                print("✅ WEBHOOK VERIFIED SUCCESSFULLY!")
                return challenge, 200
            else:
                return "Verification token mismatch", 403
                
    elif request.method == 'POST':
        data = request.json
        try:
            if data.get('object') == 'page':
                for entry in data.get('entry', []):
                    for messaging_event in entry.get('messaging', []):
                        if messaging_event.get('message') and messaging_event['message'].get('text'):
                            sender_id = messaging_event['sender']['id']
                            user_text = messaging_event['message']['text']
                            
                            # OpenAI ထံမှ အဖြေတောင်းယူခြင်း
                            ai_reply = ask_openai(user_text)
                            send_fb_message(sender_id, ai_reply)
        except Exception as e:
            print(f"❌ Processing Error: {e}")
            
        return "EVENT_RECEIVED", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
