from .models import *
# import openai
import os

def get_completion(chat, prompt, message, recent_count=0, model="gpt-4"):
    messages = []

    messages.append({"role": "system", "content": prompt})
    messages.append({"role": "user", "content": message})
    openai.api_key = os.environ.get("GPT_TOKEN","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")
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    
    print(response.choices[0].message["content"])
    GPTCall.objects.create(message = chat.messages.last(),prompt = message, system = prompt, response=response.choices[0].message["content"], tokens=response["usage"]["total_tokens"])
    return response.choices[0].message["content"]

def reply_chat(chat_id, text):
    chat = Chat.objects.get(id = chat_id)
    prompt =f"""Act as an agent for a barber reservation website.you are provided with a dataset of frequent questions and answer in persian.\
         when user asks a query,you have to answer it in persian if the answer is in dataset,ilse if answer of question of user is not in dataset, you have to return an apology messgae in persian.\
             You خnly must answer according to provided dataset.you can not add anything besied dataset.you must not answer questions that are not in dataset.below is the dataset between three backticks:\
                 ```
۱. سوال: چطور می‌توانم وقت رزرو کنم؟
پاسخ: برای رزرو وقت، می‌توانید از سایت ما استفاده کنید و یا با شماره تماس مربوطه تماس بگیرید.

۲. سوال: چقدر قبل باید وقت را رزرو کنم؟
پاسخ: برای بهترین خدمات، توصیه می‌شود حداقل ۲۴ ساعت قبل از مورد نظر وقت را رزرو کنید.

۳. سوال: آیا می‌توانم وقت را لغو یا تغییر دهم؟
پاسخ: بله، شما می‌توانید تا ۲۴ ساعت قبل از وقت مورد نظر وقت را لغو یا تغییر دهید.

۴. سوال: چگونه می‌توانم پرداخت کنم؟
پاسخ: ما از روش‌های پرداخت آنلاین و یا پرداخت نقدی در محل خدمت استفاده می‌کنیم.

۵. سوال: آیا امکانات و خدمات ویژه‌ای برای مشتریان وفادار وجود دارد؟
پاسخ: بله، ما برنامه‌های ویژه و تخفیفات برای مشتریان وفادار داریم. برای اطلاعات بیشتر، با ما تماس بگیرید.

۶. سوال: آیا امکان انتخاب آرایشگر مورد نظر وجود دارد؟
پاسخ: بله، شما می‌توانید آرایشگر مورد نظر خود را انتخاب کنید و بر اساس ویژگی‌ها و تجربه‌های آن‌ها انتخاب کنید.

۷. سوال: آیا خدمات اضافی مانند اصلاح و صاف کردن مو ارائه می‌شود؟
پاسخ: بله، علاوه بر خدمات اصلی، ما خدمات اضافی مانند اصلاح و صاف کردن مو نیز ارائه می‌دهیم.

۸. سوال: آیا می‌توانم برای چند نفر وقت رزرو کنم؟
پاسخ: بله، شما می‌توانید برای چند نفر وقت رزرو کنید. لطفاً اطلاعات همراه مشخصات هر نفر را فراهم کنید.

۹. سوال: آیا ارائه خدمات خصوصی برای افراد با نیازهای ویژه وجود دارد؟
پاسخ: بله، ما خدمات خصوصی برای افراد با نیازهای ویژه فراهم می‌کنیم. لطفاً قبل از رزرو با ما تماس بگیرید تا درخواست‌های خاص خود را مطرح کنید.

۱۰. سوال: آیا امکانات انتظار وجود دارد؟
پاسخ: بله، امکانات انتظار در صورت لزوم در دسترس می‌باشد. لطفاً با پرسنل ما تماس بگیرید تا اطلاعات بیشتری دریافت کنید. ```
                    """
    reply = get_completion(chat, prompt, text)
    return reply
