## NUEVO PYTHON NUEVO YO

La idea de la presentación es saber lo que se viene, pero como podemos estar
preparados o entender el futuro sino sabemos el pasado.

# Cómo funciona Python a la hora de hacer verdadero trabajo en paralelo??

Python tiene una manera de recuperar memoria dinármica, que se llama, contador
de referencia. Lo que hace es que literalmente cuenta cuantos objetos tienen
referencia uno del otro y cuando esta referencia llega a cero, es seguro
eliminar el objeto.

Por como esto funciona, es necesario tener un bloqueo global sobre el
intérprete, ya que sólo así va a ser posible contar las referencias que varios
procesos pueden tener, teniendo como consecuencia que sólo un proceso se pueda
ejecutar a la misma vez. Por esto mismo estamos bloqueados a una sola CPU,
entre nucleos no podemos compartir estados.

Esto hace que aunque los `hilos` son perfectos para trabajo I/O (input/output)
estos son malos para computación, ya que como se dijo anteriormente, esto
requiere consumo de CPU de manera intensiva y como sólo tenemos una CPU
disponible, bloqueamos todo el trabajo. Adicionalmente, los `hilos` se pelean
entre ellos el intérprete haciendo que varios trabajos que requieran poder
computacional un desastre.

Tampoco se soluciona con asíncronicidad o bucles de eventos. Un trabajo que
requiera computación pesada todavía puede bloquear completamente el bucle y
terminamos donde iniciamos.

# SOLUCIONES DEL PASADO

Delegar el trabajo a procesos
