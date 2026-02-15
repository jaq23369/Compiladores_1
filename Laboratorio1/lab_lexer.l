%{
#include <stdio.h>
%}

%option noyywrap
%x MULTI_COMENTARIO

%%

"//".*  { /* Comentario linea */ }

"/*" { BEGIN(MULTI_COMENTARIO); }
<MULTI_COMENTARIO>"*/" { BEGIN(INITIAL); }
<MULTI_COMENTARIO>(.|\n) { /* Ignorar */ }

\"(\\.|[^"\\])*\"       { printf("\033[0;32mToken(STRING, %s)\033[0m\n", yytext); }

0[xX][0-9a-fA-F]+       { printf("\033[0;35mToken(NUM_HEX, %s)\033[0m\n", yytext); }
[0-9]+(\.[0-9]+)?[eE][+-]?[0-9]+ { printf("\033[0;35mToken(NUM_CIENTIFICO, %s)\033[0m\n", yytext); }
[0-9]+\.[0-9]+          { printf("\033[0;36mToken(NUM_FLOAT, %s)\033[0m\n", yytext); }
[0-9]+                  { printf("\033[0;36mToken(NUM_ENTERO, %s)\033[0m\n", yytext); }

"=="|"!="|"<="|">="     { printf("\033[0;34mToken(OP_RELACIONAL, %s)\033[0m\n", yytext); }
"<"|">"                 { printf("\033[0;34mToken(OP_RELACIONAL, %s)\033[0m\n", yytext); }
"&&"|"||"|"!"           { printf("\033[0;34mToken(OP_LOGICO, %s)\033[0m\n", yytext); }
"+"|"-"|"*"|"/"         { printf("\033[0;34mToken(OP_ARITMETICO, %s)\033[0m\n", yytext); }
"="                     { printf("\033[0;34mToken(OP_ASIGNACION, %s)\033[0m\n", yytext); }

[a-zA-Z_][a-zA-Z0-9_]* { printf("\033[0;33mToken(ID, %s)\033[0m\n", yytext); }

[ \t\n]+                { /* Ignorar */ }
.                       { printf("\033[0;31mERROR: %s\033[0m\n", yytext); }

%%

int main(int argc, char **argv) {
if (argc > 1) yyin = fopen(argv[1], "r");
yylex();
return 0;
}
