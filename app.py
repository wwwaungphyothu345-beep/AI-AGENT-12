from flask import Flask, request, jsonify, Response
import requests
import json
import os
import gspread
from google.oauth2.service_account import Credentials

app = Flask(name)

# API Keys & Tokens (Render ရဲ့ Environment Variables ထဲက ဖတ်ပါမည်)
GEMINI_KEY = os.environ.get("GEMINI_KEY")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = "aung_phyo_thu_12"

# ⚠️ ဒီနေရာမှာ ကိုယ့်ရဲ့ Google Sheet ID အစစ်ကို သေချာပေါက် ပြောင်းထည့်ပေးပါဗျာ
SHEET_ID = "1CJf69o5Gp_oxtoE7tDog3KPov-ylC0jc67T4XTuFlxU"

# 📊 ၁။ Sheet1 ထဲက ပစ္စည်းစာရင်းကို လှမ်းဖတ်မည့် Function
def get_product_database():
    try:
        GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS")
        if not GOOGLE_CREDENTIALS:
            return "No database configured."
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds_dict = json.loads(GOOGLE_CREDENTIALS)
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        sheet = client.open_by_key(SHEET_ID).sheet1
        records = sheet.get_all_records()
        return json.dumps(records, ensure_ascii=False)
    except Exception as e:
        print("Error reading database:", e)
        return "Error loading database."

# 📝 ၂။ Customer ရဲ့ အချက်အလက်ကို Orders Tab ထဲ သွားသိမ်းမည့် Function
def save_order_to_sheet(user_id, message_text):
    try:
        GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS")
        if not GOOGLE_CREDENTIALS:
            return
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds_dict = json.loads(GOOGLE_CREDENTIALS)
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        sheet = client.open_by_key(SHEET_ID).worksheet("Orders")
        sheet.append_row([user_id, message_text])
        print("Saved to Google Sheet successfully!")
    except Exception as e:
        print("Error saving order:", e)

# 🤖 ၃။ Gemini AI ထံ ပစ္စည်းစာရင်းပါ ပေးပို့မေးမြန်းမည့် Function
def ask_gemini(user_message):
    try:
        product_data = get_product_database()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "contents": [{"parts": [{"text": user_message}]}],
            "systemInstruction": {
                "parts": [{
                    "text": f"မင်းက မြန်မာလို ပြန်လည်ဖြေကြားပေးရမယ့် AI အရောင်းဝန်ထမ်း ဖြစ်သည်။ ဆိုင်တွင်ရှိသော ပစ္စည်းစာရင်းနှင့် ဈေးနှုန်းများမှာ အောက်ပါအတိုင်း ဖြစ်သည်-\n{product_data}\n\nအထက်ပါ စာရင်းပေါ်မူတည်၍ Customer မေးမြန်းသမျှကို ယဉ်ကျေးပျူငှာစွာ မြန်မာလို အတိအကျ ပြန်လည်ဖြေကြားပေးပါ။"
                }]
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print("Gemini Error:", e)
        return "ခဏလေး စောင့်ပေးပါဗျာ။"

# 🌐 ၄။ Facebook Webhook Verification (GET)
@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification token mismatch", 403

# 📥 ၅။ Customer စာပို့ချိန် တုံ့ပြန်မှု (POST)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                if messaging_event.get("message") and messaging_event["message"].get("text"):
                    sender_id = messaging_event["sender"]["id"]
                    user_message = messaging_event["message"]["text"]
                    
                    # Google Sheet (Orders Tab) ထဲ စာရင်းသွင်းသည်
save_order_to_sheet(sender_id, user_message)
                    
                    # Gemini ထံမှ အဖြေတောင်းသည်
                    bot_reply = ask_gemini(user_message)
                    
                    # Customer ထံ စာပြန်သည်
                    fb_url = f"https://graph.facebook.com/v20.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
                    payload = {
                        "recipient": {"id": sender_id},
                        "message": {"text": bot_reply}
                    }
                    requests.post(fb_url, json=payload)
    return Response(status=200)

if name == '__main__':
    app.run(host='0.0.0.0', port=5000)
