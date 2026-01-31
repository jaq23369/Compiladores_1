# Fase 1: Estrcturas de Datos (Definición de clases y Constantes)
class Token:
    def __init__(self, tipo, valor, linea, columna):
        self.tipo = tipo  # Para "KEYWORD", "NUMBER", "ID"
        self.valor = valor # Para "public", "5.50", "potionsBrewed"
        self.linea = linea # Para saber donde esta el error o token
        self.columna = columna # Para saber la posicion de la linea
    
    def __repr__(self):
        # Esto me sierve para imprimir el token de forma clara en la consola
        return f"Token({self.tipo}, {self.valor}, Ln:{self.linea}, Col:{self.columna})"
    
class SymbolTable:
    def __init__(self):
        self.symbols = {} # Este diccionario es para guardar los identificadores

    def add(self, name, info_type="ID"):
    # Esto me sirve para agregar separar lo que existe de lo que no y asi no duplicar nada en la tabla
        if name not in self.symbols:
            self.symbols[name] = info_type
    
    def display(self):
        print("=========TABLA DE SIMBOLOS=========")
        print(f"{'NOMBRE':<20} | {'TIPO':<10}")
        print("=================================")
        for name, info in self.symbols.items():
            print(f"{name:<20} | {info:<10}")
        print("=================================")

# Lista de palabras reservadas de Java que hay en el codigo
KEYWORDS = {
    "public", "class", "private", "static", "final", "int", "double", 
    "String", "void", "new", "if", "else", "this", "return" 
}

# Fase 2: Motor de lectura (Para recorrer el codigo fuente)
class Tokenizer:
    def __init__(self, source_code):
        self.source = source_code # El codigo que se va a analizar
        self.pos = 0  # Posicion actual en el codigo
        self.line = 1 # La linea actual
        self.col = 1  # La columna actual
        self.tokens = [] # Lista donde guardo los tokens encontrados
        self.errors = [] # Lista donde guardo los errores encontrados (si hay)
        self.symbol_table = SymbolTable() # Tabla de simbolos
    
    def current_char(self):
    # Esta funcion me sirve para obtener el caracter actual o None si ya llego al final
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None
    
    def peek(self, offset=1):
    # Esta funcion me sirve para ver hacia adelante sin mover el puntero
    # con ello se logra distinguir =, ==, / y //
        next_pos = self.pos + offset
        if next_pos < len(self.source):
            return self.source[next_pos]
        return None
    
    def advance(self):
    # Esta funcion me sirve para avanzar de posicion, si hay salto de linea ajusta el contador
        char = self.current_char()
        if char == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.pos += 1
        return char
    
    def skip_whitespace(self):
    # Esta funcion me sirve para ignorar espacios en blanco, tabulaciones y saltos de linea
        while self.current_char() is not None and self.current_char().isspace():
            self.advance()

            

# Fase 3: Logica de clasificacion (Para detectar numeros, palabras, strings y simbolos)

# 3.1 Detectar palabras (Identificadores y Keywords)
    def _read_identifier(self):
        start_pos = self.pos # Para recordar donde comenzo la palabra
        start_col = self.col # Para recordar la columna inicial

        # Siempre que sea letras, seguir leyendo
        while self.current_char() is not None and (self.current_char().isalnum() or self.current_char() == '_'):
            self.advance()
        
        # Esto para cortar el texto que se acaba de leer
        text = self.source[start_pos : self.pos]

        # Aqui decidir si es palabra reservada o variable
        if text in KEYWORDS:
            return Token("KEYWORD", text, self.line, start_col)
        else:
            # En caso de ser variable, guardar en la tabla de simbolos
            self.symbol_table.add(text, "ID")
            return Token("ID", text, self.line, start_col)

# 3.2 Detectar numeros para diferenciar entre enteros y decimales
    def _read_number(self):
        start_pos = self.pos
        start_col = self.col
        is_double = False # Esto para asumir que es un entero al inicio

        # Leer digitos antes del punto
        while self.current_char() is not None and self.current_char().isdigit():
            self.advance()
        
        # Verificar si es un numero decimal
        if self.current_char() == '.':
            is_double = True
            self.advance() # Saltar el punto

            # Leer digitos despues del punto
            while self.current_char() is not None and self.current_char().isdigit():
                self.advance()
        
        # Cortar el texto leido
        text = self.source[start_pos : self.pos]

        # Verificar si es entero o decimal
        if is_double:
            return Token("DOUBLE_LITERAL", text, self.line, start_col)
        else:
            return Token("INT_LITERAL", text, self.line, start_col)

# 3.3 Detectar Strings en java entre comillas dobles
    def _read_string(self):
        start_col = self.col
        start_pos = self.pos
        self.advance() # Esto para saltar la comilla inicial

        start_pos = self.pos # Esto porque el texto comienza despues de la comilla

        while self.current_char() is not None and self.current_char() != '"':
            self.advance()
        
        text = self.source[start_pos : self.pos]
        self.advance() # Esto para saltar la comilla final

        return Token("STRING_LITERAL", text, self.line, start_col)

    # 3.4 Saltar comentarios
    def _skip_comment(self):
        # CORREGIDO: Ahora está bien indentado dentro de la clase
        if self.peek() == '/': 
            self.advance(); self.advance()
            while self.current_char() is not None and self.current_char() != '\n':
                self.advance()
        elif self.peek() == '*':
            self.advance(); self.advance()
            while self.current_char() is not None:
                if self.current_char() == '*' and self.peek() == '/':
                    self.advance(); self.advance()
                    break 
                self.advance()

    # Fase 4: Cerebro del Lex
    def get_next_token(self):
        while self.current_char() is not None:
            
            if self.current_char().isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char() == '/' and (self.peek() == '/' or self.peek() == '*'):
                self._skip_comment()
                continue

            if self.current_char().isalpha():
                return self._read_identifier()
            
            if self.current_char().isdigit():
                return self._read_number()
            
            if self.current_char() == '"':
                return self._read_string()

            # --- SÍMBOLOS ---
            char = self.current_char()
            
            # Símbolos dobles
            if char == '=' and self.peek() == '=':
                self.advance(); self.advance()
                return Token("EQUALS", "==", self.line, self.col - 2)
            if char == '+' and self.peek() == '+':
                self.advance(); self.advance()
                return Token("INCREMENT", "++", self.line, self.col - 2)
            if char == '<' and self.peek() == '=':
                self.advance(); self.advance()
                return Token("LESS_EQ", "<=", self.line, self.col - 2)
            if char == '-' and self.peek() == '=':
                self.advance(); self.advance()
                return Token("MINUS_ASSIGN", "-=", self.line, self.col - 2)

            # Símbolos simples
            sym_map = {
                '+': "PLUS", '-': "MINUS", '*': "MULTIPLY", '=': "ASSIGN",
                ';': "SEMICOLON", '{': "LBRACE", '}': "RBRACE", '(': "LPAREN",
                ')': "RPAREN", ',': "COMMA", '[': "LBRACKET", ']': "RBRACKET", '.': "DOT"
            }
            
            if char in sym_map:
                self.advance()
                return Token(sym_map[char], char, self.line, self.col - 1)

            # Error
            self.errors.append(f"Error: Carácter inesperado '{char}'")
            self.advance()
            
        return Token("EOF", None, self.line, self.col)
    
# Ejecucion

codigo_fuente = """ 
public class PotionBrewer {
    // Ingredient costs in gold coins
    private static final double HERB_PRICE = 5.50;
    private static final int MUSHROOM_PRICE = 3;
    private String brewerName;
    private double goldCoins;
    private int potionsBrewed;

    public PotionBrewer(String name, double startingGold) {
        this.brewerName = name;
        this.goldCoins = startingGold;
        this.potionsBrewed = 0;
    }

    public static void main(String[] args) {
        PotionBrewer wizard = new PotionBrewer("Gandalf, the Wise", 100.0);
        String[] ingredients = {"Mandrake Root", "Dragon Scale", "Phoenix Feather"};

        wizard.brewHealthPotion(3, 2); // 3 herbs, 2 mushrooms
        wizard.brewHealthPotion(5, 4);

        wizard.printStatus();
    }

    /* Brews a potion if we have enough gold */
    public void brewHealthPotion(int herbCount, int mushroomCount) {
        double totalCost = (herbCount * HERB_PRICE) + (mushroomCount * MUSHROOM_PRICE);
        
        if (totalCost <= this.goldCoins) {
            this.goldCoins -= totalCost; // Deduct the cost
            this.potionsBrewed++;
            System.out.println("Success! Potion brewed for " + totalCost + " gold.");
        } else {
            System.out.println("Not enough gold! Need: " + totalCost);
        }
    }

    // Prints the current brewer status
    public void printStatus() {
        System.out.println("\\n=== Brewer Status ===");
        System.out.println("Name: " + this.brewerName);
        System.out.println("Gold remaining: " + this.goldCoins);
        System.out.println("Potions brewed: " + this.potionsBrewed);
    }
}
"""

if __name__ == "__main__":
    lexer = Tokenizer(codigo_fuente)
    print(">>> INICIANDO ANÁLISIS...")
    
    while True:
        token = lexer.get_next_token()
        if token.tipo == "EOF":
            break
        print(token)
    
    lexer.symbol_table.display()
