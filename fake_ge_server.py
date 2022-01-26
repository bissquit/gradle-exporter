from aiohttp import web


async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = '''{
    "pending" : 0,
    "requested" : 0,
    "ageMins" : 0,
    "requestWaitTimeSecs" : 0,
    "incomingRate1m" : 0.03221981766544038,
    "incomingRate5m" : 0.02219163413405735,
    "incomingRate15m" : 0.021373141599789678,
    "processingRate1m" : 0.03399783025186821,
    "processingRate5m" : 0.022374841163558885,
    "processingRate15m" : 0.021459615070953553
}'''
    return web.Response(text=text, headers={'Content-Type': 'application/json'})

app = web.Application()
app.add_routes([web.get('/', handle)])

if __name__ == '__main__':
    web.run_app(app, port=8081)
