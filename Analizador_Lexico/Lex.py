class Token:
    def __init__(self, tipo, valor, linea, columna):
        self.tipo = tipo; self.valor = valor; self.linea = linea; self.columna = columna
    def __repr__(self): return f"< {self.tipo}, {self.valor} >"

class SymbolTable:
    def __init__(self):
        self.symbols = {}; self.counter = 1
    def add(self, name):
        if name not in self.symbols:
            self.symbols[name] = self.counter; self.counter += 1
        return self.symbols[name]
    
    def display(self):
        print("\n   TABLA DE SÍMBOLOS GENERADA:")
        print(f"   {'ID':<5} | {'LEXEMA'}")
        print("   " + "-"*30)
        inv_map = {v: k for k, v in self.symbols.items()}
        for i in range(1, self.counter): print(f"   {i:<5} | {inv_map[i]}")

KEYWORDS = {
    "public", "class", "private", "static", "final", "int", "double", 
    "String", "void", "new", "if", "else", "this", "return", "System", "out", "println"
}

class Tokenizer:
    def __init__(self, source_code):
        self.source = source_code 
        self.lexemeBegin = 0; self.forward = 0     
        self.line = 1; self.col = 1
        self.symbol_table = SymbolTable() 
    
    def get_char(self):
        return self.source[self.forward] if self.forward < len(self.source) else None
    
    def next_char(self):
        char = self.get_char()
        if char == '\n': self.line += 1; self.col = 1
        else: self.col += 1
        if char is not None: self.forward += 1
        return char
    
    def get_next_token(self):
        while self.forward < len(self.source):
            char = self.get_char()
            if char is None: break
            if char.isspace():
                self.next_char(); self.lexemeBegin = self.forward
            else: break
        
        if self.forward >= len(self.source): return Token("EOF", "EOF", self.line, self.col)

        start_col = self.col; char = self.next_char() 

        # --- CASO 1: IDENTIFICADORES Y KEYWORDS ---
        if char.isalpha() or char == '_':
            while True:
                c = self.get_char()
                if c is not None and (c.isalnum() or c == '_'): self.next_char()
                else: break 
            
            lexema = self.source[self.lexemeBegin : self.forward]
            self.lexemeBegin = self.forward 
            if lexema in KEYWORDS: return Token("KEYWORD", lexema, self.line, start_col)
            else: return Token("ID", self.symbol_table.add(lexema), self.line, start_col)

        # --- CASO 2: NÚMEROS ---
        if char.isdigit():
            is_double = False
            while True:
                c = self.get_char()
                if c is None: break
                if c.isdigit(): self.next_char()
                elif c == '.':
                    if is_double: break 
                    is_double = True; self.next_char()
                else: break
            lexema = self.source[self.lexemeBegin : self.forward]
            self.lexemeBegin = self.forward
            return Token("DOUBLE_LITERAL" if is_double else "INT_LITERAL", lexema, self.line, start_col)

        # --- CASO 3: STRINGS ---
        if char == '"':
            while True:
                c = self.next_char(); 
                if c == '"' or c is None: break
            lexema = self.source[self.lexemeBegin : self.forward]; self.lexemeBegin = self.forward
            return Token("STRING_LITERAL", lexema, self.line, start_col)
            
        # --- CASO 4: COMENTARIOS Y SLASH ---
        if char == '/':
            peek = self.get_char()
            if peek == '/': # Linea
                while True:
                    c = self.next_char()
                    if c == '\n' or c is None: break
                self.lexemeBegin = self.forward; return self.get_next_token()
            elif peek == '*': # Bloque
                self.next_char()
                while True:
                    c = self.next_char()
                    if c == '*' and self.get_char() == '/': self.next_char(); break
                    if c is None: break
                self.lexemeBegin = self.forward; return self.get_next_token()

        # --- CASO 5: SÍMBOLOS ---
        sym_map = {'+': "PLUS", '-': "MINUS", '*': "MULTIPLY", '=': "ASSIGN", ';': "SEMICOLON", 
                   '{': "LBRACE", '}': "RBRACE", '(': "LPAREN", ')': "RPAREN", ',': "COMMA", '.': "DOT"}
        tipo = "SYMBOL"; val = char
        if char in sym_map: tipo = sym_map[char]
        self.lexemeBegin = self.forward
        return Token(tipo, val, self.line, start_col)