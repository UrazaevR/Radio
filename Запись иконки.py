import os


while True:
    c = input('Введите путь к картинке\n-d для удаления переменной\n-e для выхода:\n')
    if c == '-e': break
    elif c == '-d':
        perem = input('Введите имя переменной для удаления: ')
        with open('Globals.py', 'r') as old_f:
            with open('TempGlobals.py', 'w') as new_f:
                start_del = False
                while s := old_f.readline():
                    if len(s.strip()) == 0:
                        new_f.write(s)
                    else:
                        if s.strip()[0] != '#':
                            if '=' in s:
                                if s.split('=')[0].strip() == perem:
                                    print(f'Переменная {perem} найдена!')
                                    start_del = True
                                else:
                                    start_del = False
                        if not start_del:
                            new_f.write(s)
        Y_N = input('Подтвердите удаление [Y/N?]: ')
        if Y_N == 'Y':
            os.remove('Globals.py')
            os.rename('TempGlobals.py', 'Globals.py')
    else:
        try:
            with open(c, 'rb') as file:
                b = bytearray(file.read())
                with open('Globals.py', 'a') as f:
                    x = bytearray.__str__(b)
                    f.write(f"\n{input('Название переменной: ')} = {x}")
        except Exception as ex:
            print(ex)
    print()