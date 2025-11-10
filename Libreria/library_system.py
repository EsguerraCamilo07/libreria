
from collections import deque
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import datetime
import json
import os

# ---------- Modelos ----------

@dataclass
class Book:
    id: int
    title: str
    author: str
    year: int
    copies: int = 1
    waitlist: deque = field(default_factory=deque)  # Cola de espera (FIFO)

    def available(self) -> bool:
        return self.copies > 0

@dataclass
class User:
    id: int
    name: str
    borrowed: List[int] = field(default_factory=list)  # IDs de libros

@dataclass
class Operation:
    """Registro para pila de deshacer (undo)."""
    kind: str  # "borrow" o "return"
    user_id: int
    book_id: int
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)


# ---------- Árbol binario de búsqueda para libros (no lineal) ----------
@dataclass
class BookNode:
    book: Book
    left: Optional['BookNode'] = None
    right: Optional['BookNode'] = None


class BookBST:
    """Árbol binario de búsqueda (clave: book.id) para acceso rápido por ID."""
    def __init__(self) -> None:
        self.root: Optional[BookNode] = None

    def insert(self, book: Book) -> None:
        node = BookNode(book)
        if self.root is None:
            self.root = node
            return
        cur = self.root
        while True:
            if book.id < cur.book.id:
                if cur.left is None:
                    cur.left = node
                    return
                cur = cur.left
            else:
                if cur.right is None:
                    cur.right = node
                    return
                cur = cur.right

    def search(self, book_id: int) -> Optional[Book]:
        cur = self.root
        while cur:
            if book_id == cur.book.id:
                return cur.book
            elif book_id < cur.book.id:
                cur = cur.left
            else:
                cur = cur.right
        return None

    def inorder(self) -> List[Book]:
        """Recorrido inorden (izquierda-raíz-derecha): libros ordenados por ID."""
        out: List[Book] = []
        def _in(node: Optional[BookNode]):
            if not node:
                return
            _in(node.left)
            out.append(node.book)
            _in(node.right)
        _in(self.root)
        return out

    def preorder(self) -> List[Book]:
        """Recorrido preorden (raíz-izquierda-derecha): útil para copiar/clonar el árbol."""
        out: List[Book] = []
        def _pre(node: Optional[BookNode]):
            if not node:
                return
            out.append(node.book)
            _pre(node.left)
            _pre(node.right)
        _pre(self.root)
        return out

    def postorder(self) -> List[Book]:
        """Recorrido postorden (izquierda-derecha-raíz): útil para eliminar nodos."""
        out: List[Book] = []
        def _post(node: Optional[BookNode]):
            if not node:
                return
            _post(node.left)
            _post(node.right)
            out.append(node.book)
        _post(self.root)
        return out

    def delete(self, book_id: int) -> bool:
        """Elimina un libro del árbol por su ID. Retorna True si se eliminó."""
        def _find_min(node: BookNode) -> BookNode:
            while node.left:
                node = node.left
            return node

        def _delete_node(node: Optional[BookNode], bid: int) -> Optional[BookNode]:
            if not node:
                return None
            
            if bid < node.book.id:
                node.left = _delete_node(node.left, bid)
            elif bid > node.book.id:
                node.right = _delete_node(node.right, bid)
            else:
                if not node.left:
                    return node.right
                elif not node.right:
                    return node.left
                successor = _find_min(node.right)
                node.book = successor.book
                node.right = _delete_node(node.right, successor.book.id)
            
            return node

        old_root = self.root
        self.root = _delete_node(self.root, book_id)
        return old_root != self.root or (self.root and self.search(book_id) is None)


# ---------- Árbol binario de búsqueda para libros por título ----------
@dataclass
class BookTitleNode:
    book: Book
    left: Optional['BookTitleNode'] = None
    right: Optional['BookTitleNode'] = None


class BookTitleBST:
    """Árbol binario de búsqueda (clave: book.title) para búsqueda alfabética."""
    def __init__(self) -> None:
        self.root: Optional[BookTitleNode] = None

    def insert(self, book: Book) -> None:
        node = BookTitleNode(book)
        if self.root is None:
            self.root = node
            return
        cur = self.root
        while True:
            if book.title.lower() < cur.book.title.lower():
                if cur.left is None:
                    cur.left = node
                    return
                cur = cur.left
            else:
                if cur.right is None:
                    cur.right = node
                    return
                cur = cur.right

    def search_by_title(self, title: str) -> Optional[Book]:
        """Búsqueda exacta por título."""
        cur = self.root
        title_lower = title.lower()
        while cur:
            if title_lower == cur.book.title.lower():
                return cur.book
            elif title_lower < cur.book.title.lower():
                cur = cur.left
            else:
                cur = cur.right
        return None

    def search_prefix(self, prefix: str) -> List[Book]:
        """Búsqueda por prefijo: devuelve todos los libros cuyo título comienza con el prefijo."""
        results: List[Book] = []
        prefix_lower = prefix.lower()
        
        def _search(node: Optional[BookTitleNode]):
            if not node:
                return
            if node.book.title.lower().startswith(prefix_lower):
                results.append(node.book)
            if prefix_lower <= node.book.title.lower():
                _search(node.left)
            _search(node.right)
        
        _search(self.root)
        return results

    def inorder(self) -> List[Book]:
        """Recorrido inorden: libros ordenados alfabéticamente por título."""
        out: List[Book] = []
        def _in(node: Optional[BookTitleNode]):
            if not node:
                return
            _in(node.left)
            out.append(node.book)
            _in(node.right)
        _in(self.root)
        return out


# ---------- Árbol binario de búsqueda para usuarios ----------
@dataclass
class UserNode:
    user: User
    left: Optional['UserNode'] = None
    right: Optional['UserNode'] = None


class UserBST:
    """Árbol binario de búsqueda (clave: user.id) para acceso rápido por ID."""
    def __init__(self) -> None:
        self.root: Optional[UserNode] = None

    def insert(self, user: User) -> None:
        node = UserNode(user)
        if self.root is None:
            self.root = node
            return
        cur = self.root
        while True:
            if user.id < cur.user.id:
                if cur.left is None:
                    cur.left = node
                    return
                cur = cur.left
            else:
                if cur.right is None:
                    cur.right = node
                    return
                cur = cur.right

    def search(self, user_id: int) -> Optional[User]:
        cur = self.root
        while cur:
            if user_id == cur.user.id:
                return cur.user
            elif user_id < cur.user.id:
                cur = cur.left
            else:
                cur = cur.right
        return None

    def inorder(self) -> List[User]:
        """Recorrido inorden: usuarios ordenados por ID."""
        out: List[User] = []
        def _in(node: Optional[UserNode]):
            if not node:
                return
            _in(node.left)
            out.append(node.user)
            _in(node.right)
        _in(self.root)
        return out


class Library:
    def __init__(self) -> None:
        self.books: List[Book] = []            # Lista (catálogo)
        self.users: List[User] = []            # Lista de usuarios
        self.history: List[Operation] = []     # Lista (historial)
        self.undo_stack: List[Operation] = []  # Pila (LIFO) para deshacer
        self.next_book_id = 1                  # "Arreglo" implícito de IDs
        self.next_user_id = 1
        self.book_bst = BookBST()              # Búsqueda por ID de libro
        self.book_title_bst = BookTitleBST()   # Búsqueda por título de libro
        self.user_bst = UserBST()              # Búsqueda por ID de usuario

    # Utilidades
    def _find_book(self, book_id: int) -> Optional[Book]:
        return self.book_bst.search(book_id)

    def _find_user(self, user_id: int) -> Optional[User]:
        return self.user_bst.search(user_id)

    # CRUD Libros
    def add_book(self, title: str, author: str, year: int, copies: int = 1) -> Book:
        book = Book(self.next_book_id, title, author, year, copies)
        self.books.append(book)
        self.book_bst.insert(book)
        self.book_title_bst.insert(book)
        self.next_book_id += 1
        return book

    def remove_book(self, book_id: int) -> str:
        """Elimina un libro del sistema (si no está prestado)."""
        book = self._find_book(book_id)
        if not book:
            return "Libro no encontrado."
        
        for user in self.users:
            if book_id in user.borrowed:
                return "No se puede eliminar: el libro está prestado."
        
        self.books = [b for b in self.books if b.id != book_id]
        self.book_bst.delete(book_id)
        return f"Libro '{book.title}' eliminado del sistema."

    def search_books(self, keyword: str) -> List[Book]:
        kw = keyword.lower()
        return [b for b in self.books if kw in b.title.lower() or kw in b.author.lower()]

    def search_by_title_exact(self, title: str) -> Optional[Book]:
        """Búsqueda exacta por título usando el árbol."""
        return self.book_title_bst.search_by_title(title)

    def search_by_title_prefix(self, prefix: str) -> List[Book]:
        """Búsqueda por prefijo de título usando el árbol."""
        return self.book_title_bst.search_prefix(prefix)

    # CRUD Usuarios
    def add_user(self, name: str) -> User:
        user = User(self.next_user_id, name)
        self.users.append(user)
        self.user_bst.insert(user)
        self.next_user_id += 1
        return user

    # Operaciones de préstamo / devolución
    def borrow_book(self, user_id: int, book_id: int) -> str:
        user = self._find_user(user_id)
        book = self._find_book(book_id)
        if not user or not book:
            return "Usuario o libro no encontrado."
        if book.available():
            book.copies -= 1
            user.borrowed.append(book.id)
            op = Operation("borrow", user_id, book_id)
            self.history.append(op)
            self.undo_stack.append(op)
            return f"Préstamo exitoso: '{book.title}' para {user.name}."
        else:
            # Sin copias, agregamos a cola de espera
            if user_id not in book.waitlist:
                book.waitlist.append(user_id)
                return f"No hay copias disponibles. {user.name} fue agregado a la lista de espera."
            return f"{user.name} ya está en la lista de espera."

    def return_book(self, user_id: int, book_id: int) -> str:
        user = self._find_user(user_id)
        book = self._find_book(book_id)
        if not user or not book:
            return "Usuario o libro no encontrado."
        if book_id in user.borrowed:
            user.borrowed.remove(book_id)
            book.copies += 1
            op = Operation("return", user_id, book_id)
            self.history.append(op)
            self.undo_stack.append(op)
            # Atender lista de espera si la hay
            if book.waitlist:
                next_user_id = book.waitlist.popleft()
                self.borrow_book(next_user_id, book_id)  # préstamo automático
                return f"Devolución registrada. Se prestó automáticamente a usuario en espera (ID {next_user_id})."
            return "Devolución registrada."
        return "El usuario no tenía este libro en préstamo."

    def undo_last(self) -> str:
        """Deshacer la última operación de préstamo/devolución (pila LIFO)."""
        if not self.undo_stack:
            return "No hay operaciones para deshacer."
        op = self.undo_stack.pop()
        if op.kind == "borrow":
            # revertir préstamo
            user = self._find_user(op.user_id)
            book = self._find_book(op.book_id)
            if user and book and op.book_id in user.borrowed:
                user.borrowed.remove(op.book_id)
                book.copies += 1
                return f"Se deshizo el préstamo de '{book.title}' a {user.name}."
        elif op.kind == "return":
            # revertir devolución (re-prestar si hay copia)
            user = self._find_user(op.user_id)
            book = self._find_book(op.book_id)
            if user and book and book.copies > 0:
                book.copies -= 1
                user.borrowed.append(op.book_id)
                return f"Se deshizo la devolución de '{book.title}' por {user.name}."
        return "No fue posible deshacer la última operación."

    # Reportes simples
    def list_books(self) -> str:
        if not self.books: return "Sin libros."
        lines = []
        for b in self.books:
            lines.append(f"[{b.id}] {b.title} - {b.author} ({b.year}) | copias: {b.copies} | espera: {list(b.waitlist)}")
        return "\n".join(lines)

    def list_books_ordered_by_id(self) -> str:
        """Lista libros ordenados por ID usando recorrido inorden del BST."""
        books = self.book_bst.inorder()
        if not books: return "Sin libros."
        lines = []
        for b in books:
            lines.append(f"[{b.id}] {b.title} - {b.author} ({b.year}) | copias: {b.copies}")
        return "\n".join(lines)

    def list_books_ordered_by_title(self) -> str:
        """Lista libros ordenados alfabéticamente por título usando recorrido inorden del BST."""
        books = self.book_title_bst.inorder()
        if not books: return "Sin libros."
        lines = []
        for b in books:
            lines.append(f"[{b.id}] {b.title} - {b.author} ({b.year}) | copias: {b.copies}")
        return "\n".join(lines)

    def list_users(self) -> str:
        if not self.users: return "Sin usuarios."
        lines = []
        for u in self.users:
            lines.append(f"[{u.id}] {u.name} | prestados: {u.borrowed}")
        return "\n".join(lines)

    def list_users_ordered(self) -> str:
        """Lista usuarios ordenados por ID usando recorrido inorden del BST."""
        users = self.user_bst.inorder()
        if not users: return "Sin usuarios."
        lines = []
        for u in users:
            lines.append(f"[{u.id}] {u.name} | prestados: {u.borrowed}")
        return "\n".join(lines)

    def save_to_json(self, filename: str = "biblioteca_data.json") -> str:
        """Guarda el estado completo de la biblioteca en un archivo JSON."""
        try:
            data = {
                "books": [
                    {
                        "id": b.id,
                        "title": b.title,
                        "author": b.author,
                        "year": b.year,
                        "copies": b.copies,
                        "waitlist": list(b.waitlist)
                    }
                    for b in self.books
                ],
                "users": [
                    {
                        "id": u.id,
                        "name": u.name,
                        "borrowed": u.borrowed
                    }
                    for u in self.users
                ],
                "next_book_id": self.next_book_id,
                "next_user_id": self.next_user_id
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return f"Datos guardados exitosamente en '{filename}'."
        except Exception as e:
            return f"Error al guardar: {str(e)}"

    def load_from_json(self, filename: str = "biblioteca_data.json") -> str:
        """Carga el estado de la biblioteca desde un archivo JSON."""
        try:
            if not os.path.exists(filename):
                return f"Archivo '{filename}' no encontrado."
            
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.books = []
            self.users = []
            self.history = []
            self.undo_stack = []
            self.book_bst = BookBST()
            self.book_title_bst = BookTitleBST()
            self.user_bst = UserBST()
            
            for book_data in data.get("books", []):
                book = Book(
                    id=book_data["id"],
                    title=book_data["title"],
                    author=book_data["author"],
                    year=book_data["year"],
                    copies=book_data["copies"],
                    waitlist=deque(book_data.get("waitlist", []))
                )
                self.books.append(book)
                self.book_bst.insert(book)
                self.book_title_bst.insert(book)
            
            for user_data in data.get("users", []):
                user = User(
                    id=user_data["id"],
                    name=user_data["name"],
                    borrowed=user_data.get("borrowed", [])
                )
                self.users.append(user)
                self.user_bst.insert(user)
            
            self.next_book_id = data.get("next_book_id", 1)
            self.next_user_id = data.get("next_user_id", 1)
            
            return f"Datos cargados exitosamente desde '{filename}'."
        except Exception as e:
            return f"Error al cargar: {str(e)}"


# ---------- Interfaz de consola ----------

def seed_data(lib: Library) -> None:
    # Libros
    lib.add_book("Estructuras de Datos en Python", "Zahonero & Joyanes", 2008, copies=2)
    lib.add_book("Algoritmos y Programación", "Ayala San Martín", 2020, copies=1)
    lib.add_book("Fundamentos de POO con EDD en Java", "Ruiz Rodríguez", 2009, copies=1)
    # Usuarios
    lib.add_user("Camilo Esguerra")
    lib.add_user("Ana Pérez")
    lib.add_user("Juan Gómez")

def menu_busquedas(lib: Library):
    """Submenú especializado en búsquedas usando árboles binarios."""
    while True:
        print("\n=== MENÚ DE BÚSQUEDAS (Árboles BST) ===")
        print("1. Buscar libro por ID (BST)")
        print("2. Buscar libro por título exacto (BST)")
        print("3. Buscar libros por prefijo de título (BST)")
        print("4. Buscar libro por palabra clave (Lista)")
        print("5. Listar libros ordenados por ID (Inorden BST)")
        print("6. Listar libros ordenados por título (Inorden BST)")
        print("7. Buscar usuario por ID (BST)")
        print("8. Listar usuarios ordenados por ID (Inorden BST)")
        print("0. Volver al menú principal")
        
        op = input("Elige una opción: ").strip()
        
        if op == "1":
            try:
                bid = int(input("ID del libro: "))
                book = lib._find_book(bid)
                if book:
                    print(f"[{book.id}] {book.title} - {book.author} ({book.year}) | copias: {book.copies}")
                else:
                    print("Libro no encontrado.")
            except ValueError:
                print("ID inválido.")
        elif op == "2":
            title = input("Título exacto del libro: ").strip()
            book = lib.search_by_title_exact(title)
            if book:
                print(f"[{book.id}] {book.title} - {book.author} ({book.year}) | copias: {book.copies}")
            else:
                print("Libro no encontrado.")
        elif op == "3":
            prefix = input("Prefijo del título: ").strip()
            results = lib.search_by_title_prefix(prefix)
            if not results:
                print("Sin resultados.")
            else:
                for b in results:
                    print(f"[{b.id}] {b.title} - {b.author} ({b.year}) | copias: {b.copies}")
        elif op == "4":
            kw = input("Palabra clave (título/autor): ").strip()
            res = lib.search_books(kw)
            if not res:
                print("Sin resultados.")
            else:
                for b in res:
                    print(f"[{b.id}] {b.title} - {b.author} ({b.year}) | copias: {b.copies}")
        elif op == "5":
            print(lib.list_books_ordered_by_id())
        elif op == "6":
            print(lib.list_books_ordered_by_title())
        elif op == "7":
            try:
                uid = int(input("ID del usuario: "))
                user = lib._find_user(uid)
                if user:
                    print(f"[{user.id}] {user.name} | prestados: {user.borrowed}")
                else:
                    print("Usuario no encontrado.")
            except ValueError:
                print("ID inválido.")
        elif op == "8":
            print(lib.list_users_ordered())
        elif op == "0":
            break
        else:
            print("Opción no válida.")

def menu():
    lib = Library()
    seed_data(lib)
    acciones = {
        "1": "Listar libros",
        "2": "Agregar libro",
        "3": "Eliminar libro",
        "4": "Registrar usuario",
        "5": "Listar usuarios",
        "6": "Prestar libro",
        "7": "Devolver libro",
        "8": "Deshacer última operación",
        "9": "BÚSQUEDAS (usando árboles BST)",
        "10": "Guardar datos (JSON)",
        "11": "Cargar datos (JSON)",
        "0": "Salir",
    }
    while True:
        print("\n=== Sistema de Biblioteca (Prototipo con Árboles) ===")
        for k,v in acciones.items():
            print(f"{k}. {v}")
        op = input("Elige una opción: ").strip()
        
        if op == "1":
            print(lib.list_books())
        elif op == "2":
            title = input("Título: ").strip()
            author = input("Autor: ").strip()
            try:
                year = int(input("Año: "))
                copies = int(input("Copias: "))
                book = lib.add_book(title, author, year, copies)
                print(f"Libro agregado: [{book.id}] {book.title}")
            except ValueError:
                print("Datos inválidos.")
        elif op == "3":
            try:
                bid = int(input("ID del libro a eliminar: "))
                print(lib.remove_book(bid))
            except ValueError:
                print("ID inválido.")
        elif op == "4":
            name = input("Nombre del usuario: ").strip()
            u = lib.add_user(name)
            print(f"Usuario creado: [{u.id}] {u.name}")
        elif op == "5":
            print(lib.list_users())
        elif op == "6":
            try:
                uid = int(input("ID usuario: "))
                bid = int(input("ID libro: "))
                print(lib.borrow_book(uid, bid))
            except ValueError:
                print("IDs inválidos.")
        elif op == "7":
            try:
                uid = int(input("ID usuario: "))
                bid = int(input("ID libro: "))
                print(lib.return_book(uid, bid))
            except ValueError:
                print("IDs inválidos.")
        elif op == "8":
            print(lib.undo_last())
        elif op == "9":
            menu_busquedas(lib)
        elif op == "10":
            filename = input("Nombre del archivo (default: biblioteca_data.json): ").strip()
            if not filename:
                filename = "biblioteca_data.json"
            print(lib.save_to_json(filename))
        elif op == "11":
            filename = input("Nombre del archivo (default: biblioteca_data.json): ").strip()
            if not filename:
                filename = "biblioteca_data.json"
            print(lib.load_from_json(filename))
        elif op == "0":
            print("Hasta luego.")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    menu()
