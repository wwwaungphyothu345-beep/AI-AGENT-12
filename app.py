import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- 🔒 ENV VARIABLES (Render တွင် ဖြည့်ထားသော Key များကို ဖတ်ခြင်း) ---
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 🚨 ဆာဗာစတက်ချိန်မှာ Env တွေ တကယ်ဝင်မဝင် Render Log ထဲမှာ လှမ်းပြခိုင်းမည့်အပိုင်း
print("🔍 --- SERVER ENV CHECK ---")
print(f"PAGE_ACCESS_TOKEN တွေ့ရှိမှု: {'✅ ရှိသည်' if PAGE_ACCESS_TOKEN else '❌ မရှိပါ (None)'}")
print(f"VERIFY_TOKEN တွေ့ရှိမှု: {'✅ ရှိသည်' if VERIFY_TOKEN else '❌ မရှိပါ (None)'}")
print(f"GEMINI_API_KEY တွေ့ရှိမှု: {'✅ ရှိသည်' if GEMINI_API_KEY else '❌ မရှိပါ (None)'}")
print("──────────────────────────")

# 🤖 Gemini AI ထံ စာသားလှမ်းပို့သည့် Function
def ask_gemini(user_message):
    # စာမပို့မီ Env ထဲက Key တကယ်ရှိမရှိ ထပ်မံသေချာအောင် စစ်ဆေးခြင်း
    current_key = os.environ.get("GEMINI_API_KEY")
    if not current_key:
        print("❌ Error: GEMINI_API_KEY env variable inside function is missing!")
        return "စနစ်အတွင်း API key လိုအပ်နေပါသည် ဆိုပြီး ပြနေတယ်"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={current_key}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": user_message}]}]}
    
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
    current_token = os.environ.get("PAGE_ACCESS_TOKEN")
    if not current_token:
        print("❌ Error: PAGE_ACCESS_TOKEN env variable inside function is missing!")
        return

    url = f"https://graph.facebook.com/v25.0/me/messages?access_token={current_token}"
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
                            
                            ai_reply = ask_gemini(user_text)
                            send_fb_message(sender_id, ai_reply)
        except Exception as e:
            print(f"❌ Processing Error: {e}")
            
        return "EVENT_RECEIVED", 200

if __name__  == '__main__':
    # Render အတွက် Port နံပါတ်ကို စနစ်တကျ မဖြစ်မနေ သတ်မှတ်ပေးရမည့်အပိုင်း
    port = int(os.environ.

get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
