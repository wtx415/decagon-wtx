# Native Python packages
from typing import List, Optional

# Third-party packages
from bs4 import BeautifulSoup
from bs4.element import Tag

# Custom packages
from utils.schema import Chunk, Node


class HtmlParser:
    DEFAULT_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]
    DEFAULT_INSEPARABLE_TAGS = ["li"]

    def __init__(
        self,
        tags: Optional[List] = None,
        inseparable_tags: Optional[List] = None,
        chunk_size: Optional[int] = 750,
        chunk_size_buffer: Optional[int] = 30,
    ):
        if tags is None:
            tags = self.DEFAULT_TAGS

        if inseparable_tags is None:
            inseparable_tags = self.DEFAULT_INSEPARABLE_TAGS

        self.tags = tags
        self.inseparable_tags = set(inseparable_tags)
        self.chunk_size = chunk_size
        self.chunk_size_buffer = chunk_size_buffer

    @staticmethod
    def _commit_chunk(chunks: List[Chunk], current_chunk: Chunk):
        """
        Commits the current chunk to the list of chunks.

        Args:
            chunks (List[Chunk]): list of chunks.
            current_chunk (Chunk): current chunk to commit.
        """
        current_chunk.text = current_chunk.text.strip()
        if current_chunk.text:
            chunks.append(current_chunk)

    def _split_text_into_tags(self, text: str) -> List[Tag]:
        """
        Splits text into tags based on the specified tags.

        It uses BeautifulSoup to parse the text and extract the specified tags by recursively traversing the HTML page.

        Args:
            text (str): text to split.

        Returns:
            List[Tag]: list of tags.
        """
        tags = []

        def traverse(tag):
            if isinstance(tag, Tag):
                if tag.name in self.tags:
                    if tag.get_text().strip():
                        tags.append(tag)
                else:
                    for child in tag.children:
                        traverse(child)

        soup = BeautifulSoup(text, "html.parser")
        traverse(soup)

        return tags

    def _convert_tags_to_nodes(self, tags: List[Tag]) -> List[Node]:
        """
        Converts tags into nodes.

        This function converts the tags into nodes data structure that makes it easier to combine them into chunks.
        It will also combine consecutive inseparable tags of the same tag type into a single node. This is helpful to
        ensure tags such as list items from the same section are consolidated into a single node.

        Args:
            tags (List[Tag]): list of tags.

        Returns:
            List[Node]: list of nodes.
        """
        nodes = []

        for tag in tags:
            tag_text = tag.get_text().strip()
            if not tag_text:
                continue

            # Add a newline character to the end of the tag text
            tag_text = f"{tag_text}\n"

            if (
                tag.name in self.inseparable_tags
                and nodes
                and nodes[-1].tag == tag.name
            ):
                nodes[-1].text += tag_text
            else:
                node = Node(tag_text, tag.name)
                nodes.append(node)

        return nodes

    def _is_valid_chunk_size(
        self, current_chunk_text: str, new_chunk_text: str
    ) -> bool:
        """
        Checks if the new chunk text can be added to the current chunk text without exceeding the chunk size.

        Args:
            current_chunk_text (str): current chunk text.
            new_chunk_text (str): new node text.

        Returns:
            bool: True if the new node text can be added to the current chunk text, False otherwise.
        """
        return (
            len(current_chunk_text) + len(new_chunk_text)
            <= self.chunk_size + self.chunk_size_buffer
        )

    def _combine_nodes_into_chunks(self, nodes: List[Node], url: str) -> List[Chunk]:
        """
        Combines nodes into chunks based on the chunk size.

        Args:
            nodes (List[Node]): list of nodes.
            url (str): url of the webpage.

        Returns:
            List[Chunk]: list of chunks.
        """
        if not nodes:
            return []

        chunks = []
        current_chunk = Chunk(metadata={"url": url})

        for node in nodes:
            new_node_text = node.text.strip()
            if not new_node_text:
                continue

            new_node_text_with_newline = f"{new_node_text}\n"

            if self._is_valid_chunk_size(
                current_chunk.text, new_node_text_with_newline
            ):
                current_chunk.text += new_node_text_with_newline
                current_chunk.nodes.append(node)
            else:
                self._commit_chunk(chunks, current_chunk)
                current_chunk = Chunk(
                    new_node_text_with_newline, [node], metadata={"url": url}
                )

        if current_chunk.text.strip():
            self._commit_chunk(chunks, current_chunk)

        return chunks

    def parse(self, text: str, url: str) -> List[Chunk]:
        """Parses text into chunks that can be used for embedding / loaded into vector database.

        Args:
            text (str): text to parse. Should be the html content of a webpage.
            url (str): url of the webpage.

        Returns:
            List[Chunk]: list of chunks.
        """
        tags = self._split_text_into_tags(text)
        nodes = self._convert_tags_to_nodes(tags)
        return self._combine_nodes_into_chunks(nodes, url)
