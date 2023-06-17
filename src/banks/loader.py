from operator import itemgetter

from jinja2 import BaseLoader, FileSystemLoader, PackageLoader, TemplateNotFound


class MultiLoader(BaseLoader):
    """
    Similar to Jinja's ChoiceLoader with 2 notable differences:
      - Loaders can be added at runtime
      - Each loader has a priority so the caller can decide
        in which order the loaders are evaluated
    """

    def __init__(self) -> None:
        super().__init__()
        self._loaders: list[tuple[BaseLoader, int]] = []
        # add default loaders
        self.add_loader(PackageLoader("banks", "templates"), 10)
        self.add_loader(FileSystemLoader("templates"), 20)

    def add_loader(self, loader: BaseLoader, priority: int = 100) -> None:
        self._loaders.append((loader, priority))

    def get_source(self, environment, template):
        # Sort by priority, ascending
        for loader, _ in sorted(self._loaders, key=itemgetter(1)):
            try:
                return loader.get_source(environment, template)
            except TemplateNotFound:
                continue

        raise TemplateNotFound(template)
