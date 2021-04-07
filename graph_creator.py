'''
Здесь представлен набор функций необходимых для построения графа-источника
из описания конечных автоматов

Основной функцией является make_graph

Построение имеет следующие этапы:

1) Выделим все предоставляемые интерфейсы (и внешние, и внутренние) - это будут
вершины графа источника.

2) Проверим для каждой из команд: существует ли 2 различных состояния (или одно
состояние, но 2 различных события на переходах), из которых вызывается эта команда.
Если это условие выполнено, то команду нужно ’размножить’ по числу таких состояний.
Для таких команд вводим новые команды вида ’<st>_<interface>’
- комбинацию из названия состояния и команды. В описаниях переходов заменяем
вызовы команд на введённые.

3) Выделяем конечные состояния: все, из которых есть переход в ’exit’.

4) Переходим к добавлению дуг. Сначала добавляем дуги из <interface1> в <interface2>
в случае, если существует переход вида: <st1> -> <interface1> / <interface2> ->
<st2>. Таким образом мы учтем внешнее взаимодействие между объектами.

5) Теперь учтём внутренние переходы. Пройдёмся по всем внутренним интерфейсам и
если для интерфейса <interfaceI> существует переход вида: <st1> -> <interface>
/ <interfaceI> -> <st2>, то необходимо добавить дуги между <interfaceI> и всеми
событиями, ведущими из <st2>.

Все автоматы представлены Python словарём с полями

"name" - имя автомата
"provided" - предоставляеме интерфейсы
"inner" - внутренние интерфейсы
"transition" все переходы вида <st1> -> <interface1> / <interface2> -> <st2> и является также словарём

"transition" содержит:
"states" = [st1, st2]
"actions" = [interface1, interface2]
'''

#splitVertices реализует разделение вершин. Пункт 2 алгоритма
#updateTransition обновляет команды и события согласно новым вершинам

def updateTransition(sm_ls, state1, state2, command):
    for state_machine in sm_ls:
        for transition in state_machine['transition']:
            if transition['actions'][1] == command:
                if transition['states'][0] == state1:
                    transition['actions'][1] = command + "_" + state1
                if transition['states'][0] == state2:
                    transition['actions'][1] = command + "_" + state2

def splitVertices(sm_ls):
    for state_machine1 in sm_ls:
        for transition1 in state_machine1['transition']:
            for state_machine2 in sm_ls:
                for transition2 in state_machine2['transition']:
                    command = transition1['actions'][1]
                    if command == transition2['actions'][1] \
                    and transition1['states'][0] != transition2['states'][0] \
                    and command != '':
                        if command in state_machine1['interfaces']: state_machine1['interfaces'].remove(command)
                        if command in state_machine2['interfaces']: state_machine2['interfaces'].remove(command)
                        
                        state1 = transition1['states'][0]
                        state2 = transition2['states'][0]
                        
                        new_command1 = command + "_" + state1
                        new_command2 = command + "_" + state2
                        
                        updateTransition(sm_ls, state1, state2, command)
                        
                        transition1['actions'][1] = new_command1
                        transition2['actions'][1] = new_command2
                        
                        state_machine1['interfaces'].append(new_command1)
                        state_machine2['interfaces'].append(new_command2)
                        
                        if command in state_machine1['inner']:
                            state_machine1['inner'].remove(command)
                            state_machine1['inner'].append(new_command1)
                        if command in state_machine2['inner']:
                            state_machine2['inner'].remove(command)
                            state_machine2['inner'].append(new_command2)

#findFinallState и findFinallActions реализуют поиск финальных вершин

def findFinallState(state_machine):
    for state in state_machine['transition']:
        if state['states'][1] == 'exit': return state['states'][0]

def findFinallActions(finall_state, state_machine, vertices_names):
    out = []
    for state in state_machine['transition']:
        if state['states'][1] == finall_state:
            if state['actions'][1] == '':
                out.append(vertices_names.index(state['actions'][0]))
            else:
                out.append(vertices_names.index(state['actions'][1]))
            del state

    return out

#getGraph строит окончательное представление графа источника
#Реализует пункты 3,4,5
#in: sm_ls - список конечных автоматов

def getGraph(sm_ls):
    vertices_names = []
    finall = []
    for state_machine in sm_ls:
        vertices_names.extend(state_machine['interfaces'])
        finall_state = findFinallState(state_machine)
        finall.extend(findFinallActions(finall_state, state_machine, vertices_names))

    neighbours = [[] for i in range(len(vertices_names))]

    for state_machine in sm_ls:
        for state in state_machine['transition']:
            if state['actions'][1] != '' and state['actions'][0] != '':
                v_idx = vertices_names.index(state['actions'][0])
                value = vertices_names.index(state['actions'][1])
                if not value in neighbours[v_idx]: neighbours[v_idx].append(value)

    for state_machine in sm_ls:
        for state in state_machine['transition']:
            action = state['actions'][1]
            state_buffer = state['states'][1]
            if action in state_machine['inner']:
                for state_in in state_machine['transition']:
                    if state_buffer == state_in['states'][0] \
                     and state_in['actions'][0] != '':
                        v_idx = vertices_names.index(action)
                        value = vertices_names.index(state_in['actions'][0])
                        if not value in neighbours[v_idx]: neighbours[v_idx].append(value)
                            
    for state_machine in sm_ls:
        for state in state_machine['transition']:
            if state['actions'][1] == '':
                action = state['actions'][0]
                state_buffer = state['states'][1]
                if action in state_machine['inner']:
                    for state_in in state_machine['transition']:
                        if state_buffer == state_in['states'][0] \
                         and state_in['actions'][0] != '':
                            v_idx = vertices_names.index(action)
                            value = vertices_names.index(state_in['actions'][0])
                            if not value in neighbours[v_idx]: neighbours[v_idx].append(value)

    return vertices_names, neighbours, finall

#Итоговая функция строящая граф-источник
#in: sm_ls - список конечных автоматов
#out:
#vertices_names - список имён вершин
#neighbours - список смежности для каждой вершины
#finall - список индексов заключительных вершин
def make_graph(sm_ls):
    splitVertices(sm_ls)
    vertices_names, neighbours, finall = getGraph(sm_ls)
    return vertices_names, neighbours, finall