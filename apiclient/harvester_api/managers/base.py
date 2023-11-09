import json
from weakref import ref

from pkg_resources import parse_version

DEFAULT_NAMESPACE = "default"


def merge_dict(src, dest):
    for k, v in src.items():
        if isinstance(dest.get(k), dict) and isinstance(v, dict):
            merge_dict(v, dest[k])
        else:
            dest[k] = v
    return dest


class BaseManager:
    support_to = "0.0.0"

    @classmethod
    def is_support(cls, target_version):
        return parse_version(target_version) >= parse_version(cls.support_to)

    @classmethod
    def for_version(cls, version):
        for c in sorted(cls.__subclasses__(), reverse=True,
                        key=lambda x: parse_version(x.support_to).release):
            if c.is_support(version):
                return c.for_version(version)
        return cls

    def __init__(self, api, target_version=""):
        self._api = ref(api)
        self._ver = target_version

    def __repr__(self):
        return f"<{self.__class__.__name__} for {self._ver!r}>"

    @property
    def api(self):
        if self._api() is None:
            raise ReferenceError("API object no longer exists")
        return self._api()

    def _delegate(self, meth, path, *, raw=False, **kwargs):
        func = getattr(self.api, meth)
        resp = func(path, **kwargs)

        if raw:
            return resp
        try:
            if "json" in resp.headers.get('Content-Type', ""):
                rval = resp.json()
            else:
                rval = resp.text
            return resp.status_code, rval
        except json.decoder.JSONDecodeError as e:
            return resp.status_code, dict(error=e, response=resp)

    def _get(self, path, *, raw=False, **kwargs):
        return self._delegate("_get", path, raw=raw, **kwargs)

    def _create(self, path, *, raw=False, **kwargs):
        return self._delegate("_post", path, raw=raw, **kwargs)

    def _update(self, path, data, *, raw=False, as_json=True, **kwargs):
        if as_json:
            kwargs.update(json=data)
        else:
            kwargs.update(data=data)

        return self._delegate("_put", path, raw=raw, **kwargs)

    def _delete(self, path, *, raw=False, **kwargs):
        return self._delegate("_delete", path, raw=raw, **kwargs)

    def _patch(self, path, *, raw=False, **kwargs):
        return self._delegate("_patch", path, raw=raw, **kwargs)

    def _inject_data(self, data):
        s = json.dumps(data).replace("{API_VERSION}", self.api.API_VERSION)
        return json.loads(s)
