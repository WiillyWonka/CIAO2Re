from queue import Queue

'''
Далее представлена функция построения регулярного выражения из графа-источника make_regex.

На вход получаем описание графа источника:
names - имена врешин
neighbours - список смежности для каждой вершины
d - индексы стоков
s - индекс начальной вершины

На выходе получаем массив заполненный результатами для различных стоков
и для получения итогового регулярного выражения достаточно объединить их знаком ’+’.

Алгоритм представляет из себя 2 обхода в ширину.
На первом проходе ищем циклы и наколение путей в терминальных вершинах.
На втором проходе формируем финальные регулярные выражения.
'''

def make_regex_parts(s, d, neighbours, names):
    Q = Queue()
    Q.put(s)
    d_ = [''] * len(neighbours)
    d_[s] = names[s]
    result = []
    while not Q.empty():
        current_v = Q.get()
        for u in neighbours[current_v]:
            if u in d:
                result.append(d_[current_v] + ' ' + names[u])
            elif d_[u] == '':
                d_[u] = d_[current_v] + ' ' + names[u]
                Q.put(u)
            else:
                d_[u] = '(' + d_[current_v] + ')*(' + names[u]
    
    Q.put(s)
    while not Q.empty():
        current_v = Q.get()
        for u in neighbours[current_v]:
            if u == s:
                continue
            if u in d:
                result.append(d_[current_v] + ' ' + names[u] + ')')
            else:
                d_[u] = d_[current_v] + ' ' + names[u]
                Q.put(u)
    return result

# Объединение результата знаком альтерации

def uniteResult(ls):
    it = iter(ls)
    out = next(it)
    for inst in it:
        out += ' + ' + inst

    return out

# Итоговая функция преобразующая граф в регулярное выражение
# Аргументы и выходные данные идентичны функции make_regex_parts

def make_regex(start_name, finall, neighbours, vertices_names):
    return uniteResult( \
        make_regex_parts(vertices_names.index(start_name), finall, neighbours, vertices_names))