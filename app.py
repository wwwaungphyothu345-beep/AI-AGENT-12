from flask import Flask, request, jsonify

app = Flask(__name__)

# အစ်ကိုကြီး Facebook Developer Console မှာ ပေးခဲ့တဲ့ စာသားကို ဒီမှာ ထည့်ပါ
VERIFY_TOKEN = "EAAz6gX8m3AQBR7vBFVWSZBEi6muLAQI8C8kkl4slZCHXza1VMfoMJrb5qvp8GEZBKKBgG8dHSmXPe976VonZBNgJu2jbyS270923NmrOsZBeZA8s8OYBPBNbDBoG1WjGgVjRBYR8SBl7yqE4Px7p3W1yjEDG7ZBuWRDBLrSMUVjdEtnu4YzWmfSCNpFBo7exfyDVJvDRKB0o66c2z51QaH5srN7ZBxokv6PPOf3QeTPFdojW" 

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # ၁။ Facebook က Webhook လင့်ခ်ကို လာစစ်တဲ့ (Setup လုပ်တဲ့) အပိုင်း
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
                
    # ၂။ စာဝင်လာတဲ့အခါ ဒေတာတက်မတက် စစ်တဲ့အပိုင်း
    elif request.method == 'POST':
        data = request.json
        print("\n📥 --- WEBHOOK DATA RECEIVED ---")
        print(data) # ဝင်လာသမျှ Payload အကုန်လုံးကို Termux မှာ ပြခိုင်းတာ
        print("--------------------------------\n")
        return "EVENT_RECEIVED", 200

if __name__ == '__main__':
     app.run(port=5000, debug=True)
