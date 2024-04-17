class var_data:  # класс для хранения данных о переменных
    def __init__(self, name, type, id):
        self.name = name
        self.type = type
        self.id = id

    def __str__(self):
        return self.name + " " + self.type


vartypes = ["int", "long", "short", "byte", "sbyte", "uint", "ulong", "ushort",
            "float", "double", "decimal",
            "bool",
            "char",
            "string",
            "struct",
            "record",
            "enum",
            "object",
            "var",
            "delegate",
            "void"]  # void рассматривается как тип для функций

keywords = ["int", "long", "short", "byte", "sbyte", "uint", "ulong", "ushort", "float", "double", "decimal",
            "bool", "char", "string", "struct", "class", "record", "enum", "object", "var", "delegate", "void",
            "new", "int", "if", "while", "do", "for", "foreach", "public", "protected", "private", 'internal',
            "Stack", "Dictionary", "SortedDictionary", "HashSet", "SortedSet", "LinkedList", "List", "SortedList",
            "Queue", "PriorityQueue", "switch", "case", "continue", "break", "default", "const", "true", "false",
            "null", "return", "yield", "this", "namespace", 'sealed', 'partial']

error = False


def get_lexem_list(text):  # функция возвращает код разбитый на лексемы и массив координат лексем в коде
    global error
    generictypes = ["Stack", "Dictionary", "SortedDictionary", "HashSet", "SortedSet", "LinkedList",
                    "List", "SortedList", "Queue", "PriorityQueue"]

    str_index = 0  # номер символа в файле
    substr_start = 0  # начало текущей подстроки (лексемы)
    line = 1  # реальный номер строки в файле
    col = 1  # реальный столбец в файле
    var_symbols = set('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_')  # символы в названии лексем

    all_list = []
    pos_list = []  # координаты соответсвующей по индексу лексемы из all_list

    generic_depth = 0  # глубина внутри generic типов
    on_array = False # флаг означающий открытые квадратные скобки у типа-массива
    while str_index < len(text):  # выделение лексем типов переменных ,самих переменных и констант, операторов

        # игнорирование однострочных комментариев
        if text[str_index] == '/' and str_index != len(text) - 1 and text[str_index + 1] == '/':
            while str_index < len(text) and text[str_index] != '\n':
                col += 1
                str_index += 1
            substr_start = str_index
            continue

            # строковая/символьная константа
        if text[str_index] in ['\'', '\"'] or \
                str_index+1 != len(text) and text[str_index] in ['@', '$'] and text[str_index+1] == '"':
            if str_index != substr_start:  # начало строки не в начале лексемы
                print(f"Error on {line}:{col}: Invalid \" {text[str_index]} \" symbol (not a string)")
                raise Exception
                break

            if text[str_index] in ['@', '$']:   # специальные строки
                str_index += 1
                col += 1

            raw_string = False           # строки с """
            if str_index+2 < len(text) \
                    and text[str_index] == '"' and text[str_index+1] == '"' and text[str_index+2] == '"':
                raw_string = True

            start_symbol = text[str_index]
            if not raw_string:  # обычная строка
                col += 1
                str_index += 1
                # поиск " без \
                while str_index < len(text) \
                        and not (text[str_index] == start_symbol and text[str_index-1] != '\\'):
                    col += 1
                    if text[str_index] == '\n':
                        col = 1
                        line += 1
                    str_index += 1
            else:   # строка """
                col += 3
                str_index += 3
                while str_index < len(text) and\
                        not(text[str_index] == '"' and text[str_index-1] == '"' and text[str_index-2] == '"'
                            and text[str_index-3] != '\\'):
                    col += 1
                    if text[str_index] == '\n':
                        col = 1
                        line += 1
                    str_index += 1

            if str_index == len(text):
                print(f"Error on {line}:{col}: No closing \"{start_symbol}\"")
                raise Exception
                break
            else:
                if str_index+1 != len(text) and text[str_index+1] not in [" ", ";", ",", "\n", ")",  "}"]:
                    print(f"Error on {line}:{col}: Unexpected \"{text[str_index+1]}\" after string")
                    raise Exception
                    break
                all_list.append(text[substr_start:str_index+1])
                pos_list.append((line, col))
                col += 1
                if text[str_index] == '\n':
                    col = 1
                    line += 1
                str_index += 1
                substr_start = str_index
            continue

        if text[str_index] == '[' and is_vartype(text[substr_start:str_index]):  # открытие скобок в типе-массиве
            on_array = True

        if text[str_index] == ']' and is_vartype(text[substr_start:str_index+1]):
            on_array = False

        if text[str_index] == '<' and text[substr_start:str_index] in generictypes:  # начало generic
            while str_index < len(text):
                if text[str_index] == '>':
                    generic_depth -= 1
                    if generic_depth == 0:
                        break
                if text[str_index] == '<':
                    generic_depth += 1
                col += 1
                if text[str_index] == '\n':
                    col = 1
                    line += 1
                str_index += 1
            all_list.append(text[substr_start:str_index + 1])
            pos_list.append((line, col))
            col += 1
            str_index += 1
            substr_start = str_index
            continue

        # обычный разделитель || разделитель допустимый в generic не внутри generic ||
        # +- и не число вида 10e-1 || ? и не nullable переменная || < и не generic

        if text[str_index] in [';', '\n', '\t', '=', '*', '/', '%', '(', ')', '&', '|', ':', '>', '!', '~', '{', '}'] \
                or text[str_index] in [',', ' '] and not on_array \
                or text[str_index] in ['+', '-'] and text[str_index - 1] not in ['e', 'E'] \
                or text[str_index] == '?' and not is_vartype(text[substr_start:str_index]) \
                or text[str_index] == '<' and text[substr_start:str_index] not in generictypes:

            if str_index - substr_start != 0:  # добавление лексем-операндов (до текущего разделителя)
                all_list.append(text[substr_start:str_index])
                pos_list.append((line, col))
            substr_start = str_index + 1

            # добавление операторов (разделители)
            # операторы из 2 символов
            if text[str_index] in ['+', '-', '|', '&', '>', '<', '?'] and text[str_index] == text[str_index + 1] or \
                    text[str_index] in ['+', '-', '*', '/', '%', '>', '<', '=', '!'] and text[str_index + 1] == '=':
                # ++, --, ...  // +=, -=, ...
                all_list.append(text[str_index:str_index + 2])
                pos_list.append((line, col))
                col += 1
                str_index += 1
                substr_start = str_index + 1
                if str_index >= len(text):
                    break
            # операторы из 1 символа
            elif text[str_index] in [';', '=', '*', '/', ',', '%', '(', ')', '&', '|', '{', '}',
                                     ':', '+', '-', '?', '>', '<', '~', '!']:
                all_list.append(text[str_index])
                pos_list.append((line, col))

        col += 1
        if text[str_index] == '\n':
            line += 1
            col = 1
        str_index += 1

    if str_index - substr_start != 0:   # последняя лексема (если подходит)
        all_list.append(text[substr_start:str_index])
        pos_list.append((line, col))
    return all_list, pos_list, error


var_names = []
const_names = []
class_names = []
operator_names = []
variables = []
constants = []
operators = []
keyword_names = []
function_names = ["Console.WriteLine", "Console.Write", "Console.Read", "Console.ReadLine"]

id_cnt = 1  # счетчик для заменяемого id переменной
index = 0  # переменная для номера лексемы
var_type = ""  # предыдущий тип (для объявления переменных)
rvalue_depth = 0  # содержит глубину вложенности скобок (арифметические и кортежи) в rvalue (также в аргументах)
array_depth = 0  # глубина открытия массивов (для корректного закрытия)
scope_depth = 0  # текущая глубина области видимости


def is_operator(val):  # является ли лексема оператором
    if val in [';', '=', '*', '/', ',', '%', '(', ')', '&', '|', ':', '>', '<', '?', ':', '~', '!',
               '+', '-', '|', '&', '^',
               '>', '<', '?', '++', '--', '||', '&&', '>>', '<<', '??',
               '+=', '-=', '*=', '/=', '%=', '==', '!=']:
        return True
    else:
        return False
    pass


def is_variable(val):  # является ли лексема переменной
    return val in var_names


def is_id(val):  # является ли лексема id переменной
    if val[0] == '<' and val[-1] == '>' and val[1:3] == "id" and val[3:-1].isdigit:
        return True
    return False


def is_constant(val):  # является ли лексема константой-литералом
    if len(val) == 0:    # пустая строка может возникнуть при проверке прошлой лексемы, если ее нет
        return False

    if val == 'null':
        return True

    if val in ["true", "false"]:
        return True

    if val.isnumeric():  # число
        return True

    try:        # число с плавающей точкой (работает на экспоненциальной записи числа)
        float(val)
        return True
    except ValueError:
        pass

    if val[0] == val[-1] and val[0] in ['\'', '\"']:  # символьный/строчный литерал
        return True
    if val[0] in ['@', '$'] and val[1] == val[-1] and val[1] in ['\'', '\"']:  # особый символьный/строчный литерал
        return True
    # многострочный литерал
    if val[0] == "\"" and val[1] == "\"" and val[2] == "\"" and val[-1] == "\"" and val[-2] == "\"" and val[-3] == "\"":
        return True
    return False


def constant_type(val):     # определяет тип константы
    if val == 'null':
        return 'null'

    if val in ["true", "false"]:
        return "bool"

    if val.isdigit():
        return "int"

    if val.isnumeric():
        return "double"

    try:
        float(val)
        return "double"
    except ValueError:
        pass

    if val[0] == val[-1] and val[0] == '\'':
        return "char"
    if val[0] == val[-1] and val[0] == '\"':
        return "string"
    if val[0] in ['@', '$'] and val[1] == val[-1] and val[1] in ['\'', '\"']:  # особый символьный/строчный литерал
        return "string"
    # многострочный литерал
    if val[0] == "\"" and val[1] == "\"" and val[2] == "\"" and val[-1] == "\"" and val[-2] == "\"" and val[-3] == "\"":
        return "string"


def is_generic(val):   # определяет является ли лексема generic типом
    generictypes = ["Stack", "Dictionary", "SortedDictionary", "HashSet", "SortedSet", "LinkedList",
                    "List", "SortedList", "Queue", "PriorityQueue"]
    try:
        split1 = val.split('<', maxsplit=1)
        split2 = split1[1].rsplit('>', maxsplit=1)  # содержит все типы generic (необходимо разьить)

        generic_vars_list = []
        temp = ""
        open_brackets = 0    # угловые скобки считаются для вложенных generic
        open_brackets2 = 0  # круглые скобки считаются для вложенных кортежей
        split3 = split2[0].replace(" ", "")  # удаление пробелов
        for char in split3:     # разбиение на типы с учетом возможной вложенности generic
            if char == ',' and open_brackets == 0 and open_brackets2 == 0:
                generic_vars_list.append(temp)
                temp = ""
            else:
                temp += char
                if char == '<':
                    open_brackets += 1
                elif char == '>':
                    open_brackets -= 1
                elif char == '(':
                    open_brackets2 += 1
                elif char == ')':
                    open_brackets2 -= 1
        generic_vars_list.append(temp)
        correct_types = True
        for word in generic_vars_list:
            if not is_vartype(word):
                correct_types = False
                break

        if len(split1) == 2 and len(split2) == 2 and split1[0] in generictypes and correct_types and split2[1] == '':
            return True
        else:
            return False
    except:
        return False


def is_vartype(val, array_size=False):
    # array_size означает что массивы могут содержать размер (допустимо только при создании через new)

    if len(val) == 0:
        return False

    if val in vartypes:  # примитивный тип
        return True
    if is_generic(val):  # generic тип
        return True
    if val[-1] == '?':  # nullable тип (проверка без знака "?")
        return is_vartype(val[:-1])
    left = val.rfind('[')  # поиск скобок в массиве с конца
    right = val.rfind(']')
    if left != -1 and right != -1 and right > left:     # массив
        inside = val[left+1:right]
        for i in range(len(inside)):    # проверка содержимого между скобками
            if not array_size:
                if inside[i] not in [' ', ',']:
                    break
            else:
                if inside[i] not in " ,123456789":
                    print(inside)
                    break
        return is_vartype(val[:left])   # проверка без "[]"

    # кортеж-тип
    if val[0] == '(' and val[-1] == ')':
        types_str = val[1:-1]       # разбиение аналогичное generic
        types_str = types_str.replace(" ", "")  # удаление пробелов

        tuple_vars_list = []
        temp = ""
        open_brackets = 0  # угловые скобки считаются для вложенных generic
        open_brackets2 = 0  # круглые скобки считаются для вложенных кортежей
        for char in types_str:  # разбиение на типы с учетом возможной вложенности generic
            if char == ',' and open_brackets == 0 and open_brackets2 == 0:
                tuple_vars_list.append(temp)
                temp = ""
            else:
                temp += char
                if char == '<':
                    open_brackets += 1
                elif char == '>':
                    open_brackets -= 1
                elif char == '(':
                    open_brackets2 += 1
                elif char == ')':
                    open_brackets2 -= 1
        tuple_vars_list.append(temp)
        correct_types = True
        for word in tuple_vars_list:
            if not is_vartype(word):
                correct_types = False
                break
        if correct_types:
            return True

    return False


def find_last_by_name(data_list, name):  # вспомогательная функция для поиска последнего элемента с данным именем
    for data in reversed(data_list):
        if data.name == name:
            return data
    return None


def eof_check(all_list):    # проверка на то что файл закончился
    global error
    global index
    if index == len(all_list):  # конец файла
        print(f"Error on EOF: Unexpected EOF")
        raise Exception


# функция выполняющая поиск вправо операнда (через унарные префиксные операторы)
# (нужна для проверки есть ли соответсвующее значение для бинарного и префиксного оператора)
def check_right_for_value(all_list):
    global index
    local_index = index+1  # индекс для поиска операнда
    while True:
        if local_index == len(all_list):  # конец файла при поиске
            print(f"Error on EOF: Unexpected EOF")
            raise Exception
        if is_variable(all_list[local_index]) or is_constant(all_list[local_index]) or all_list[local_index] == '(':
            # значение найдено
            return True
        if all_list[local_index] not in ['++', '--', '+', '-', '~', '!']:
            # не значение и не унарный оператор => правая лексема не соответсвует
            return False
        local_index += 1


def arguments(all_list, pos_list):   # функция отвечающая за анализ аргументов вызова функций/конструкторов
    global error
    global index
    global rvalue_depth
    if all_list[index] != '(':  # начало аргументов с лексемы скобки
        print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}: Expected \"(\" in call arguments ")
        raise Exception
    rvalue_depth += 1
    index += 1
    skip_arguments = False
    # закрытие аргументов конструктора (случай с 0 аргументов, для избежания ситуаций вида "(1,)")
    if all_list[index] == ')':
        skip_arguments = True
        rvalue_depth -= 1
        index += 1

    while True and not skip_arguments:  # значение передаваемое в конструктор
        eof_check(all_list)

        # значение
        rvalue(all_list, pos_list)
        index -= 1   # rvalue при встрече скобок делает шаг вперед, что в данном случае не надо

        # разделители
        if all_list[index] == ',':  # следующий параметр
            index += 1
            continue

        elif all_list[index] == ')':  # закрытие аргументов конструктора
            index += 1
            # функция rvalue уже уменшила вложенность на 1
            break
        else:
            print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}: Incorrect arguments end")
            raise Exception
    return


def new_initialization(all_list, pos_list):  # сегмент отвечающий за обработку инициализации переменной после new
    global error
    global index
    global id_cnt
    eof_check(all_list)  # проверка на то что файл закончился

    if all_list[index] == '(':   # конструкция "new ()"
        new_start_index = index - 1
        new_arguments_start_index = index
        arguments(all_list, pos_list)
        global var_type
        local_new_type = var_type                         # берется из предыдущего объявляения функции
        new_const_name = "new "+local_new_type
        while new_arguments_start_index < index:  # имя константы
            new_const_name += all_list[new_arguments_start_index]
            new_arguments_start_index += 1
        constants.append(var_data(new_const_name, local_new_type, id_cnt))   # добавление константы
        const_names.append(new_const_name)
        del all_list[new_start_index:index]  # замена всех составляющих лексем на один id
        del pos_list[new_start_index + 1:index]
        all_list.insert(new_start_index, f"<id{id_cnt}>")
        index = new_start_index + 1
        id_cnt += 1
        return "_"
    elif not is_vartype(all_list[index], True):  # могут быть массивы с цифрами в скобках
        print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
              f" Expected type after \"new\"")
        raise Exception
    local_new_type = all_list[index]  # тип константы-new
    index += 1
    new_arguments_start_index = index
    array_possible = True
    # у любой переменной вместо аргументов могут быть пустые фигурные скобки
    if index+1 < len(all_list) and all_list[index] == '{' and all_list[index+1] == '}':
        array_possible = False      # после такой конструкции добавлять массив уже нельзя
        index += 2
    # типы-массивы и generic-коллекции могут создаваться без круглых скобок (аргументов)
    elif not ( (local_new_type[-1] == ']' or is_generic(local_new_type) )
               and index+1 != len(all_list) and all_list[index] != '('):
        arguments(all_list, pos_list)

    new_const_name = "new " + local_new_type  # добавление константы созданной с помощью new
    new_start_index = new_arguments_start_index - 2
    while new_arguments_start_index < index:
        new_const_name += all_list[new_arguments_start_index]
        new_arguments_start_index += 1
    if new_const_name not in const_names:   # новая константа
        constants.append(var_data(new_const_name, local_new_type, id_cnt))
        const_names.append(new_const_name)
        del all_list[new_start_index:index]   # замена всех составляющих лексем на один id
        del pos_list[new_start_index+1:index]
        all_list.insert(new_start_index, f"<id{id_cnt}>")
        index = new_start_index+1
        id_cnt += 1
    else:   # не новая константа
        del all_list[new_start_index:index]  # замена всех составляющих лексем на один id
        del pos_list[new_start_index + 1:index]
        # последнее вхождение константы в список констант
        all_list.insert(new_start_index, f"<id{find_last_by_name(constants,new_const_name).id}>")
        index = new_start_index + 1

    # после аргументов может быть массив для значений
    if array_possible and all_list[index] == '{':
        array_content(all_list, pos_list)

    return new_const_name


def array_content(all_list, pos_list):  # обработчик содержимого массива (близко к arguments)
    global error
    global index
    global array_depth
    if all_list[index] != '{':  # начало массива с лексемы скобки
        print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}: Expected array")
        raise Exception
    index += 1
    skip_arguments = False
    # закрытие массива (случай с 0 аргументов, для избежания ситуаций вида "{1,}")
    if all_list[index] == '}':
        skip_arguments = True
        index += 1
        return

    while True and not skip_arguments:  # значение передаваемое в конструктор
        eof_check(all_list)

        # значение
        array_depth+=1
        rvalue(all_list, pos_list)

        # разделители
        if all_list[index] == ',':  # следующий элемент
            index += 1
            continue
        elif all_list[index] == '}':  # закрытие массива
            index += 1
            break
        else:
            print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}: Incorrect array end")
            raise Exception

    if all_list[index] in [';', ','] or (array_depth != 0 and all_list[index] in [';', ',', '}']):
        # корректное завершение массива
        return

    print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}: Expected  \";\" or \",\" after array declaration")
    raise Exception


def tuple_content(all_list, pos_list):  # обработчик содержимого кортежа (близко к массиву)
    # начинает работать с середины (запятой), как только обнаруживается что это кортеж, а не арифметические скобки
    global error
    global index
    global rvalue_depth

    while True:  # значение передаваемое в конструктор
        eof_check(all_list)

        # значение
        rvalue(all_list, pos_list)
        index -= 1  # сдвиг происходит внутри rvalue что не нужно в данном случае

        # разделители
        if all_list[index] == ',':  # следующий элемент
            index += 1
            continue
        elif all_list[index] == ')':  # закрытие кортежа
            index += 1
            break
        else:
            print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}: Incorrect tuple end")
            raise Exception
    return


def suitable_varname(name):  # проверка что имя является допустимым
    if name[0] in '#`':
        return False
    for char in name[1:]:
        if char in '#`@':
            return False
    if name[0] in "0123456789.":
        return False
    if name in keywords:
        return False
    return True


# специальная переменная, означающая что rvalue находится в case и должен заканчиваться на :
case_rvalue = False

def add_operator(val):
    val_type = ""
    if val in ['+', '-', '*', '/', '%']:
        val_type = "arithmetic"
    if val in ['=', '+=', '-=', '*=', '/=', '%=', '++','--']:
        val_type = "assignment"
    if val in ['==', '>=', '<=', '>', '<', '!=', ]:
        val_type = "comparison"
    if val in ['&&', '||', '!']:
        val_type = "logical"
    if val in ['~', '>>', '<<', '|', '&', '^']:
        val_type = "bit"
    if val in [';', '{', '}', ',', '(', ')']:
        val_type = "separator"
    if val in ['?', ':']:
        val_type = "ternary"
    if val in ['??']:
        val_type = "null-coalescing"
    if val in ['if', 'else', 'switch']:
        val_type = "conditional"
    if val in ['do', 'while', 'for', 'foreach', 'break', 'continue']:
        val_type = "loop"
    if val in ['new']:
        val_type = "new"
    if val not in operator_names:
        operator_names.append(val)
        operators.append(var_data(val, val_type, None))


def rvalue(all_list, pos_list):   # обработчик выражений
    # функция отвечающая за анализ сегментов справа от =, +=, ...; значений аргументов функций
    global error
    global rvalue_depth
    global array_depth
    global index
    global id_cnt

    ternary_opened = 0   # кол-во открытых тернарных операторов
    lexem_before = ""  # последняя предшествующая лексема (оператор или операнд)
    operand_before = ""  # _ означает результат функции (некоторые операторы применимы только к переменным)
    operator_before = ""
    while True:
        eof_check(all_list)  # проверка на то что файл закончился

        if all_list[index] in [';']:  # конец строки/выражения, выход из функции
            add_operator(all_list[index])
            if rvalue_depth != 0:   # ; в вложенных скобках
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}: \"{all_list[index]}\" instead of \")\"")
                raise Exception
            # не были встречены операнды для rvalue (пустые скобки или только унарные операторы)
            if lexem_before == "":
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}: Expected value for assignment")
                raise Exception
            break

        if all_list[index] == ',':  # либо следующее объявление переменной либо кортеж
            add_operator(all_list[index])
            if rvalue_depth == 0:   # нулевая вложенность - не кортеж
                if lexem_before == "":
                    print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}: Expected value for assignment")
                    raise Exception
                break
            else:       # кортеж
                index += 1
                tuple_content(all_list, pos_list)
                continue

        if is_variable(all_list[index]) or is_constant(all_list[index]):  # встречен операнд
            if is_variable(lexem_before) or is_constant(lexem_before) or lexem_before == '_':
                # 2 значения подряд - некорректный порядок лексем
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}: Unexpected operand")
                raise Exception
            else:
                if is_constant(all_list[index]):
                    global const_names
                    if all_list[index] not in const_names:  # новая встреченная константа
                        constants.append(var_data(all_list[index], constant_type(all_list[index]), id_cnt))
                        const_names.append(all_list[index])
                        all_list[index] = f"<id{id_cnt}>"  # замена на id
                        id_cnt += 1
                    else:   # повтор константы
                        all_list[index] = f"<id{find_last_by_name(constants,all_list[index]).id}>"  # замена на id
                else:   # старая переменная
                    all_list[index] = f"<id{find_last_by_name(variables,all_list[index]).id}>"  # замена на id
                operand_before = all_list[index]
                lexem_before = all_list[index]
                index += 1
                continue

        # начало массива-константы
        if all_list[index] == '{':
            add_operator(all_list[index])
            if lexem_before != "":  # массив используются с другими операторами (запрещено синтаксисом)
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}: Array not allowed")
                raise Exception
            array_content(all_list, pos_list)   # должно заканчиваться на ; поэтому можно выходить из rvalue
            return

        if all_list[index] == '}':
            add_operator(all_list[index])
            if array_depth == 0:
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}: Unexpected \"{{\" (not array end)")
                raise Exception
            else:
                array_depth -= 1
                return

        # унарные операторы с постфиксной и префиксной версией (могут применяться только к переменным)
        if all_list[index] in ['++', '--']:
            if index > 0 and is_id(lexem_before):  # постфиксный оператор (перед ним id)
                add_operator(all_list[index])
                lexem_before = '_'
                operand_before = '_'
                index += 1
                continue
            elif index + 1 != len(all_list) and is_variable(all_list[index + 1]):  # префиксный оператор
                add_operator(all_list[index])
                lexem_before = '_'
                index += 2
                continue
            else:
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}: No matching variable")
                raise Exception

        # бинарные операторы присваивания
        if all_list[index] in ['=', '+=', '-=', '*=', '/=', '%=']:
            add_operator(all_list[index])
            if not is_id(lexem_before): #id-переменная до этого
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}: "
                      f"Assignment to non-variable \"{lexem_before}\"")
                raise Exception
            else:
                index += 1
                rvalue(all_list, pos_list)  # рекурсивный вызов, т.к правая часть должна быть rvalue
                continue

        # унарные префиксные операторы (предшествующая лексема - оператор или отсутствует)
        if all_list[index] in ['+', '-', '~', '!'] and (is_operator(lexem_before) or lexem_before == ""):
            add_operator(all_list[index])

            # справа от унарного оператора должна быть лексема-операнд или еще 1 унарный оператор
            if index + 1 < len(all_list) and check_right_for_value(all_list):   # имеется правый операнд
                lexem_before = all_list[index]
                index += 1
                continue
            else:
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected operand after \"{all_list[index]}\"")
                raise Exception
            pass

        # бинарные операторы
        if all_list[index] in ['+', '-', '*', '/', '%', '==', '>', '<', '>=', '<=', '!=', '&&', '||',
                               '&', '|', '^', '>>', '<<', '??']:
            add_operator(all_list[index])
            if lexem_before == "":  # не было соответствующего левого операнда
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected operand before \"{all_list[index]}\"")
                raise Exception

            if index + 1 < len(all_list) and check_right_for_value(all_list):   # имеется правый операнд
                lexem_before = all_list[index]
                index += 1
                continue
            else:
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected operand after \"{all_list[index]}\"")
                raise Exception
            pass

        if all_list[index] == ')':  # выход из выражения внутри скобок
            add_operator(all_list[index])
            if rvalue_depth == 0:
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Unexpected \")\"")
                raise Exception
            if lexem_before == "":
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Empty \"()\"")
                raise Exception
            rvalue_depth -= 1
            index += 1
            return

        if all_list[index] == '(':  # значения внутри скобок в rvalue тоже всегда должны быть rvalue
            add_operator(all_list[index])
            # случай когда скобки - аргументы функции
            if all_list[index-1] in function_names or is_id(all_list[index-1]):
                arguments(all_list,pos_list)
                continue
            # перед скобками обязательно должен быть оператор либо ничего
            if not is_operator(lexem_before) and lexem_before != "":
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" \"(\" after value")
                raise Exception
            rvalue_depth += 1
            index += 1
            rvalue(all_list, pos_list)
            lexem_before = '_'  # после коррекной обработки скобок они считаются за предшествующее значение
            continue

        # new (далее идет конструктор типа) - можно рассматривать как цельную константу
        if all_list[index] == 'new':
            add_operator(all_list[index])
            index += 1
            lexem_before = new_initialization(all_list, pos_list)
            continue

        # тернарный оператор
        if all_list[index] == '?':
            add_operator(all_list[index])
            lexem_before = '?'
            ternary_opened += 1
            index += 1
            continue

        if all_list[index] == ':':
            add_operator(all_list[index])
            if ternary_opened == 0 and case_rvalue == True:
                return
            if ternary_opened == 0:
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Unexpected \":\" without matching \"?\" beforehand")
                raise Exception
            else:
                # после : должно быть значение, т.е по сути бинарный оператор
                if index + 1 < len(all_list) and check_right_for_value(all_list):  # имеется правый операнд
                    lexem_before = ':'
                    ternary_opened -= 1
                    index += 1
                    continue
                else:
                    print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                          f" Expected operand after \"{all_list[index]}\"")
                    raise Exception

        # обработчик остальных лексем (неожиданная лексема)
        print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
              f" Unexpected \"{all_list[index]}\"")
        raise Exception


def var_initalization(all_list, pos_list):  # функция отвечающая за анализ сегментов инициализации переменных
    global index
    global var_type
    global error
    global id_cnt

    while True:
        eof_check(all_list)
        if suitable_varname(all_list[index]):    # имя объявляемой переменной корректное
            variables.append(var_data(all_list[index], var_type, id_cnt))
            var_names.append(all_list[index])
            all_list[index] = f"<id{id_cnt}>"  # замена на id
            id_cnt += 1
        else:
            print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                  f" Invalid variable name \"{all_list[index]}\"")
            raise Exception
        index += 1
        eof_check(all_list)

        if all_list[index] == '=':  # присваивание значения к переменой (переход к проверке rvalue выражений)
            add_operator(all_list[index])
            index += 1
            rvalue(all_list, pos_list)

        if all_list[index] == ';':  # конец строки
            add_operator(all_list[index])
            index += 1
            var_type = ""
            return
        elif all_list[index] == '{':    # может идти после объявления переменных классов, структур...
            add_operator(all_list[index])
            index += 1
            var_type = ""
            return
        elif all_list[index] == ',':  # следующая переменная с тем же типом (рекурсивный вызов)
            add_operator(all_list[index])
            index += 1
            var_initalization(all_list, pos_list)
            return
        else:  # ни один из ожидаемых идентификаторов
            print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}: Unexpected identifier \"{all_list[index]}\" ")
            raise Exception


def func_initalization(all_list, pos_list):  # функция отвечающая за анализ сегментов инициализации переменных
    global index
    global var_type
    global error
    global id_cnt
    func_name = ""
    func_args = []
    name_index = 0

    eof_check(all_list)
    if suitable_varname(all_list[index]):  # имя объявляемой функции корректное (запоминается)
        func_name = all_list[index]
        name_index = index

    else:
        print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
              f" Invalid function name \"{all_list[index]}\"")
        raise Exception
    index += 1
    eof_check(all_list)
    if all_list[index] == '(':
        add_operator(all_list[index])
        index += 1
    else:
        print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
              f" Expected \"(\" in function declaration")
        raise Exception
    eof_check(all_list)
    argument_line = "("
    # обработка типов аргументов функций
    while True:

        # окончание списка аргументов
        if all_list[index] == ')':
            add_operator(all_list[index])
            argument_line += ')'
            index += 1
            # добавление функции как переменной
            variables.append(var_data(func_name, var_type+argument_line, id_cnt))
            var_names.append(func_name)
            all_list[name_index] = f"<id{id_cnt}>"
            id_cnt += 1
            function_names.append(func_name)  # позволяет обрабатывать вызов новой функции
            # далее { или ; что обрабатывается в общем анализаторе
            return

        eof_check(all_list)

        # тип
        if is_vartype(all_list[index]):
            argument_line += all_list[index]+" "
            index += 1
        else:
            print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                  f" Expected variable type in function declaration")
            raise Exception

        eof_check(all_list)

        # имя
        if suitable_varname(all_list[index]):
            argument_line += all_list[index]
            index += 1
        else:
            print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                  f" Expected variable name in function declaration")
            raise Exception

        # следующий аргумент
        if all_list[index] == ',':
            add_operator(all_list[index])
            argument_line += ", "
            index += 1
            continue


def analyze_lexems(all_list, pos_list):  # функция входа в анализ набора лексем, обрабатывает начала выражений
    global index
    global var_type
    global error
    global rvalue_depth
    global id_cnt


    while index < len(all_list):  # цикл анализа лексем (для начала строки)
        eof_check(all_list)  # проверка на то что файл закончился

        # переход на следущую строку
        if all_list[index] == ';':
            add_operator(all_list[index])
            index += 1
            continue

        if all_list[index] == 'using':
            keyword_names.append(all_list[index])
            if index + 2 < len(all_list) and suitable_varname(all_list[index+1]) and all_list[index+2] == ';':
                index += 2
                continue
            else:
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Incorrect \"using\" syntax")
                raise Exception

        # после const может быть только объявление переменной
        if all_list[index] == 'const':
            keyword_names.append(all_list[index])
            index += 1
            if is_vartype(all_list[index]):
                var_type = all_list[index]
                index += 1
                var_initalization(all_list, pos_list)
                continue
            else:
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected type after const")
                raise Exception

        # встречен модификатор доступа
        if all_list[index] in ['public', 'private', 'protected', 'internal']:
            keyword_names.append(all_list[index])
            # перед модификатором функции или типом (функции или переменной)
            if index+1 < len(all_list) and ( (all_list[index+1] in
                     ['abstract', 'override', 'virtual', 'static'] or is_vartype(all_list[index+1])) ):
                index += 1
                continue
            else:
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Unexpected \"{all_list[index]}\" modifier")
                raise Exception

        # модификаторы классов
        if all_list[index] in ['abstract', 'sealed', 'partial', 'static']:
            keyword_names.append(all_list[index])
            if index + 1 < len(all_list) and all_list[index+1] == 'class':
                index += 1
                continue
            else:
                if all_list[index] not in ['abstract', 'static']:  # это также могут быть модификаторы функций
                    print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                          f" Unexpected \"{all_list[index]}\" modifier")
                    raise Exception

        # модификаторы функции
        if all_list[index] in ['abstract', 'override', 'virtual', 'static']:
            keyword_names.append(all_list[index])
            # перед модификатором функции или типом функции + аргументами функции
            if index+3 < len(all_list) and (all_list[index+1] in ['abstract', 'override', 'virtual', 'static']
                                              or is_vartype(all_list[index+1]) and all_list[index+3] == '('):
                index += 1
                continue
            else:
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Unexpected \"{all_list[index]}\" modifier")
                raise Exception

        # объявление переменной
        if is_vartype(all_list[index]):
            var_type = all_list[index]
            index += 1
            if index + 1 < len(all_list) and all_list[index+1] == '(':   # объявление функции
                func_initalization(all_list, pos_list)
            else:
                var_initalization(all_list, pos_list)
            continue

        # начало с "(" возможно тип-кортеж объявляющий переменную
        if all_list[index] == '(':
            add_operator(all_list[index])
            tuple_depth = 1
            tuple_start = index
            index += 1
            while True:
                if index == len(all_list):
                    print(f"Error on {pos_list[tuple_start][0]}:{pos_list[tuple_start][1]}:"
                          f" No closure for tuple")
                    raise Exception
                if all_list[index] == '(':
                    tuple_depth += 1
                if all_list[index] == ')':
                    tuple_depth -= 1
                if tuple_depth == 0:
                    break
                index += 1
            tuple_str = "".join(all_list[tuple_start:index+1])
            if is_vartype(tuple_str):
                var_type = tuple_str
                index += 1
                var_initalization(all_list, pos_list)
                continue
            else:
                print(f"Error on {pos_list[tuple_start][0]}:{pos_list[tuple_start][1]}:"
                      f" \"(\" in the begining of line only available for valid tuple types")
                raise Exception

        # вызов функции
        if all_list[index] in function_names:
            if all_list[index] in var_names:    # функция объявленная пользователем - переменная
                all_list[index] = f"<id{find_last_by_name(variables, all_list[index]).id}>"
            index += 1
            arguments(all_list, pos_list)
            continue

        # существующая переменная
        if all_list[index] in var_names:
            all_list[index] = f"<id{find_last_by_name(variables, all_list[index]).id}>"  # замена на id
            index += 1
            eof_check(all_list)
            if all_list[index] in ['--', '++']:  # допускается использование ++/-- как выражения
                index += 1
                if all_list[index] == ';':
                    add_operator(all_list[index])
                    index += 1
                    continue
                else:
                    print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                          f" Expected \";\" after \"{all_list[index-1]}\"")
                    raise Exception

            # не присваивание к существующей переменной
            elif all_list[index] not in ['=', '+=', '-=', '*=', '/=', '%=']:
                add_operator(all_list[index])
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Usage of operator \"{all_list[index]}\" not allowed as statement")
                raise Exception
            else:
                index += 1
                rvalue(all_list, pos_list)
                continue

        # строка начинается с new
        if all_list[index] == "new":
            add_operator(all_list[index])
            index += 1
            new_initialization(all_list, pos_list)
            continue

        # оператор if
        if all_list[index] == "if":
            add_operator(all_list[index])
            index += 1
            eof_check(all_list)
            if all_list[index] != '(':
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected \"(\" after \"if\" ")
                raise Exception
            add_operator(all_list[index])
            index += 1
            rvalue_depth += 1
            rvalue(all_list, pos_list)  # выход произойдет при встрече финальной скобки if
            # далее 1 выражение или {} что обрабатывается этим же анализатором
            continue

        if all_list[index] == "else":
            add_operator(all_list[index])
            # после else должно быть содержимое (обрабатывается этим же анализатором)
            index += 1
            eof_check(all_list)
            continue

        # открытие различных областей видимости (не важно для лексического анализа)
        if all_list[index] in ['{', '}']:
            add_operator(all_list[index])
            index += 1
            continue

        if all_list[index] == 'for':
            add_operator(all_list[index])
            index += 1
            eof_check(all_list)
            if all_list[index] != '(':
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected \"(\" after \"for\" ")
                raise Exception
            add_operator(all_list[index])
            index += 1
            eof_check(all_list)
            # первое выражение - утверждение (объявление/присваивание/вызов/new)
            if all_list[index] != ';':  # пропуск первого блока
                if is_vartype(all_list[index]):     # объявление переемнной
                    var_type = all_list[index]
                    index += 1
                    var_initalization(all_list, pos_list)
                    index -= 1
                elif is_variable(all_list[index]):  # присваивание
                    index += 1
                    eof_check(all_list)
                    if all_list[index] in ['--', '++']:
                        index += 1
                    elif all_list[index] not in ['=', '+=', '-=', '*=', '/=', '%=',]:
                        print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                              f" Expected assignment after \"{all_list[index-1]}\", got \"{all_list[index ]}\"  ")
                        raise Exception
                    else:
                        index += 1
                        rvalue(all_list, pos_list)
                elif all_list[index] in function_names:   # вызов
                    index += 1
                    arguments(all_list, pos_list)
                elif all_list[index] == 'new':  # new
                    index += 1
                    new_initialization(all_list, pos_list)
                else:
                    print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                          f" Unexpected  {all_list[index]} inside \"for\"")
                    raise Exception
                # проверка что закончилось на ; а не другом символе
                if all_list[index] != ';':
                    print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                          f" Expected  \";\" inside \"for\", not {all_list[index]} ")
                    raise Exception
                index += 1
            else:
                index += 1
            # второе выражение - условие (rvalue)
            if all_list[index] != ';':  # пропуск второго блока
                rvalue(all_list, pos_list)
                index += 1
                # проверка что rvalue закончилось на ; а не другом символе
                if all_list[index-1] != ';':
                    print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                          f" Expected  \";\" inside \"for\", not {all_list[index - 1]} ")
                    raise Exception
            else:
                index += 1
            # третье выражение - утверждение (присваивание/вызов/new)
            if all_list[index] != ')':  # пропуск третьего блока
                if is_vartype(all_list[index]):  # объявление переемнной
                    var_type = all_list[index]
                    index += 1
                    var_initalization(all_list, pos_list)
                    index -= 1
                elif is_variable(all_list[index]):  # присваивание
                    all_list[index] = f"<id{find_last_by_name(variables, all_list[index]).id}>"  # замена на id
                    index += 1
                    eof_check(all_list)
                    if all_list[index] in ['--', '++']:
                        index += 1
                    elif all_list[index] not in ['=', '+=', '-=', '*=', '/=', '%=', ]:
                        print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                              f" Expected assignment after \"{all_list[index - 1]}\", got \"{all_list[index ]}\" ")
                        raise Exception
                    else:
                        index += 1
                        rvalue_depth += 1  # увеличение глубины на 1 т.к заканчивается на )
                        rvalue(all_list, pos_list)
                        index -= 1  # смещение происходит внутри rvalue, что не нужно для дальнейшей проверки

                elif all_list[index] in function_names:  # вызов
                    index += 1
                    arguments(all_list, pos_list)
                elif all_list[index] == 'new':  # new
                    index += 1
                    new_initialization(all_list, pos_list)
                else:
                    print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                          f" Unexpected  {all_list[index]} inside \"for\"")
                    raise Exception
                # проверка что закончилось на ) а не другом символе
                if all_list[index] != ')':
                    print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                          f" Expected  \")\" inside \"for\", not {all_list[index]} ")
                    raise Exception
                index += 1
            else:
                index += 1
            # далее {} или выражение оба обрабатываются данным анализатором
            continue

        if all_list[index] == 'foreach':
            add_operator(all_list[index])
            # foreach ( тип имя in имя ){}
            index += 1
            eof_check(all_list)
            if all_list[index] != '(':
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected \"(\" after \"foreach\" ")
                raise Exception
            add_operator(all_list[index])
            index += 1
            eof_check(all_list)
            if not is_vartype(all_list[index]):
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected variable type in \"foreach\" ")
                raise Exception
            index += 1
            eof_check(all_list)
            if not suitable_varname(all_list[index]):
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected variable in \"foreach\" ")
                raise Exception
            variables.append(var_data(all_list[index], all_list[index-1], id_cnt))   # новая переменная                     #id_cnt
            var_names.append(all_list[index])
            all_list[index] = f"<id{id_cnt}>"  # замена на id
            id_cnt += 1

            index += 1
            eof_check(all_list)
            if all_list[index] != 'in':
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected \"i\" in \"foreach\" ")
                raise Exception
            keyword_names.append(all_list[index])
            index += 1
            eof_check(all_list)
            if not is_variable(all_list[index]):
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected collection in \"foreach\" ")
                raise Exception
            all_list[index] = f"<id{find_last_by_name(variables, all_list[index]).id}>"
            index += 1
            eof_check(all_list)
            if all_list[index] != ')':
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected \")\" after \"foreach\" ")
                raise Exception
            index += 1
            continue

        # начало цикла do...while
        if all_list[index] == 'do':
            add_operator(all_list[index])
            index += 1
            eof_check(all_list)

            if all_list[index] != '{':
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected \"{{\" after \"do\" ")
                raise Exception
            continue

        # while (либо начало цикла либо конец)
        if all_list[index] == 'while':
            add_operator(all_list[index])
            index += 1
            eof_check(all_list)

            if all_list[index] != '(':
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected \"(\" after \"while\" ")
                raise Exception
            add_operator(all_list[index])
            index += 1
            eof_check(all_list)
            if all_list[index] != ')':
                rvalue_depth += 1
                rvalue(all_list, pos_list)  # внутри условие - rvalue
                if all_list[index-1] != ')':
                    print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                          f" Expected \")\" after \"while\" ")
                    raise Exception
                add_operator(")")
            else:
                add_operator(all_list[index])
                index += 1
            continue

        if all_list[index] in ['break', 'continue']:
            add_operator(all_list[index])
            index += 1
            eof_check(all_list)
            if all_list[index] != ';':
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected  \";\" after \"{all_list[index]}\"")
                raise Exception
            continue

        # объявление класса
        if all_list[index] == 'class':
            keyword_names.append(all_list[index])
            index += 1
            eof_check(all_list)
            if suitable_varname(all_list[index]):  # имя объявляемой переменной корректное
                var_names.append(all_list[index])
                class_names.append(all_list[index])
                variables.append(var_data(all_list[index], "class", id_cnt))
                all_list[index] = f"<id{id_cnt}>"  # замена на id
                id_cnt += 1
            var_type = all_list[index]
            index += 1
            if all_list[index] == ':':  # обработка наследования
                index += 1
                eof_check(all_list)
                if all_list[index] not in class_names:
                    print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                          f" Expected class after \":\"")
                    raise Exception
                # замена id для наследуемого класса
                all_list[index] = f"<id{find_last_by_name(variables, all_list[index]).id}>"
                index += 1
            continue

        if all_list[index] in ['yield', 'return']:
            keyword_names.append(all_list[index])
            index += 1
            rvalue(all_list, pos_list)  # возвращает некоторое численное значение
            if all_list[index] != ';':  # проверка, что после значения есть ;
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected \";\" after value")
                raise Exception
            continue

        # switch
        if all_list[index] == 'switch':
            add_operator(all_list[index])
            index += 1
            eof_check(all_list)
            if all_list[index] != '(':
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected \"(\" after \"switch\" ")
                raise Exception
            index += 1
            eof_check(all_list)
            rvalue_depth += 1
            rvalue(all_list, pos_list)  # switch содержит любой rvalue
            if all_list[index-1] != ')':
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f"  Expected \")\" after \"switch\" ")
                raise Exception
            continue

        if all_list[index] == 'case':
            keyword_names.append(all_list[index])
            index += 1
            eof_check(all_list)
            rvalue_depth += 1
            global case_rvalue
            case_rvalue = True
            rvalue(all_list, pos_list)  # case может содержать rvalue с константами
            case_rvalue = False
            if all_list[index] != ':':
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected \":\" after \"case\" value ")
                raise Exception
            index += 1
            continue

        if all_list[index] == 'default':
            keyword_names.append(all_list[index])
            index += 1
            eof_check(all_list)
            if all_list[index] != ':':
                print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
                      f" Expected \":\" after \"case\" value ")
                raise Exception
            index += 1
            continue

        # обработчик остальных лексем (неожиданная лексема)
        print(f"Error on {pos_list[index][0]}:{pos_list[index][1]}:"
              f" Unexpected \"{all_list[index]}\"")
        raise Exception
    return variables, constants, operators, keyword_names, all_list, error
