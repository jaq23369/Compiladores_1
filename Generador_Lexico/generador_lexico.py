import sys
import re 
from graphviz import Digraph
import os

# ===========================================================================
# Lexemas elegidos del codigo de Java: Identificadores y Literales Numericos
# Expresion Regular para Identificadores: [a-zA-Z_][a-zA-Z0-9_]*
# Expresion Regular para Literales Numericos: [0-9]+
# Expresion Regular a Evaluar: Letra(Letra|Digito)*
# ===========================================================================

# ==================================================================
# CONFIGURACIÓN DE RUTAS E IMPORTACION MODULAR
# ==================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir) 

try:
    from Lex import Tokenizer
    print(f"Librería Lex.py importada correctamente.")
except ImportError:
    # Intento alternativo si está en carpeta hermana (como en tu estructura anterior)
    lex_path = os.path.join(current_dir, '..', 'Analizador_Lexico')
    sys.path.append(lex_path)
    try:
        from Lex import Tokenizer
        print(f"Librería Lex.py importada desde: {lex_path}")
    except ImportError:
        print("ERROR: No se encuentra Lex.py.")
        sys.exit()

# ==================================================================
# LÓGICA (Shunting Yard, Árboles, DFA)
# ==================================================================
class RegexConverter:
    @staticmethod
    def shunting_yard(infix):
        precedence = {'*': 3, '.': 2, '|': 1, '(': 0}
        output = []; stack = []; infix = infix.replace(' ', '')
        for char in infix:
            if char.isalnum() or char == '#' or char in ['L', 'D']: output.append(char)
            elif char == '(': stack.append(char)
            elif char == ')':
                while stack and stack[-1] != '(': output.append(stack.pop())
                stack.pop() 
            else: 
                while stack and precedence.get(stack[-1], 0) >= precedence.get(char, 0): output.append(stack.pop())
                stack.append(char)
        while stack: output.append(stack.pop())
        return "".join(output)
# ==================================================================

class Node:
    def __init__(self): self.nullable=False; self.firstpos=set(); self.lastpos=set(); self.id=None
class Position(Node):
    def __init__(self, s, i): super().__init__(); self.symbol=s; self.pos_id=i; self.firstpos={i}; self.lastpos={i}; self.id=f"pos_{i}"
class Or(Node): 
    def __init__(self, c1, c2): super().__init__(); self.c1=c1; self.c2=c2; self.nullable=c1.nullable or c2.nullable; self.firstpos=c1.firstpos|c2.firstpos; self.lastpos=c1.lastpos|c2.lastpos; self.id=f"or_{id(self)}"
class Cat(Node):
    def __init__(self, c1, c2): super().__init__(); self.c1=c1; self.c2=c2; self.nullable=c1.nullable and c2.nullable; self.firstpos=c1.firstpos|c2.firstpos if c1.nullable else c1.firstpos; self.lastpos=c1.lastpos|c2.lastpos if c2.nullable else c2.lastpos; self.id=f"cat_{id(self)}"
class Star(Node):
    def __init__(self, c1): super().__init__(); self.c1=c1; self.nullable=True; self.firstpos=c1.firstpos; self.lastpos=c1.lastpos; self.id=f"star_{id(self)}"

class VisualDFA:
    def __init__(self, regex_postfix, alphabet):
        self.regex_postfix = regex_postfix; self.alphabet = alphabet
        self.positions = {}; self.followpos = {}; self.root = None 
        self.pos_counter = 1; self.dfa_transitions = {}; self.dfa_states = {}; self.accept_pos_id = -1
    
    def build_tree(self):
        stack = []
        for char in self.regex_postfix:
            if char in self.alphabet or char == '#':
                pos_node = Position(char, self.pos_counter); self.positions[self.pos_counter] = char
                self.followpos[self.pos_counter] = set(); stack.append(pos_node); self.pos_counter += 1
            elif char == '*': c1 = stack.pop(); stack.append(Star(c1))
            elif char == '.': c2 = stack.pop(); c1 = stack.pop(); stack.append(Cat(c1, c2))
            elif char == '|': c2 = stack.pop(); c1 = stack.pop(); stack.append(Or(c1, c2))
        self.root = stack.pop(); self.accept_pos_id = self.pos_counter - 1 
    
    def compute_followpos(self, node=None):
        if node is None: node = self.root
        if isinstance(node, Cat):
            for i in node.c1.lastpos: self.followpos[i].update(node.c2.firstpos)
            self.compute_followpos(node.c1); self.compute_followpos(node.c2)
        elif isinstance(node, Star):
            for i in node.c1.lastpos: self.followpos[i].update(node.c1.firstpos)
            self.compute_followpos(node.c1)
        elif isinstance(node, Or): self.compute_followpos(node.c1); self.compute_followpos(node.c2)

    def generate_dfa(self):
        start_node = frozenset(self.root.firstpos)
        self.dfa_states = {start_node: "S0"}; queue = [start_node]; processed = set(); counter = 1
        while queue:
            current_state = queue.pop(0)
            if current_state in processed: continue
            processed.add(current_state)
            state_name = self.dfa_states[current_state]
            for symbol in [s for s in self.alphabet if s != '#']:

                target_pos = set()
                for pos in current_state:
                    if self.positions[pos] == symbol: target_pos.update(self.followpos[pos])
                target_frozen = frozenset(target_pos)
                if target_frozen:

                    if target_frozen not in self.dfa_states:
                        self.dfa_states[target_frozen] = f"S{counter}"; counter += 1; queue.append(target_frozen)
                    self.dfa_transitions[(state_name, symbol)] = self.dfa_states[target_frozen]

    def minimize_and_draw(self, filename="dfa_minimizado"):
        final = []; non_final = []
        for s_set, s_name in self.dfa_states.items():
            if self.accept_pos_id in s_set: final.append(s_name)
            else: non_final.append(s_name)
        
        print(f"\n   Proceso de Minimización (Partición de Estados):")
        print(f"   Pi_0 (Finales vs No Finales): {{ {non_final} , {final} }}")
        
        min_groups = [sorted(non_final), sorted(final)]
        min_groups = [g for g in min_groups if g]
        
        dot = Digraph(comment='DFA Minimizado'); dot.attr(rankdir='LR')
        state_to_group = {}; group_names = {}
        
        for i, group in enumerate(min_groups):
            g_name = f"Q{i}"; group_names[g_name] = group
            label = "{" + ",".join(group) + "}"
            is_final = "S0" not in group
            dot.node(g_name, label, shape='doublecircle' if is_final else 'circle')
            if "S0" in group: dot.node('start', '', shape='none'); dot.edge('start', g_name)
            for old in group: state_to_group[old] = g_name
                
        added = set()
        for g_name, group in group_names.items():
            rep = group[0]
            for char in self.alphabet:
                if char == '#': continue
                target = self.dfa_transitions.get((rep, char))
                if target:
                    target_g = state_to_group.get(target)
                    edge = (g_name, target_g, char)
                    if edge not in added:
                        dot.edge(g_name, target_g, label=char)
                        added.add(edge)
        try: dot.render(filename, view=False, format='png'); print(f"DFA Minimizado generado: {filename}.png")
        except: pass

    def render_tables(self):
        print("\n2. Tabla Followpos (Construcción Directa):")
        print("   " + "-" * 30)
        for pos in sorted(self.followpos.keys()):
            if pos in self.positions:
                print(f"   {pos:<5} | {self.positions[pos]:<5} | {sorted(list(self.followpos[pos]))}")
        print("\n3. Tabla Transiciones (DFA):")
        print("   " + "-" * 30)
        for key, val in self.dfa_transitions.items():
            print(f"   {key[0]} --({key[1]})--> {val}")

    def render_all(self):
        dot = Digraph(comment='Arbol'); dot.attr(rankdir='TB') 
        def add_node(n):
            label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD>Anulable: {"V" if n.nullable else "F"}</TD></TR><TR><TD>FP:{list(n.firstpos)} LP:{list(n.lastpos)}</TD></TR><TR><TD BGCOLOR="lightgrey"><B>{self._get_symbol(n)}</B></TD></TR></TABLE>>'''
            dot.node(n.id, label, shape='plaintext')
            if isinstance(n, (Cat, Or)): add_node(n.c1); add_node(n.c2); dot.edge(n.id, n.c1.id); dot.edge(n.id, n.c2.id)
            elif isinstance(n, Star): add_node(n.c1); dot.edge(n.id, n.c1.id)
        add_node(self.root)
        try: dot.render("arbol_java", view=False, format='png'); print("Árbol generado: arbol_java.png")
        except: pass

        dot2 = Digraph(comment='DFA'); dot2.attr(rankdir='LR') 
        for state_set, name in self.dfa_states.items():
            shape = 'doublecircle' if self.accept_pos_id in state_set else 'circle'
            dot2.node(name, f"{name}\n{list(state_set)}", shape=shape)
            if name == "S0": dot2.node('start', '', shape='none'); dot2.edge('start', 'S0')
        for (origin, symbol), dest in self.dfa_transitions.items(): dot2.edge(origin, dest, label=symbol)
        try: dot2.render("dfa_java", view=False, format='png'); print("DFA generado: dfa_java.png")
        except: pass

    def _get_symbol(self, n):
        if isinstance(n, Position): return f"'{n.symbol}' ({n.pos_id})"
        return "." if isinstance(n, Cat) else "|" if isinstance(n, Or) else "*" if isinstance(n, Star) else "?"

# ==================================================================
# FUNCIÓN DE DEMOSTRACIÓN 
# ==================================================================
def simulate_step_by_step(lexema, trans_table, final_states):
    print(f"\n4. Demostración Paso a Paso (Lexema: '{lexema}')")
    print("   " + "-" * 40)
    current = "S0"
    for char in lexema:
        # Mapeo al alfabeto abstracto
        mapped = '?'
        if char.isalpha() or char == '_': mapped = 'L'
        elif char.isdigit(): mapped = 'D'
        
        next_s = trans_table.get((current, mapped))
        if next_s:
            print(f"   Estado {current} --('{char}' como {mapped})--> {next_s}")
            current = next_s
        else:
            print(f"   Estado {current} --('{char}')--> ERROR (Rompe patrón)")
            return
            
    res = "ACEPTADO" if current in final_states else "RECHAZADO"
    print(f"   Estado Final: {current} -> Resultado: {res}")

# ==================================================================
# BLOQUE PRINCIPAL
# ==================================================================
if __name__ == "__main__":
    print("=== GENERADOR LÉXICO MODULAR ===")
    
    # REQUERIMIENTO 1: DEFINICIÓN DE TIPOS
    print("\n1. Definición de Patrones (Regex):")
    print("   A) Identificadores: Letra (Letra | Digito)*")
    print("   B) Números:         Digito (Digito)*")

    # REQUERIMIENTO 2: CONSTRUCCIÓN DIRECTA
    regex_infix = "L . ( L | D )* . #"
    regex_postfix = RegexConverter.shunting_yard(regex_infix)

    print(f"2. Regex Postfix: {regex_postfix}")
    
    alphabet = ['L', 'D']
    engine = VisualDFA(regex_postfix, alphabet)
    engine.build_tree()
    engine.compute_followpos()
    engine.generate_dfa()
    
    engine.render_all()     # Genera imagenes
    engine.render_tables()  # Imprime tablas followpos y transiciones

    # MINIMIZACIÓN
    engine.minimize_and_draw()

    # Identificar estados finales para la simulación
    final_states = []
    for s_set, s_name in engine.dfa_states.items():
        if engine.accept_pos_id in s_set: final_states.append(s_name)

    # DEMOSTRACIÓN PASO A PASO
    simulate_step_by_step("PotionBrewer", engine.dfa_transitions, final_states)

    # FASE B: ESCÁNER COMPLETO (LEX.PY)
    java_source_code = """
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
     double totalCost = (herbCount * HERB_PRICE) + (mushroomCount * MUSHROOM_PRICE
    );
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
    System.out.println(" Brewer Status ");
    System.out.println("Name: " + this.brewerName);
    System.out.println("Gold remaining: " + this.goldCoins);
    System.out.println("Potions brewed: " + this.potionsBrewed);
    }
    }
    """
    
    print("\n--- FASE B: EJECUCIÓN DEL ESCÁNER (Lex.py) ---")
    print("Analizando qué tokens cumplen con la Regex de Identificadores...\n")
    
    lexer = Tokenizer(java_source_code)
    
    print(f"{'TOKEN GENERADO':<35} | {'ANÁLISIS CONTRA REGEX <ID>'}")
    print("-" * 80)
    
    while True:
        token = lexer.get_next_token()
        if token.tipo == "EOF": break
        
        # LÓGICA DE VALIDACIÓN VISUAL
        if token.tipo == "ID":
            # Buscamos el nombre real en la tabla
            nombre_real = "???"
            for k, v in lexer.symbol_table.symbols.items():
                if v == token.valor: nombre_real = k; break
            
            # ESTE SÍ CUMPLE
            token_str = f"< ID, {nombre_real} >"
            print(f"{token_str:<35} | MATCH (Cumple L(L|D)*)")
            
        elif token.tipo == "KEYWORD":
            # CUMPLE LA REGEX PERO ES RESERVADA
            token_str = f"< KEYWORD, {token.valor} >"
            print(f"{token_str:<35} | MATCH (Pero es Reservada)")
            
        else:
            # NO CUMPLE 
            token_str = f"< {token.tipo}, {token.valor} >"
            print(f"{token_str:<35} | NO MATCH (Es otro tipo)")

    