import inspect
import httpx
print('httpx module file:', inspect.getsourcefile(httpx))
print('httpx.BaseTransport exists:', hasattr(httpx, 'BaseTransport'))
print('httpx version:', getattr(httpx, '__version__', 'unknown'))
