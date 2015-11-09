#     Copyright 2015, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
""" This to keep track of used modules.

    There is a set of root modules, which are user specified, and must be
    processed. As they go, they add more modules to active modules list
    and move done modules out of it.

    That process can be restarted and modules will be fetched back from
    the existing set of modules.
"""

from nuitka.containers.oset import OrderedSet
from nuitka.PythonVersions import python_version
from nuitka.utils import Utils

# One or more root modules, i.e. entry points that must be there.
root_modules = OrderedSet()

# To be traversed modules
active_modules = OrderedSet()

# Already traversed modules
done_modules = set()

# Uncompiled modules
uncompiled_modules = set()


def addRootModule(module):
    root_modules.add(module)


def getRootModules():
    return root_modules


def hasRootModule(module_name):
    for module in root_modules:
        if module.getFullName() == module_name:
            return True

    return False


def addUncompiledModule(module):
    uncompiled_modules.add(module)


def getUncompiledModules():
    return sorted(
        uncompiled_modules,
        key = lambda module : module.getFullName()
    )


def _normalizeModuleFilename(filename):
    if python_version >= 300:
        filename = filename.replace("__pycache__", "")

        suffix = ".cpython-%d.pyc" % (python_version // 10)

        if filename.endswith(suffix):
            filename = filename[:-len(suffix)] + ".py"
    else:
        if filename.endswith(".pyc"):
            filename = filename[:-3] + ".py"

    if Utils.basename(filename) == "__init__.py":
        filename = Utils.dirname(filename)

    return filename


def getUncompiledModule(module_name, module_filename):
    for uncompiled_module in uncompiled_modules:
        if module_name == uncompiled_module.getFullName():
            if Utils.areSamePaths(
                _normalizeModuleFilename(module_filename),
                _normalizeModuleFilename(uncompiled_module.filename)
            ):
                return uncompiled_module

    return None


def removeUncompiledModule(module):
    uncompiled_modules.remove(module)


def startTraversal():
    # Using global here, as this is really a singleton, in the form of a module,
    # pylint: disable=W0603
    global active_modules, done_modules

    active_modules = OrderedSet(root_modules)
    done_modules = set()

    for active_module in active_modules:
        active_module.startTraversal()


def addUsedModule(module):
    if module not in done_modules and module not in active_modules:
        active_modules.add(module)

        module.startTraversal()


def nextModule():
    if active_modules:
        result = active_modules.pop()
        done_modules.add(result)

        return result
    else:
        return None


def remainingCount():
    return len(active_modules)


def getDoneModules():
    return sorted(
        done_modules,
        key = lambda module : module.getFullName()
    )


def getDoneUserModules():
    return sorted(
        [
            module
            for module in
            done_modules
            if not module.isInternalModule()
            if not module.isMainModule()
        ],
        key = lambda module : module.getFullName()
    )


def removeDoneModule(module):
    done_modules.remove(module)
