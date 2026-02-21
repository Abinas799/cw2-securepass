from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, Iterable, Iterator, Optional, TypeVar, List, Tuple

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class _Node(Generic[K, V]):
    key: K
    value: V
    next: Optional["_Node[K, V]"] = None


class HashTable(Generic[K, V]):
    """
    Simple separate-chaining hash table (user-defined DS).
    - Average O(1) insert/lookup, worst-case O(n)
    """

    def __init__(self, capacity: int = 101) -> None:
        if capacity < 11:
            capacity = 11
        self._buckets: List[Optional[_Node[K, V]]] = [None] * capacity
        self._size = 0

    def _idx(self, key: K) -> int:
        return hash(key) % len(self._buckets)

    def __len__(self) -> int:
        return self._size

    def put(self, key: K, value: V) -> None:
        i = self._idx(key)
        head = self._buckets[i]
        cur = head
        while cur:
            if cur.key == key:
                cur.value = value
                return
            cur = cur.next
        self._buckets[i] = _Node(key=key, value=value, next=head)
        self._size += 1

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        i = self._idx(key)
        cur = self._buckets[i]
        while cur:
            if cur.key == key:
                return cur.value
            cur = cur.next
        return default

    def contains(self, key: K) -> bool:
        return self.get(key, None) is not None

    def remove(self, key: K) -> bool:
        i = self._idx(key)
        cur = self._buckets[i]
        prev: Optional[_Node[K, V]] = None
        while cur:
            if cur.key == key:
                if prev:
                    prev.next = cur.next
                else:
                    self._buckets[i] = cur.next
                self._size -= 1
                return True
            prev = cur
            cur = cur.next
        return False

    def keys(self) -> Iterator[K]:
        for node in self._iter_nodes():
            yield node.key

    def values(self) -> Iterator[V]:
        for node in self._iter_nodes():
            yield node.value

    def items(self) -> Iterator[Tuple[K, V]]:
        for node in self._iter_nodes():
            yield (node.key, node.value)

    def _iter_nodes(self) -> Iterator[_Node[K, V]]:
        for b in self._buckets:
            cur = b
            while cur:
                yield cur
                cur = cur.next
