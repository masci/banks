from operator import itemgetter
from typing import Optional

from jinja2 import BaseLoader, PackageLoader, TemplateNotFound


class MultiLoader(BaseLoader):
    """
    Similar to Jinja's ChoiceLoader with 2 notable differences:
      - Loaders can be added at runtime
      - Each loader has a priority so the caller can decide
        in which order the loaders are evaluated
    """

    def __init__(self) -> None:
        super().__init__()
        self._loaders: list(BaseLoader) = []
        # add a default loader
        self.add_loader(PackageLoader("banks", "templates"), 1)

    def add_loader(self, loader: BaseLoader, priority: Optional[int] = 100) -> None:
        self._loaders.append((loader, priority))

    def get_source(self, environment, template):
        # Sort by priority, ascending
        for loader, _ in sorted(self._loaders, key=itemgetter(1)):
            try:
                return loader.get_source(environment, template)
            except TemplateNotFound:
                continue

        raise TemplateNotFound(template)
