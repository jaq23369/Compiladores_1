# Analizador Léxico (Scanner)

Esta primera fase de desarrollo implementa un Analizador Léxico manual  escrito en Python. Cuyo objetivo es procesar código fuente (basado en un subconjunto de Java), generar una secuencia de tokens y construir una tabla de símbolos, sin utilizar expresiones regulares ni generadores de autómatas.

## Descripción

El programa lee el código fuente carácter por carácter, identificando y clasificando los elementos léxicos (tokens). Es capaz de reconocer palabras clave, identificadores, números (enteros y decimales), cadenas de texto, operadores y comentarios. Esto está siendo desarrollado como parte del curso de **Compiladores 1**.

## Características

* **Implementación Manual:** No se utiliza la librería `re` (Regex) ni herramientas como Lex/Flex. Toda la lógica es algorítmica.
* **Tabla de Símbolos:** Almacena identificadores únicos encontrados durante el análisis.
* **Manejo de Literales:** Distingue entre enteros (`int`) y decimales (`double`), así como cadenas (`String`).
* **Ignora:** Espacios en blanco, saltos de línea y comentarios (tanto de línea `//` como de bloque `/* ... */`).
* **Reporte de Errores:** Indica la línea y columna donde se encuentran caracteres no reconocidos.

## Requisitos

* Python 3.x

## Ejecución

Para correr el analizador, simplemente ejecutr el archivo principal desde su terminal:

```bash
python Lex.py
```

## Ejemplo de Funcionamiento
Dado un código de entrada en Java como este:
```bash
public class PotionBrewer {
    private double gold = 100.50;
}
```

El programa generará una salida en consola similar a esto:
```bash
>>> INICIANDO ANÁLISIS...
Token(KEYWORD, public, Ln:1, Col:1)
Token(KEYWORD, class, Ln:1, Col:8)
Token(ID, PotionBrewer, Ln:1, Col:14)
Token(LBRACE, {, Ln:1, Col:27)
...
```

Y mostrará una tabla de símbolos como esta:
```bash
========= TABLA DE SIMBOLOS =========
NOMBRE               | TIPO      
===================================
PotionBrewer         | ID        
gold                 | ID        
===================================
```

## Video explicando funcionamiento y respondiendo dudas del ejercicio
https://youtu.be/BCVK9__Hh6E
---------------------------------------------------------------------------------------------

## Respuestas a los ejercicios

### Explicación detallada de como funciona el Scanner y proceso de Tokenización
El analizador léxico (Scanner) funciona como una máquina de estados manual que lee el código fuente carácter por carácter para agruparlos en unidades con significado llamadas Tokens. El proceso se divide en las siguientes fases lógicas:

#### Fase 1: El Puntero y la Lectura 
Aqui el scanner mantiene un cursor (pos) que recorre el texto de entrada. Además, rastrea la línea y columna actual para poder reportar la ubicación exacta de cada elemento. Utiliza funciones auxiliares como advance() para moverse hacia adelante y peek() para espiar el siguiente carácter sin consumirlo (fundamental para distinguir operadores como = de ==).

#### Fase 2: El Cerebro (Bucle Principal) 
Aqui la función get_next_token actúa como el director de orquesta. Contiene un bucle infinito que examina el carácter actual y decide a qué sub-rutina llamar:

- Si encuentra espacios en blanco o saltos de línea, los ignora y limpia.
- Si encuentra el inicio de un comentario (// o /*), activa la lógica para saltar texto hasta el final de la línea o del bloque.
- Si encuentra una letra, asume que es una palabra y delega el trabajo a la lógica de identificadores.
- Si encuentra un dígito, asume que es un número y delega el trabajo a la lógica numérica.
- Si encuentra comillas, procesa una cadena de texto (String).

#### Fase 3: Clasificación y Tabla de Símbolos 
Aquí el scanner detecta una palabra (una secuencia de letras), verifica si esa palabra existe en su lista interna de Palabras Reservadas (como public, int, if).
- Si está en la lista: Se crea un token de tipo KEYWORD. Si no está en la lista: Se clasifica como un ID (identificador variable) y, lo más importante, se guarda automáticamente en la Tabla de Símbolos para llevar un registro único de las variables del usuario.

#### Fase 4: Generación de Tokens 
Aqui finalmente, el scanner corta el pedazo de texto procesado y devuelve un objeto Token que contiene:
- Tipo: (Ej: INT_LITERAL, PLUS, ID).
- Valor: El texto real (Ej: 100, +, gold).
- Posición: Fila y columna donde fue encontrado.

---------------------------------------------------------------------------------------------

### Implementación de Recuperación de Errores
Actualmente, si el programa encuentra un símbolo extraño (como un @), se detiene o marca un error y sigue con el siguiente carácter. Para hacerlo más robusto y profesional, investigue y pues sería de implementar una estrategia conocida como Modo Pánico, que funciona así:

Primero imaginar que el analizador está leyendo y de repente se topa con basura o errores. En lugar de reportar 50 errores seguidos por una sola equivocación, el programa debería entrar en un estado de emergencia y hacer lo siguiente:
- Reportar el primer error que encontró.
- Ignorar todo lo que sigue rápidamente sin analizar nada.
- Frenar al encontrar un lugar seguro como el punto y coma (;) o el cierre de una llave (}), incluso un espacio seria un lugar seguro.

Esto evita que el analizador se confunda con el resto del código que sí está bien escrito.

---------------------------------------------------------------------------------------------

### Modificación para un idioma son Espacios como el Japonés
Si el código estuviera en japonés y sin espacios, la modificación principal sería eliminar la regla de encontrar un espacio en blanco, ya que esos espacios no existirían. En su lugar, se me ocurre que cambiar la lógica para que el escáner funcione consultando constantemente un diccionario, tipo tendría que leer símbolo por símbolo y preguntar en cada paso ¿lo que llevo leído ya forma una palabra conocida? y apenas detecte que los caracteres acumulados forman una instrucción válida o una variable, cortaría el token ahí mismo y empezaría a buscar el siguiente desde cero. En otro caso se me ocurre que podría apoyarme de el lenguaje japonés o de sus variaciones y definir una palabra que sea espacio para que así cuando el scanner la lea sepa que allí es un espacio y así proceder a cortar para evaluar que es.

---------------------------------------------------------------------------------------------






# Generador Léxico (Método Directo)

## Descripción del Problema:
El objetivo de este problema fue implementar desde cero el Método Directo para la construcción de compiladores. Se requirió desarrollar un programa capaz de transformar una Expresión Regular (específicamente para Identificadores: `Letra(Letra|Digito)*`) en un Autómata Finito Determinista (DFA) funcional y optimizado.

## Requerimientos Técnicos Implementados:

1.  ### Procesamiento de Expresiones (Regex):
    - Conversión de notación Infix a *Postfix* utilizando el algoritmo **Shunting Yard**.
    - Manejo de operadores básicos: Concatenación (`.`), Unión (`|`) y Cerradura de Kleene (`*`).

2.  ### Construcción del Árbol Sintáctico (AST):
    - Creación de un árbol de nodos (`Star`, `Cat`, `Or`, `Position`).
    - Cálculo automático de propiedades clave para cada nodo: `nullable`, `firstpos`, `lastpos` y `followpos`.

3.  ### Generación y Visualización:
    - Construcción de la tabla de transiciones del DFA basada en la tabla `followpos`.
    - Minimización de Estados: Algoritmo de partición para optimizar el autómata.
    - Generación de diagramas `.png` (Árbol y DFA) utilizando la librería Graphviz.

4.  ### Simulación (Scanner):
    - Validación del autómata mediante un escáner que lee un archivo de código fuente (Java) y clasifica los tokens encontrados como "Aceptados" (Identificadores) o "Rechazados" según las reglas del autómata generado.

## Demostracion y Explicación
- https://youtu.be/WWYBuPwUcQI

---------------------------------------------------------------------------------------------

## Autor
- Joel Antonio Jaquez López #23369
