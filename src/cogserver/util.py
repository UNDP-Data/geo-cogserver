from fastapi import FastAPI
from fastapi.dependencies.utils import get_parameterless_sub_dependant
from fastapi import Depends
def get_path_dependency(app:FastAPI=None, arg_name=None):
    """
    Extract the first dependency of any kind whose arg name is arg_name
    Used  in conjunction
    :param app:
    :param field_name:
    :return:
    """

    for r in app.routes:
        if hasattr(r, 'dependant') and r.dependant:
            for d in r.dependant.dependencies:
                if d.query_params:
                    fields = [f.name for f in d.query_params]
                    if arg_name in fields:
                        fi = fields.index(arg_name)
                        return r.dependant.dependencies[fi].call


def replace_dependency(app=None, new_dependency=None, arg_name=None):
    print('JUSSI')
    depends = Depends(new_dependency)
    for r in app.routes:
        if hasattr(r, 'dependant') and r.dependant:
            for d in r.dependant.dependencies:
                if d.query_params:
                    fields = [f.name for f in d.query_params]
                    if arg_name in fields:
                        #print(r.path)
                        fi = fields.index(arg_name)
                        old = r.dependant.dependencies.pop(fi)
                        r.dependant.dependencies.insert(  # type: ignore
                            fi,
                            get_parameterless_sub_dependant(
                                depends=depends, path=r.path_format  # type: ignore
                            ),
                        )
                        r.dependencies.extend([depends])
            #print([[e.call for n in e.query_params if n.name == arg_name] for e in r.dependant.dependencies if e])
            #print(r.dependencies)
