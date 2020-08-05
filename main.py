from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Router
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from handlers import getAvatar, uploadAvatar
from config import config
import uvicorn
import io, json

async def default(request):
    return JSONResponse({
        "status": "i'm okay!",
        "code": 200
    })

app = Starlette(debug=config['web_config']['debug'])
app.add_middleware(ProxyHeadersMiddleware)

router = Router([
    Route('/avatars/uploadAvatar', endpoint=uploadAvatar.handler, methods=['POST']),
    Route('/{id:int}', endpoint=getAvatar.handler, methods=['GET']),
    Route('/', endpoint=default, methods=['GET'])
])
app.mount('', router)

if __name__ == '__main__':
    uvicorn.run(app, host=config['web_config']['host'], port=config['web_config']['port'])