def ask_gemini(user_message):
    current_key = os.environ.get("GEMINI_API_KEY")
    if not current_key:
        return "စနစ်အတွင်း API key လိုအပ်နေပါသည်"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={current_key}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": user_message}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        
        # 🚨 Google က ပြန်ပေးတဲ့ Error Message အစစ်ကို Log ထဲမှာ လှမ်းထုတ်ကြည့်ရန်
        if 'error' in response_data:
            print(f"❌ Google Gemini API raw error: {response_data['error']}")
            return "Gemini API Key မှားယွင်းနေပုံရပါတယ်ဗျာ။"
            
        bot_response = response_data['candidates'][0]['content']['parts'][0]['text']
        return bot_response
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        return "ခဏလေးနော်ဗျာ၊ စနစ်အတွင်း အမှားအယွင်းတစ်ခု ရှိနေလို့ပါ။"
