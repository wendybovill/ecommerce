from os import path as os_path, makedirs
from datetime import datetime
import typing as t  # typing is optional but nice for clarity
from pathlib import Path
from decimal import Decimal
import pandas as pandas
import numpy as numpy
import json

class DoublyNode:
    def __init__(self, data, node_id, description):
        self.id = node_id
        self.data = data
        self.previous = None
        self.next = None
        self.name = f"Node-node{node_id if node_id is not None else id(self)}"
        self.description = f"Enter {self.name} description: {data if description is None else description}"

    def __str__(self):
        return f"Node({self.name}, {self.description}, {self.data})"
    
    def __repr__(self):
        return self.__str__()
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "data": self.data,
            "next": self.next.name if self.next else None,
            "previous": self.previous.name if self.previous else None
        }
           
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)


class DoublyLinkedList:
    def __init__(self, node_id=None):
        self.head = None
        self.tail = None
        self.size = 0
        self.node_id = node_id if node_id is not None else id(self)

    
    def append(self, data, node_id=None):
        """Add new nodes to the end of the list"""
        node = DoublyLinkedList(data, node_id)
        if self.head is None:
            self.head = self.tail = node
        else:
            node.previous = self.tail
            self.tail.next = node
            self.tail = node
        self.size += 1
        return node

    def append_current(self, node, data, node_id=None):
        """Add new node after the current node."""
        if node is None:
            raise ValueError("Append_current: Current node must have data")
        node = DoublyLinkedList(data, node_id)
        node.previous = node
        node.next = node.next
        if node.next is not None:
            node.next.previous = node
        else:
            self.tail = node
        node.next = node
        self.size += 1
        return node

    def delete(self, node):
        """Delete current node."""
        if node is None:
            return
        if node.previous is not None:
            node.previous.next = node.next
        else:
            self.head = node.next
        if node.next is not None:
            node.next.previous = node.previous
        else:
            self.tail = node.previous
        node.previous = node.next = None
        self.size -= 1

    # O(n) search for first node matching condition
    def search(self, condition):
        """Return first node for which condition(node.data) is True."""
        current = self.head
        while current is not None:
            if condition(current.data):
                return current
            current = current.next
        return None

    # Next in List
    # O(n)
    def next_in_list(self):
        out = []
        current = self.head
        while current is not None:
            out.append(current.data)
            current = current.next
        return out
    
    # Previous in List
    # O(n)
    def previous_in_list(self):
        out = []
        current = self.tail
        while current is not None:
            out.append(current.data)
            current = current.previous
        return out
    
    def get_next(self, current):
        if current is not None and current.next is not None:
            return current.next
        return current

    def get_previous(self, current):
        if current is not None and current.previous is not None:
            return current.previous
        return current

node = DoublyNode(data="First Node", node_id=1, description="This is the first node")
node2 = DoublyNode(data="Second Node", node_id=2, description="This is the second node")
node3 = DoublyNode(data="Third Node", node_id=3, description="This is the third node")
node4 = DoublyNode(data="Fourth Node", node_id=4, description="This is the fourth node")
node5 = DoublyNode(data="Fifth Node", node_id=5, description="This is the fifth node")
print(node)
print(node2)
print(node3)
print(node4)
print(node5)

    # @classmethod
    # def from_dict(cls, data: dict) -> "Node":
    #     node = cls(data["data"], data["name"], data["description"])
    #     if data["next"]:
    #         node.next = cls.from_dict(data["next"])
    #     if data["previous"]:
    #         node.previous = cls.from_dict(data["previous"])
    #     return node

