import xml.etree.ElementTree as ET

def generate_lt_rules(dictionary_file, output_file):
    """Generates a LanguageTool rules XML file from a list of words."""

    root = ET.Element("ruleset", version="1")

    with open(dictionary_file, 'r', encoding='utf-8') as f:
        for i, word in enumerate(f):
            word = word.strip()
            if word:
                rule = ET.SubElement(root, "rule", id=f"IGNORE_{i+1}", name=f"Игнорировать слово '{word}'")
                pattern = ET.SubElement(rule, "pattern")
                ET.SubElement(pattern, "token", regexp="yes").text = word
                message = ET.SubElement(rule, "message").text = "Это слово разрешено в данном контексте."
                short = ET.SubElement(rule, "short").text = "Разрешенное слово"
                ET.SubElement(rule, "exampleCorrection")
                ET.SubElement(rule, "exception")

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0) # Для красивого форматирования
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    dictionary_file = ".github/languagetool/custom_dict.txt"
    output_file = ".github/languagetool/custom_rules.xml"
    generate_lt_rules(dictionary_file, output_file)
    print(f"Файл правил LanguageTool успешно сгенерирован: {output_file}")
