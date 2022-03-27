import asyncio
import websockets

import xbmc
import xbmcaddon
import xbmcgui


SERVICE_FN = 'Asyncio WS Test'


class Client:
    def __init__(self, url):
        self.url = url
        self.websocket = None
        self.dialog = None
        self.seq = 0

    async def echo(self, message: str = ''):
        self.seq += 1
        xbmc.log(f'{SERVICE_FN}: {self.seq}, Snd: {message}')
        try:
            await self.websocket.send(message)
            self.dialog.notification(f'{SERVICE_FN}: {self.seq}', f'Snd: {message}')
            result = await self.websocket.recv()
            xbmc.log(f'{SERVICE_FN}: {self.seq}, Rec: {result}')
            self.dialog.notification(f'{SERVICE_FN}: {self.seq}', f'Rec: {result}')
        except Exception as e:
            xbmc.log(f'{SERVICE_FN}: Exception {str(e)}')
            self.dialog.notification(f'{SERVICE_FN}: Exception {str(e)}', xbmc.LOGERROR)

    async def __aenter__(self):
        xbmc.log(f'{SERVICE_FN}: Starting')
        self.dialog = xbmcgui.Dialog()
        self.websocket = await websockets.connect(self.url)
        xbmc.log(f'{SERVICE_FN}: Connected')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.websocket.close()
        del self.dialog
        xbmc.log(f'{SERVICE_FN}: Stopped')


class Service(xbmc.Monitor):
    def __init__(self):
        super().__init__()
#        self.enabled = xbmcaddon.Addon().getSettingBool('enabled')

    async def run(self):
        xbmc.log(f'{SERVICE_FN}: run')
        try:
            async with Client("ws://echo.websocket.events/") as client:
                while not self.abortRequested():
                    await client.echo('Is there anybody out there?')
                    timer = 10
                    while timer and not self.abortRequested():
                        xbmc.sleep(1000)
                        timer -= 1
                        await asyncio.sleep(0)
        except Exception as e:
            xbmc.log(f'{SERVICE_FN}: Exception {str(e)}')
            xbmcgui.Dialog().notification(f'{SERVICE_FN}', str(e))
            await asyncio.sleep(0)
            raise
        finally:
            self.waitForAbort()


if __name__ == '__main__':
    xbmc.sleep(2000)
    service = Service()
    asyncio.run(
        service.run()
    )
    del service
