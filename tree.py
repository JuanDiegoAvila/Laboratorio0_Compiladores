def stringTreeToList(tree_string):
    new_word = ''
    words = []
    string_flag = False

    for i in tree_string:
        if string_flag==False:
            if i =='(':
                words.append(i)
                new_word = ''
            elif i == ' ':
                if new_word != '' and new_word!=' ':
                    words.append(new_word)
                new_word=''
            elif i == ')':
                if new_word != '' and new_word!=' ':
                    words.append(new_word)
                new_word=''
                words.append(i)
            elif i == '"':
                string_flag=True
                new_word=i
            else:
                new_word+=i
        else:
            if i == '"':
                string_flag=False
                new_word+=i
                words.append(new_word)
                new_word=''
            else: 
                new_word+=i
    return words


class Node:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or []
        self.number = 0
    
    def addChild(self, child_node):
        self.children.append(child_node)
        
    def Traverse(self):
        stack = [self]
        while stack:
            lookat = stack.pop()
            print(lookat.name)
            if lookat.children:
                for i in lookat.children:
                    stack.append(i)
                    
    def Traverse2(self):
        print(" ")
        stack = [self]
        while stack:
            lookat = stack.pop()

            if lookat.children:
                names = [i.name for i in lookat.children]
                print(lookat.name, names)

                for i in lookat.children:
                    if i.children:
                        
                        stack.append(i)
    
    def showGraph(self):
        stack = [self]
        count = 0
        dot = Graph()
        
        dot.node(name=str(self.number)+' '+self.name, label=self.name)
        while stack:
            lookat = stack.pop()
            if lookat.children:
                for i in lookat.children:
                    count+=1
                    i.number = count
                    nombre_i = str(i.number)+' '+i.name
                    dot.node(name=nombre_i, label=i.name)
                    dot.edge((str(lookat.number)+' '+lookat.name), nombre_i)
                    stack.append(i)
        dot.render('tree', format='png')