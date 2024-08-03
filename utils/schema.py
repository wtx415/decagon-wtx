from typing import List, Optional


class Node:
    """
    Represents a node with text and a tag.

    Attributes:
        text (str): The text content of the node.
        tag (str): The tag associated with the node.
        metadata (Optional[dict]): Additional metadata associated with the node.
    """

    def __init__(self, text: str, tag: str, metadata: Optional[dict] = None):
        """
        Initializes a Node instance.

        Args:
            text (str): The text content of the node.
            tag (str): The tag associated with the node.
            metadata (Optional[dict]): Additional metadata associated with the node. Defaults to an empty dictionary.
        """
        if metadata is None:
            metadata = {}

        self.text = text
        self.tag = tag
        self.metadata = metadata

    def __str__(self):
        return self.text

    def __repr__(self):
        text_repr = self.text.replace("\n", "\\n")[:20]
        return f"Node(text={text_repr}, tag={self.tag})"


class Chunk:
    """
    Represents a chunk of text with associated nodes.

    Attributes:
        text (Optional[str]): The text content of the chunk.
        nodes (Optional[List[Node]]): A list of Node objects associated with the chunk.
        metadata (Optional[dict]): Additional metadata associated with the chunk.
    """

    def __init__(
        self,
        text: Optional[str] = "",
        nodes: Optional[List[Node]] = None,
        metadata: Optional[dict] = None,
    ):
        """
        Initializes a Chunk instance.

        Args:
            text (Optional[str]): The text content of the chunk. Defaults to an empty string.
            nodes (Optional[List[Node]]): A list of Node objects associated with the chunk. Defaults to None.
            metadata (Optional[dict]): Additional metadata associated with the chunk. Defaults to an empty dictionary.
        """
        if nodes is None:
            nodes = []

        if metadata is None:
            metadata = {}

        self.text = text
        self.nodes = nodes
        self.metadata = metadata

    def __str__(self):
        return self.text

    def __repr__(self):
        # Escape newlines and limit to 20 characters for the representation.
        text_repr = self.text.replace("\n", "\\n")[:20]
        return f"Chunk(text={text_repr})"
