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

## Autor
- Joel Antonio Jaquez López #23369
