# QUÉ HACEMOS CUANDO DEBEMOS ADAPATAR EL LENGUAJE A NUESTRO PROBLEMA??

La idea de este curso es aprender cómo podemos extender el lenguaje de Python
para que se adapte a nuestras necesidades. No vamos a llegar al nivel de Numpy
o de Pandas, donde vamos a crear modelos nuevos desde cero, pero si vamos a ver
cómo un proyecto como MyPy puede llegar a ser.

## Lo que me atrajo a Python...

Es su facilidad de uso. Fácilmente uno puede pasar de trabajar en Excel a hacer
buenos reportes en Python. Automatizar procesos. Enviar correos. Las
posibilidades son casi que ilimitadas en un lenguaje tan fácil de aprender.

Aunque la facilidad de uso y prototipado son excelentes, se paga con el peso de
la velocidad y con la amplitud de acción de las funciones que uno puede llegar
a hacer.

```Python

# Ejemplos:
1 + 1
'a' + 'a'
1.1 + 1.1
'a' + 1
1 + 1.1

```

Un operador puede llegar a tener tanto campo de acción que las mismas funciones
que nosotros hacemos, pueden tener comportamiento no planeado sólo por los
argumentos que se les pasan. Esto puede ser por un mal autor, buscando
comportamientos raros en nuestra aplicación o también, algo tan simple como un
mal parceado de datos.

```Python

def limited_sum(a, b):
    return a + b

```

Una manera de hacerle ver al que va a implementar la función de suma, el rango
de funcionalidad esperada de la función es agregándo type hints, y
documentación a la función. Ya saben todos los que están en grado senior para
arriba, que se debe de preguntar para dejar que el gente entre acá.

```Python

def limited_sum(a:int, b:int):
    """
    :type a => int
    :param a => number of the sum

    :type b => int
    :param b => number of the sum

    Sum between two integers
    """
    return a + b

```

*hacer este comentario mientras se escribe el código*
Si alguien reconoce en qué paquetes hacen la documentación de esta manera, que
hable ya mismo con el evaluador de salario que yo doy fe de que se merece ese
aumento.

El actual problema con esta implementación, es que de hecho no hace nada. Uno
sigue con la posibilidad de agregar elementnos del tipo que no se desea y
recibir excepciones raras propias del lenguaje o funcionalidad extraña.

Entonces estamos agregando nueva connotación al código que lo hace ver como si
fuera compilado o si hubiera una funcionalidad adicional que no existe.

También, es necesario tener en cuenta que a través de estos pseudo types que se
ponen en las funciones, el linter si puede seguir las definiciones y métodos en
caso de que pasemos objetos. Pero es pq le estamos dando contexto al linter
sobre que es lo que vamos a colocar y nos va a dar los errores respectivos en
caso de que no sea así. *mostrar ejemplo de un script. Puede ser el de raft*
Pero esa funcionalidad adicional no es lo que estamos buscando para resolver el
problema, entonces podemos volver con tranquilidad al caso.

Una manera en la que podemos asegurar que el tipo que va a llegar a la función
sea el que queremos puede ser

```Python

def limited_sum(a, b):
    assert isinstance(a,int), f'Expected int from {a}'
    assert isinstance(b,int), f'Expected int from {b}'
    return a + b

```

Ahora con la aserción si obtenemos el error que necesitamos, donde estamos
enforzándo el tipo de parámetro sobre el cual la funcióno debería de tener el
rango de acción. Adicionalmente, con el assert, estamos nuevamente haciendo
claro el tipo de argumento que estamos pasando.

=> Pregunta, será que el linter captará los métodos asociados a un objetos que
pasemos después del assert???

=> Hay que mirarlo de esta manera, sino es un valor del tipo que necesitamos,
se va a levantar el error. Asegurándo desde el código, sin los type hints, la
consistencia con el tipo.

Qué pasa cuando queremos expresar restricciones que no se pueden referenciar un
tipo específico??, así como los números mayores a 0, o sólo números negativos,
o cualquier parámetro interno de un objeto???

## IDEA

Hacer un framework que refuerce las condiciones que necesitemos. Idealmente
hacerlo desde los type hints => Hacerlos funcionales

Adicionalmente, usar la mayor cantidad de funcionalidades de las nuevas
versiones de Python para que la gente que intente implementar este código fuera
de la conferencia, se estrelle con la mayor cantidad de paredes posibles.
