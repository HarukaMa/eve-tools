import html
import json
import os
import pickle
import sqlite3
from typing import Dict

import aiohttp_jinja2
import jinja2
import requests
from aiohttp import web

from dogmaAttributesLoader import load as attributes_load, dogmaAttribute
from dogmaEffectsLoader import load as effects_load, dogmaEffect
from typeDogmaLoader import load as dogma_load, Dogma

routes = web.RouteTableDef()

en = {}
enfsd = {}
zh = {}
zhfsd = {}
name_type_table = {}
type_table = {}
dogma = {}
attributes: Dict[int, dogmaAttribute] = {}
effects: Dict[int, dogmaEffect] = {}

def format_result(_id: str, e: str, z: str = None, key: str = "msgid"):
    result = {key: _id, "en": html.escape(e).replace("\n", "<br>")}
    if z is None:
        result["zh"] = html.escape("<<<NO DATA>>>")
    else:
        result["zh"] = html.escape(z).replace("\n", "<br>")
    return result


@routes.get("/")
@aiohttp_jinja2.template("index.jinja2")
async def index(request: web.Request):
    return


@routes.get("/msg")
@aiohttp_jinja2.template("msg.jinja2")
async def msg(request: web.Request):
    keyword = request.query.get("msg", "")
    result = []
    added = set()
    if keyword != "":
        for k, v in en.items():
            if str(k) == keyword or keyword.lower() in v[0].lower():
                try:
                    result.append(format_result(str(k), v[0], zh[k][0]))
                except KeyError:
                    result.append(format_result(str(k), v[0]))
                added.add(str(k))
        for k, v in zh.items():
            if (str(k) == keyword or keyword.lower() in v[0].lower()) and str(k) not in added:
                result.append(format_result(str(k), en[k][0], v[0]))
        for k, v in enfsd.items():
            if str(k) == keyword or keyword.lower() in v[0].lower():
                try:
                    result.append(format_result("fsd:%d" % k, v[0], zhfsd[k][0]))
                except KeyError:
                    result.append(format_result("fsd:%d" % k, v[0]))
                added.add("fsd:%d" % k)
        for k, v in zhfsd.items():
            if (str(k) == keyword or keyword.lower() in v[0].lower()) and "fsd:%d" % k not in added:
                result.append(format_result("fsd:%d" % k, enfsd[k][0], v[0]))

    return {"result": result, "kw": keyword}


@routes.get("/types")
@aiohttp_jinja2.template("types.jinja2")
async def types(request: web.Request):
    keyword = request.query.get("name", "")
    result = []
    added = set()
    matches = []
    if keyword != "":
        for k, v in enfsd.items():
            if keyword.lower() in v[0].lower():
                try:
                    matches.append((k, v[0], zhfsd[k][0]))
                except KeyError:
                    matches.append((k, v[0], "<<<NO DATA>>>"))
                added.add(k)
        for k, v in zhfsd.items():
            if keyword.lower() in v[0].lower() and k not in added:
                matches.append((k, enfsd[k][0], v[0]))
        try:
            if int(keyword) in type_table.keys():
                msgid = type_table[int(keyword)]["typeNameID"]
                result.append(format_result(keyword, enfsd[msgid][0], zhfsd[msgid][0], "type_id"))
        except:
            pass
        for msgid, e, z in matches:
            if msgid in name_type_table.keys():
                result.append(format_result(name_type_table[msgid], e, z, "type_id"))
    return {"result": result, "kw": keyword}


@routes.get("/types/{type_id}")
@aiohttp_jinja2.template("types_detail.jinja2")
async def types_detail(request: web.Request):
    try:
        type_id = int(request.match_info["type_id"])
    except:
        return web.Response(status=404)
    type_name = enfsd[type_table[type_id]["typeNameID"]][0]
    desc = enfsd[type_table[type_id]["descriptionID"]][0]
    dgm: Dogma = dogma[type_id]
    attrs = dgm.dogmaAttributes
    attr = []
    for attribute in attrs:
        a = {}
        name_id = attributes[attribute.attributeID].displayNameID
        if name_id is not None:
            name = enfsd[name_id][0]
        else:
            name = attributes[attribute.attributeID].name
        a["name"] = name
        a["id"] = attribute.attributeID
        a["value"] = attribute.value
        attr.append(a)
    effs = dgm.dogmaEffects
    eff = []
    for effect in effs:
        e = {}
        name_id = effects[effect.effectID].displayNameID
        if name_id is not None:
            name = enfsd[name_id][0]
        else:
            name = effects[effect.effectID].effectName
        desc_id = effects[effect.effectID].descriptionID
        if desc_id is not None:
            eff_desc = enfsd[desc_id][0]
        else:
            eff_desc = "No description"
        e["name"] = name
        e["id"] = effect.effectID
        e["desc"] = eff_desc
        eff.append(e)
    return {"name": type_name, "desc": html.escape(desc).replace("\n", "<br>"), "attr": attr, "eff": eff}


def load_files():
    global en, zh, enfsd, zhfsd, dogma, attributes, effects
    print("Loading localization data...")
    en = pickle.load(open("cache/localization_en-us.pickle", "rb"))[1]
    zh = pickle.load(open("cache/localization_zh.pickle", "rb"))[1]
    enfsd = pickle.load(open("cache/localization_fsd_en-us.pickle", "rb"))[1]
    zhfsd = pickle.load(open("cache/localization_fsd_zh.pickle", "rb"))[1]
    print("Loading types data...")
    conn = sqlite3.connect("cache/evetypes.static")
    c = conn.cursor()
    sql = "SELECT value FROM cache"
    c.execute(sql)
    result = c.fetchall()
    for i, in result:
        data = json.loads(i)
        name_type_table[data["typeNameID"]] = data["typeID"]
        type_table[data["typeID"]] = data
    print("Loading type dogma data...")
    dogma = dogma_load("cache/typedogma.fsdbinary")
    print("Loading dogma attributes data...")
    attributes = attributes_load("cache/dogmaattributes.fsdbinary")
    print("Loading dogma effects data...")
    effects = effects_load("cache/dogmaeffects.fsdbinary")

def main():
    bin_base = "http://binaries.eveonline.com/"
    res_base = "http://resources.eveonline.com/"
    print("Getting latest version info...")
    r = requests.get(bin_base + "eveclient_SISI.json")
    if not r.ok:
        print("Failed to get version info: %d" % r.status_code)
        exit(1)
    build = int(r.json()["build"])
    try:
        cached_version = int(open("cache/version.txt").readline())
    except:
        cached_version = 0
    if build <= cached_version:
        print("Using cached files for version %s" % build)
    else:
        os.makedirs("cache", exist_ok=True)
        print("Downloading client info of build %s..." % build)
        r = requests.get(bin_base + "eveonline_%s.txt" % build)
        if not r.ok:
            print("Failed to get client info: %d" % r.status_code)
            exit(1)
        files = r.text.split("\n")
        idx = None
        for f in files:
            file = f.split(",")
            if file[0] == "app:/resfileindex.txt":
                idx = file[1]
                break
        if idx is None:
            print("Failed to find resource index location!")
            exit(1)
        print("Downloading resource index...")
        r = requests.get(bin_base + idx)
        if not r.ok:
            print("Failed to download resource index: %d" % r.status_code)
            exit(1)
        files = r.text.split("\n")
        for f in files:
            file = f.split(",")
            if len(file) != 5:
                break
            fn = file[0]
            path = file[1]
            if fn == "res:/localization/localization_en-us.pickle":
                print("Downloading en-us localization data...")
                r = requests.get(res_base + path)
                if not r.ok:
                    print("Failed to download en-us localization data: %d" % r.status_code)
                    exit(1)
                open("cache/localization_en-us.pickle", "wb").write(r.content)
            elif fn == "res:/localization/localization_zh.pickle":
                print("Downloading zh localization data...")
                r = requests.get(res_base + path)
                if not r.ok:
                    print("Failed to download zh localization data: %d" % r.status_code)
                    exit(1)
                open("cache/localization_zh.pickle", "wb").write(r.content)
            elif fn == "res:/localizationfsd/localization_fsd_en-us.pickle":
                print("Downloading en-us fsd localization data...")
                r = requests.get(res_base + path)
                if not r.ok:
                    print("Failed to download en-us fsd localization data: %d" % r.status_code)
                    exit(1)
                open("cache/localization_fsd_en-us.pickle", "wb").write(r.content)
            elif fn == "res:/localizationfsd/localization_fsd_zh.pickle":
                print("Downloading zh fsd localization data...")
                r = requests.get(res_base + path)
                if not r.ok:
                    print("Failed to download zh fsd localization data: %d" % r.status_code)
                    exit(1)
                open("cache/localization_fsd_zh.pickle", "wb").write(r.content)
            elif fn == "res:/staticdata/evetypes.static":
                print("Downloading type info static data...")
                r = requests.get(res_base + path)
                if not r.ok:
                    print("Failed to download type info static data: %d" % r.status_code)
                    exit(1)
                open("cache/evetypes.static", "wb").write(r.content)
            elif fn == "res:/staticdata/typedogma.fsdbinary":
                print("Downloading type dogma static data...")
                r = requests.get(res_base + path)
                if not r.ok:
                    print("Failed to download type dogma static data: %d" % r.status_code)
                    exit(1)
                open("cache/typedogma.fsdbinary", "wb").write(r.content)
            elif fn == "res:/staticdata/dogmaattributes.fsdbinary":
                print("Downloading dogma attributes static data...")
                r = requests.get(res_base + path)
                if not r.ok:
                    print("Failed to download dogma attributes static data: %d" % r.status_code)
                    exit(1)
                open("cache/dogmaattributes.fsdbinary", "wb").write(r.content)
            elif fn == "res:/staticdata/dogmaeffects.fsdbinary":
                print("Downloading dogma effects static data...")
                r = requests.get(res_base + path)
                if not r.ok:
                    print("Failed to download dogma effects static data: %d" % r.status_code)
                    exit(1)
                open("cache/dogmaeffects.fsdbinary", "wb").write(r.content)
        open("cache/version.txt", "w").write(str(build))

    load_files()

    app = web.Application()
    app.add_routes(routes)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("template"))
    web.run_app(app, port=8001)


if __name__ == '__main__':
    main()