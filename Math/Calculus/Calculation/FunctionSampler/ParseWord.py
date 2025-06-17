from docx import Document


def read_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    i = 0
    properties_desc = []
    op_examples = []
    while i < len(full_text):
        line = full_text[i]
        if line.strip() == '':
            i += 1
        elif line == '性质列表':
            i += 1
            for _ in range(13):
                properties_desc.append(full_text[i])
                i += 1
        elif line.startswith('运算类型：'):
            i += 1
            prop_examples = []
            for _ in range(13):
                i += 1
                combo_examples = []
                for _ in range(4):
                    i += 1
                    combo_examples.append(full_text[i])
                    i += 1
                prop_examples.append(combo_examples.copy())
            op_examples.append(prop_examples.copy())
    return '\n'.join(full_text)


# 使用示例
text = read_docx(r'C:\Users\16413\Desktop\NPEE\统计\WWII\抽象函数举例.docx')
print(text)
