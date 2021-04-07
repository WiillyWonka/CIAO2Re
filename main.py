import re
import argparse
from graph_creator import make_graph
from regex_creator import make_regex

def parseFile(data):
    data = data.casefold()
    data = re.sub(r"end(\n)+", r"end", data)
    row_sm_list = [i for i in data.casefold().split('end') if i != '']
    
    sm_list = []
    for row_sm in row_sm_list:
        sm = parseMachine(row_sm)
        if not sm is None: sm_list.append(sm)
    
    return sm_list

def parseMachine(data):
    commands = [i for i in data.split('\n') if i != '']
    it = iter(commands)
    
    state_machine = dict()
    fields = iter(['provided', 'inner', 'state'])
    
    next_field = next(fields)

    try:
        state_machine["name"] = next(it)
        if next(it) == 'provided':
            next_field = next(fields)
            state_machine['interfaces'] = []

            next_line = next(it)
            while next_line != 'inner':
                state_machine['interfaces'].append(next_line)
                next_line = next(it)
        else:
            print("Invalid sintax, \"provided\" missing")
            return None
            
        next_field = next(fields)
        state_machine['inner'] = []

        next_line = next(it)
        while next_line != 'state':
            state_machine['inner'].append(next_line)
            state_machine['interfaces'].append(next_line)
            next_line = next(it)

        state_machine['transition'] = []

        for next_line in it:
            buffer = next_line.split('->')
            state_machine['transition'].append({'states': [buffer[0], buffer[-1]],
                                'actions': [i for i in buffer[1].split("/")]})
        
        return state_machine
    
    except StopIteration:
        print("Invalid sintax, \"{}\" missing".format(next_field))
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str,
                    help="Path to CIAO2 file")

    parser.add_argument("start_name", type=str,
                    help="Name of start vertex")

    args = parser.parse_args()

    with open(args.path, 'r', encoding='utf-8') as f:
        sm_ls = parseFile(f.read())
        vertices_names, neighbours, finall = make_graph(sm_ls)
        print(make_regex(args.start_name, finall, neighbours, vertices_names))