import pyautogui
from PIL import Image
import pyocr
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()


file_name = 'my_screenshot.png'
wh = pyautogui.size()

pyautogui.screenshot(file_name, region=(0, int(wh.height/10), int(wh.width/2), int(wh.height * 8 /10))) 
img1 = Image.open(file_name)

pyocr.tesseract.TESSERACT_CMD = 'C:/Users/81704/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'


tools = pyocr.get_available_tools()
tool = tools[0]

txt1 = tool.image_to_string(
    img1,
    lang='jpn+eng',
    builder=pyocr.builders.TextBuilder(tesseract_layout=6)
)
pattern = r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f\u3000 a-zA-Z0-9。、,\.]'

result = re.findall(pattern, txt1)

result = "".join(result)
print(result)

completion = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {
            "role": "user",
            "content": "あなたは日本語の文章を英語に翻訳するプロの翻訳者です。以下の日本語の文章を英語に翻訳してください。翻訳結果以外は一切必要ありません。\n\n" + result
        }
    ]
)

print()
print(completion.choices[0].message.content)


tool.image_to_string(
    img1,
    lang='jpn+eng',
    builder=pyocr.builders.TextBuilder(tesseract_layout=6)
)