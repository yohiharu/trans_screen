import pyautogui
from PIL import Image
import pyocr
import re
from dotenv import load_dotenv
from openai import OpenAI
import os
from google.cloud import vision
from PIL import ImageDraw, ImageFont
import textwrap


load_dotenv()



file_name = "my_screenshot.png"
wh = pyautogui.size()

pyautogui.screenshot(
    file_name,
    region=(0, int(wh.height / 10), int(wh.width / 2), int(wh.height * 8 / 10)),
)
img1 = Image.open(file_name)





username = os.getenv("USERNAME")
pyocr.tesseract.TESSERACT_CMD = (
    "C:/Users/{}/AppData/Local/Programs/Tesseract-OCR/tesseract.exe".format(username)
)
tools = pyocr.get_available_tools()
tool = tools[0]
txt1 = tool.image_to_string(
    img1, lang="jpn+eng", builder=pyocr.builders.TextBuilder(tesseract_layout=6)
)
pattern = r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f\u3000 a-zA-Z0-9。、,\.]"
result = re.findall(pattern, txt1)
result = "".join(result)


def trans(text):
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "user",
                "content": "あなたは日本語の文章を英語に翻訳するプロの翻訳者です。以下の日本語の文章を英語に翻訳してください。翻訳結果以外は一切必要ありません。なお翻訳する文章が無い時は""と出力しなさい\n\n"
                + text,
            }
        ],
    )
    return completion.choices[0].message.content



draw = ImageDraw.Draw(img1)
font = ImageFont.load_default()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./key.json"
client = vision.ImageAnnotatorClient()
with open(file_name, "rb") as image_file:
    content = image_file.read()
image = vision.Image(content=content)
response = client.text_detection(image=image)
for page in response.full_text_annotation.pages:
    for block in page.blocks:
        block_text = ""
        for paragraph in block.paragraphs:
            for word in paragraph.words:
                word_text = ''.join([symbol.text for symbol in word.symbols])
                block_text += word_text + ' '
        block_text = block_text.strip()
        if len(block_text) < 6 and "+" in block_text:
            continue
        print(block_text)
        translated_text = trans(block_text)
        print(translated_text)
        vertices = block.bounding_box.vertices
        print(vertices)
        print("-" * 20)

img1.save("translated_image.png")
img1.show()
