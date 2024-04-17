from analyze import get_lexem_list, analyze_lexems


def table_string(data_array):
    max_name_width = max(len(data.name) for data in data_array)
    max_type_width = max(len(data.type) for data in data_array)
    result = ""
    for data in data_array:
        result += f"{data.name.ljust(max_name_width)} | {data.type.ljust(max_type_width)}"+'\n'
    return result


file_path = 'D:/MtranTests/code.txt'
file_path = input("Path to analyzable file: ")

with open(file_path, 'r', encoding='utf-8') as file:
    text = file.read()

all_list, pos_list, error = get_lexem_list(text)
if error:
    exit(0)

# потом сюда вернуть try/except блок
try:
    variables, constants, operators, keywords, lex_list, error = analyze_lexems(all_list, pos_list)
    all_list = lex_list


    print("Variables:")
    print(table_string(variables))
    print()
    print()
    print("Constants:")
    print(table_string(constants))
    print()
    print()
    print("Operators:")
    print(table_string(operators))
    print()
    print()
    keywords = set(keywords)
    print("Keywords:")
    for keyword in keywords:
        print(keyword)
    print()
    print()

    # вывод списка лексем, вывод с замененными идентификаторами

    code_string = ""
    tabcnt = 0
    for i, lex in enumerate(all_list):
        if lex == '{':
            tabcnt += 1
        if lex == '}':
            tabcnt -= 1
        if lex == '{' and (i == 0 or all_list[i-1] not in [']', '=', ',']):
            code_string += '\n'
            for j in range(tabcnt):
                code_string += '\t'
        if lex not in [';', ',', '{', '}']:
            code_string += ' '
        code_string += lex
        if lex in ['{', '}'] and (i+1 == len(all_list) or all_list[i+1] not in [';', '{', '}', ',']):
            code_string += '\n'
            for j in range(tabcnt):
                code_string += '\t'
        if lex == ';' and (i == 0 or all_list[i+1] not in [';', ')']):
            code_string += '\n'
            for j in range(tabcnt):
                code_string += '\t'
    print()
    print()
    print()
    print(code_string)
except:
    exit(0)
