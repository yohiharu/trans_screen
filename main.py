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
from PIL import ImageFont

font_path = "C:/Windows/Fonts/meiryo.ttc"
font_size = 18
font = ImageFont.truetype(font_path, font_size)


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




img = Image.open("my_screenshot.png")
width, height = img.size
print("画像の幅:", width)
print("画像の高さ:", height)





draw = ImageDraw.Draw(img1)


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
        #-------------
        # 座標取得
        if len(vertices) == 4:
            # 矩形の描画
            draw.polygon([
                (vertices[0].x, vertices[0].y),
                (vertices[1].x, vertices[1].y),
                (vertices[2].x, vertices[2].y),
                (vertices[3].x, vertices[3].y)
            ], outline="red", width=1)

            # 描画位置と幅
            x = vertices[0].x
            y = vertices[0].y - 6  # テキストを枠の上に描く（ずれる場合は調整）
            max_width = vertices[1].x - vertices[0].x

            # 折り返し
            wrapped_text = textwrap.fill(translated_text, width=max(1, int(max_width /10)))  # 文字幅調整
            draw.multiline_text((x, max(y, 0)), wrapped_text, fill="blue", font=font)







img1.save("translated_image.png")
img1.show()
