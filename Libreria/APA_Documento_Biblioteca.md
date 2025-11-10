
# Sistema de Gestión de Biblioteca con Estructuras de Datos Lineales

**Autor:** Juan Camilo Esguerra  
**Curso:** Estructuras de Datos — Unidad 1  
**Fecha:** 2025-10-05

## Introducción

Este documento presenta el prototipo funcional de un sistema de gestión de biblioteca implementado con estructuras de datos lineales. Se emplean listas, pilas, colas y arreglos para modelar catálogo, usuarios, historial de operaciones, listas de espera y deshacer (undo). El objetivo es evidenciar la selección adecuada de estructuras según la operación (búsqueda, préstamo, devolución, espera y reversión) y justificar decisiones de diseño con criterios de eficiencia y claridad.

## Selección del enfoque

- **Listas**: Catálogo de libros, usuarios e historial por su acceso secuencial simple y operaciones de recorrido.
- **Cola (FIFO)**: Lista de espera por libro; el primer usuario en esperar es el primero en recibir una copia disponible.
- **Pila (LIFO)**: Registro de operaciones para permitir *undo* del último préstamo/devolución.
- **Arreglo (lista indexada)**: Asignación de IDs secuenciales a libros y usuarios.

## Diseño de las estructuras

- `Book`: id, title, author, year, copies, `waitlist: deque`.
- `User`: id, name, `borrowed: List[int]`.
- `Operation`: kind (borrow/return), user_id, book_id, timestamp.
- `Library`: `books: List[Book]`, `users: List[User]`, `history: List[Operation]`, `undo_stack: List[Operation]`.

## Implementación (resumen)

Ver archivo `library_system.py`. La interfaz de consola permite:

- Registrar usuarios, listar y buscar libros.
- Prestar, devolver y deshacer la última operación.
- Gestionar automáticamente la cola de espera en devoluciones.

## Interfaz de usuario

Se provee un menú textual simple y autodescriptivo; cada acción confirma el resultado por pantalla. La navegación secuencial facilita pruebas controladas.

## Pruebas y depuración

- **Préstamo con copias disponibles**: reduce `copies` y añade el id del libro a `user.borrowed`.
- **Préstamo sin copias**: añade el usuario a `book.waitlist` (cola).
- **Devolución**: incrementa `copies` y, si hay espera, presta automáticamente al primer usuario de la cola.
- **Undo**: revierte el último préstamo o devolución (pila LIFO).
- Se validan casos de error: ids inexistentes, devoluciones no válidas.

## Buenas prácticas

Tipado estático con *type hints*, `@dataclass`, separación de responsabilidades y docstrings. Nombres con significado y funciones cortas.

## Conclusiones

1. Las estructuras lineales permiten modelar de forma directa procesos comunes de bibliotecas (espera, historial y reversión) maximizando simplicidad y mantenibilidad.
2. El uso combinado de listas, colas y pilas mejora la experiencia de usuario (asignación justa vía FIFO) y facilita control transaccional básico mediante *undo*.
3. El prototipo es base para futuras extensiones (persistencia, GUI web, reportes).

## Referencias (APA 7ª ed.)

- Ayala San Martín, G. (2020). *Algoritmos y programación: mejores prácticas* (pp. 106–113). Fundación Universidad de las Américas Puebla.
- Fritelli, V., Guzman, A., & Tymoschuk, J. (2020). *Algoritmos y estructuras de datos* (2.ª ed., pp. 95–125, 257–299). Jorge Sarmiento Editor – Universitas.
- Ruiz Rodríguez, R. (2009). *Fundamentos de la programación orientada a objetos: una aplicación a las estructuras de datos en Java*. El Cid Editor.
- Zohonero Martínez, I., & Joyanes Aguilar, L. (2008). *Estructuras de datos en Java*. McGraw-Hill.
