grammar yalp;

/* GRAMATICA */

program: class SEMICOLON POSITIVE;

// class: DIGIT TIMES DIGIT;

class: CLASS TYPE LSQUARE INHERITS TYPE RSQUARE LBRACE LSQUARE feature RSQUARE KLEENE RBRACE;

feature: ID LPAR LSQUARE formal LSQUARE COMMA formal RSQUARE KLEENE RSQUARE RPAR COLON TYPE LBRACE expr RBRACE
    | ID COLON TYPE LSQUARE ASSIGN expr RSQUARE;

formal:
    ID COLON TYPE;

expr: ID COLON expr
    | expr LSQUARE AT TYPE RSQUARE DOT ID LPAR LSQUARE expr LSQUARE COMMA expr RSQUARE KLEENE RSQUARE RPAR
    | IF expr THEN expr ELSE expr FI
    | WHILE expr LOOP expr POOL
    | LBRACE LSQUARE expr SEMICOLON RSQUARE POSITIVE RBRACE
    | LET ID COLON TYPE LSQUARE ASSIGN expr RSQUARE LSQUARE COMMA ID COLON TYPE LSQUARE ASSIGN expr RSQUARE RSQUARE KLEENE IN expr
    | NEW TYPE
    | ISVOID expr
    | expr PLUS expr
    | expr MINUS expr
    | expr TIMES expr
    | expr DIVIDE expr
    | DIAC expr
    | expr LT expr
    | expr LE expr
    | expr EQUALS expr
    | NOT expr
    | LPAR expr RPAR
    | ID
    | DIGIT
    | STRING
    | TRUE
    | FALSE;

/* REGLAS */

// ENTEROS
DIGIT: [0-9];

UPPERCASE: [A-Z];
LOWERCASE: [a-z];
LETTER: [a-zA-Z];

// Caracteres especiales
DOT: '.';
AT: '@';
DIAC: '~';
TIMES: '*';
DIVIDE: '/';
PLUS: '+';
MINUS: '-';
LT: '<';
LE: '<=';
EQUALS: '=';
ASSIGN: '<-';

KLEENE: '"*"';
POSITIVE: '"+"';

LPAR: '(';
RPAR: ')';
COLON: ':';
SEMICOLON: ';';
LBRACE: '{';
RBRACE: '}';
COMMA: ',';
LSQUARE: '[';
RSQUARE: ']';

// Identificadores especiales
SELF: 'self';
SELF_TYPE: 'SELF_TYPE';

// Palabras reservadas
FALSE: 'false';
TRUE: 'true';
CLASS: [cC][lL][aA][sS][sS];
ELSE: [eE][lL][sS][eE];
FI: [fF][iI];
IF: [iI][fF];
IN: [iI][nN];
INHERITS: [iI][nN][hH][eE][rR][iI][tT][sS];
ISVOID: [iI][sS][vV][oO][iI][dD];
LOOP: [lL][oO][oO][pP];
POOL: [pP][oO][oO][lL];
THEN: [tT][hH][eE][nN];
WHILE: [wW][hH][iI][lL][eE];
NEW: [nN][eE][wW];
NOT: [nN][oO][tT];
LET: [lL][eE][tT];
TYPE: UPPERCASE (ID)*;
OBJECT: LOWERCASE ID;

ID: LETTER (LETTER | DIGIT)*;
// cadenas
// STRING : '"' ( ESC_SEQ | ~["\b\t\n\f\r\\] )* '"';
// fragment ESC_SEQ : '\\' [btnf];
STRING: '"' .*? '"';

// comentarios
COMMENT: '--' ~[\r\n]* -> skip;
CLOSED_COMMENT: '(*' .*? '*)' -> skip;

WHITESPACE: [ \t\r\n\f]+ -> skip;

ERROR: . ;