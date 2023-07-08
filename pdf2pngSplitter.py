import os
import re

import PyPDF2
from pdf2image import convert_from_path

inputDir = "pdfs"
outputPath = "IndexCards"
assignsOutputPath = "assigns"
name_regex = r'(.+)\n'
dpi = 300


def convertToImg(inputPdf):
    images = convert_from_path(inputPdf, dpi, poppler_path=r'poppler-0.68.0/bin')
    dirname = os.path.splitext(os.path.basename(inputPdf))[0]
    output_folder = "IndexCards/{}".format(dirname)
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    if not os.path.exists(assignsOutputPath):
        os.mkdir(assignsOutputPath)
    print("Output folder: ", output_folder)
    for page_number, image in enumerate(images, 1):
        image_path = "{}/{}.jpg".format(output_folder, page_number)
        if os.path.exists(image_path):
            os.remove(image_path)

        image.save(image_path, "JPEG")
        print(f"Page {page_number} saved as {image_path}")


def extract_titles(pdf_path):
    dirname = os.path.splitext(os.path.basename(pdf_path))[0]
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)

        with open(assignsOutputPath + "/" + dirname + ".lua", 'a', encoding='utf-8') as output:
            output.write("local {} = {{\n".format(dirname.lower()))
            title_set = set()
            pattern = r'(.+)\n'
            for page_number in range(6, num_pages):
                title = ''
                page = pdf_reader.pages[page_number]
                text = page.extract_text()
                match = re.search(pattern, text)
                if match:
                    title = match.group(1)
                if title and title not in title_set:
                    print(f"Extracted title {title}")
                    title_set.add(title)
                    formatted_text = """    [\"{}\"] = {{ 
      face = indexPagesUrl .. \"/{}/{}.jpg\",
      back = indexPagesUrl .. \"/{}/{}.jpg\"
   }}""".format(title, dirname, page_number + 1, dirname, page_number + 2)

                    if page_number == num_pages - 1:
                        formatted_text += "\n"
                    else:
                        formatted_text += ",\n"
                    output.write(formatted_text)
            output.write("}\n\n")


def get_title_files():
    return os.listdir(assignsOutputPath)


def print_assignment_list(lua_list):
    file_names = set()
    for lua_name in lua_list:
        name = os.path.splitext(lua_name)[0]
        file_names.add(name.lower())

    joined_string = ', '.join(file_names)
    print("joinedString: " + joined_string)
    return joined_string


def merge_title_files():
    lua_list = get_title_files()
    with open(assignsOutputPath + "/merged.lua", 'w') as target:
        target.write("local indexPagesUrl = \"https://pablosbrodos.github.io/10thIndexCards/IndexCards\"\n\n")
        for lua_name in lua_list:
            with open(assignsOutputPath + "/" + lua_name, 'r') as source:
                target.write(source.read())

        target.write("""
local urlToModel = {{}}
local mainName = "Universal 10th index card"

function onLoad()
    setOwner("")
    urlToModel = mergeTables({})
end
        """.format(print_assignment_list(lua_list)))


file_list = get_title_files()
for file_name in file_list:
    file_path = os.path.join(assignsOutputPath, file_name)
    if os.path.isfile(file_path):
        os.remove(file_path)

for filename in os.listdir(inputDir):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(inputDir, filename)
        print("Processing: ", pdf_path)
        convertToImg(pdf_path)
        extract_titles(pdf_path)

merge_title_files()
