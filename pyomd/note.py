import os
import re
from pathlib import Path
from typing import Optional, Union

from pyomd.metadata import MetadataType, NoteMetadata


class Note:
    """A Markdown note.

    Attributes:
        path: path to the note on disk.
        metadata: NoteMetadata object, containing all of the notes metadata (frontmatter and inline)
        content: The note's content (frontmatter + text)
    """

    def __init__(self, path: Union[Path, str]):
        """Initializes XXX"""
        self.path: Path = Path(path)
        with open(self.path, "r") as f:
            self.content: str = f.read()
        self.metadata: NoteMetadata = NoteMetadata(self.content)

    def __repr__(self) -> str:
        return f'Note (path: "{self.path}")\n'

    def update_content(
        self,
        inline_how: str = "bottom",
        inline_inplace: bool = True,
        write: bool = False,
    ):
        """Updates the note's content.

        Args:
            inline_how:
                if "bottom" / "top", inline metadata is grouped at the bottom/top of the note.
                This is always the case for new inline metadata (that didn't exist in the previous note content)
            inline_inplace:
                Whether to update inline metadata in place or not. If False, the metadata is grouped
                according to "inline_how"
            write:
                Whether to write changes to the file on disk after updating the content.
                If write = False, the user needs to call Note.write() subsequently to write changes to disk,
                otherwise only the self.content attribute is modified (in memory).
        """
        self.content = self.metadata.update_content(
            self.content, inline_how=inline_how, inline_inplace=inline_inplace
        )
        if write:
            self.write()

    def write(self, path: Union[Path, None] = None):
        """Writes the note's content to disk."""
        p = self.path if path is None else path
        with open(p, "w") as f:
            f.write(self.content)

    def sub(self, pattern: str, replace: str, is_regex: bool = False):
        """Substitutes text within a note.

        Args:
            pattern:
                the pattern to replace (plain text or regular expression)
            replace:
                what to replace the pattern with
            is_regex:
                Whether the pattern is a regex pattern or plain text.
        """
        if not is_regex:
            pattern = re.escape(pattern)
        self.content = re.sub(pattern, replace, self.content)

    def print(self):
        """Prints the note content to the screen."""
        print(self.content)


class Notes:
    """A group of notes.

    Attributes:
        self.notes:
            list of Note objects
    """

    def __init__(self, paths: list[Path], recursive: bool = True):
        """Initializes a Notes object.

        Add paths to individual notes or to directories containing multiple notes.

        Args:
            paths:
                list of paths pointing to markdown notes or folders
            recursive:
                When given a path to a directory, whether to add notes
                from sub-directories too
        """
        self.notes: list[Note] = []
        self.add(paths=paths, recursive=recursive)

    def add(self, paths: list[Path], recursive: bool = True):
        """Adds new notes to the Notes object.

        Args:
            paths:
                list of paths pointing to markdown notes or folders
            recursive:
                When given a path to a directory, whether to add notes
                from sub-directories too
        """
        for pth in paths:
            assert pth.exists(), f"file or folder doesn't exist: '{pth}'"
            if pth.is_dir():
                for root, _, fls in os.walk(pth):  # type: ignore
                    for f_name in fls:  # type: ignore
                        pth_f: Path = Path(root) / f_name  # type: ignore
                        self.notes.append(Note(path=pth_f))
                    if not recursive:
                        break
            else:
                self.notes.append(Note(path=pth))

    def filter(
        self,
        starts_with: Optional[str] = None,
        ends_with: Optional[str] = None,
        pattern: Optional[str] = None,
        has_meta: Optional[list[tuple[str, list[str], MetadataType]]] = None,
    ):
        """Filters notes.

        Args:
            starts_with:
                keep notes which file name starts with the string
            ends_with:
                keep notes which file name ends with the string
            pattern:
                keep notes which file name matches the regex pattern
            has_meta:
                keep notes which contains the specified metadata.
                has_meta is a list of tuples:
                (key_name, l_values, meta_type)
                that correspond to the arguments of NoteMetadata.has()

        Returns:
            None. Filters notes from self.notes
        """
        if starts_with is not None:
            self.notes = [
                n for n in self.notes if str(n.path.name).startswith(starts_with)
            ]
        if ends_with is not None:
            self.notes = [n for n in self.notes if str(n.path.name).endswith(ends_with)]
        if pattern is not None:
            self.notes = [n for n in self.notes if re.match(pattern, str(n.path.name))]
        if has_meta is not None:
            include: list[bool] = []
            for note in self.notes:
                inc = True
                for (k, vals, meta_type) in has_meta:
                    if not note.metadata.has(k=k, l=vals, meta_type=meta_type):
                        inc = False
                include.append(inc)
            self.notes = [n for (n, inc) in zip(self.notes, include) if inc]
