from operator import itemgetter
from typing import Optional

from jinja2 import BaseLoader, PackageLoader, TemplateNotFound


class MultiLoader(BaseLoader):
    def __init__(self) -> None:
        super().__init__()
        self.loaders: list(BaseLoader) = []
        # default loader
        self.add_loader(PackageLoader("banks", "templates"), 1)

    def add_loader(self, loader: BaseLoader, priority: Optional[int] = 100) -> None:
        self.loaders.append((loader, priority))

    def get_source(self, environment, template):
        # Sort by priority, ascending
        for loader in sorted(self.loaders, key=itemgetter(1)):
            try:
                return loader.get_source(environment, template)
            except TemplateNotFound:
                continue

        raise TemplateNotFound
