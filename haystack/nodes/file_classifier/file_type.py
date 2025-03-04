import mimetypes
from typing import List, Union

from pathlib import Path
import magic
from haystack.nodes.base import BaseComponent


DEFAULT_TYPES = ["txt", "pdf", "md", "docx", "html"]


class FileTypeClassifier(BaseComponent):
    """
    Route files in an Indexing Pipeline to corresponding file converters.
    """

    outgoing_edges = 10

    def __init__(self, supported_types: List[str] = DEFAULT_TYPES):
        """
        Node that sends out files on a different output edge depending on their extension.

        :param supported_types: the file types that this node can distinguish.
            Note that it's limited to a maximum of 10 outgoing edges, which
            correspond each to a file extension. Such extension are, by default
            `txt`, `pdf`, `md`, `docx`, `html`. Lists containing more than 10
            elements will not be allowed. Lists with duplicate elements will
            also be rejected.
        """
        if len(supported_types) > 10:
            raise ValueError("supported_types can't have more than 10 values.")
        if len(set(supported_types)) != len(supported_types):
            duplicates = supported_types
            for item in set(supported_types):
                duplicates.remove(item)
            raise ValueError(f"supported_types can't contain duplicate values ({duplicates}).")

        super().__init__()

        self.supported_types = supported_types

    def _estimate_extension(self, file_path: Path) -> str:
        """
        Return the extension found based on the contents of the given file

        :param file_path: the path to extract the extension from
        """
        extension = magic.from_file(str(file_path), mime=True)
        return mimetypes.guess_extension(extension) or ""

    def _get_extension(self, file_paths: List[Path]) -> str:
        """
        Return the extension found in the given list of files.
        Also makes sure that all files have the same extension.
        If this is not true, it throws an exception.

        :param file_paths: the paths to extract the extension from
        :return: a set of strings with all the extensions (without duplicates), the extension will be guessed if the file has none
        """
        extension = file_paths[0].suffix.lower()
        if extension == "":
            extension = self._estimate_extension(file_paths[0])

        for path in file_paths:
            path_suffix = path.suffix.lower()
            if path_suffix == "":
                path_suffix = self._estimate_extension(path)
            if path_suffix != extension:
                raise ValueError(f"Multiple file types are not allowed at once.")

        return extension.lstrip(".")

    def run(self, file_paths: Union[Path, List[Path], str, List[str], List[Union[Path, str]]]):  # type: ignore
        """
        Sends out files on a different output edge depending on their extension.

        :param file_paths: paths to route on different edges.
        """
        if not isinstance(file_paths, list):
            file_paths = [file_paths]

        paths = [Path(path) for path in file_paths]

        output = {"file_paths": paths}
        extension = self._get_extension(paths)
        try:
            index = self.supported_types.index(extension) + 1
        except ValueError:
            raise ValueError(
                f"Files of type '{extension}' ({paths[0]}) are not supported. "
                f"The supported types are: {self.supported_types}. "
                "Consider using the 'supported_types' parameter to "
                "change the types accepted by this node."
            )
        return output, f"output_{index}"
