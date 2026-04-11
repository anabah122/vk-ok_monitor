# Project Rules

## Singleton modules

Files that are singleton classes (e.g. `VkApi`) are named with PascalCase (capital first letter).
They are imported as a whole module, not destructured:

```python
import VkApi as VkApi
```
