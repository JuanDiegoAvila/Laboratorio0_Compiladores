class Stack:
    def __init__(self):
        self.memory = {}
        self.registros = {}            
    
    def push(self, name, value={}):
        self.memory[name] = value
                
        
    def pop(self):
        keys = self.memory.keys()
        pop_value = keys[-1]
        value = self.memory[pop_value]
        self.memory.pop(pop_value)
        return value
        
    def peek(self):
        keys = self.memory.keys()
        peek_value = keys[-1]
        value = self.memory[peek_value]
        return value
        
        