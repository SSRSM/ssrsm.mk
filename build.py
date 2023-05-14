import json
import os
import glob
import re
import shutil
from pickle import BUILD
import pathlib
from fnmatch import fnmatch

BUILD_FOLDER = "build"
COMPONENTS_FOLDER = "components"
SRC_FILES = glob.glob("dist/**/*", recursive=True)
TRANSLATION_FILE = "translations.json"
IGNORE_FILE = ".buildignore"

if os.path.exists(IGNORE_FILE):
    with open(IGNORE_FILE, "r", encoding="utf-8") as file:
        IGNORED_FILES = file.read().splitlines()
else:
    IGNORED_FILES = []


def build_path(path, locale=""):
    return os.path.join(BUILD_FOLDER + ("" if BUILD_FOLDER[-1] == "/" else "/"),
                        (locale + "/" if locale != "" else ""),
                        path)


if not os.path.exists(BUILD_FOLDER):
    os.mkdir(BUILD_FOLDER)
else:
    for filename in os.listdir(BUILD_FOLDER):
        file_path = build_path(filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

print("🗑️ Deleted old build structure in " + BUILD_FOLDER + ".")

translation_map = {}

with open(TRANSLATION_FILE, "r", encoding="utf-8") as f:
    raw_translation_map = f.read()
    translation_map = json.loads(raw_translation_map)

print("📖 Loaded translation files.")


def ordinal(n): return "%d%s" % (
    n, "tsnrhtdd"[(n//10 % 10 != 1)*(n % 10 < 4)*n % 10::4])


def matches_ignore(filename):
    for ignore in IGNORED_FILES:
        if fnmatch(filename, ignore):
            return True
    return False


locales = translation_map["locales"]

locale_idx_map = {}
for i in range(len(locales)):
    locale_idx_map[i] = locales[i]


for locale_idx, locale in enumerate(locales):
    print("🌐 Building locale", locale,
          "(" + str(locale_idx + 1) + "/" + str(len(locales)) + ")")

    os.mkdir(build_path("", locale))

    files_processed = 0
    for idx, file in enumerate(SRC_FILES):
        filename, file_extension = os.path.splitext(file)

        src_path = pathlib.Path(*pathlib.Path(file).parts[1:])

        is_ignored = matches_ignore(src_path)

        output_path = build_path(
            src_path, "" if is_ignored else locale)

        if is_ignored and locale_idx > 0:
            continue

        if os.path.isdir(file):
            dir_name = output_path
            os.mkdir(dir_name)
            print("📂 Made directory " + dir_name + ".")
            continue

        if file_extension != '.html':
            shutil.copyfile(file, output_path)
            continue

        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            new_lines = []

            for line in lines:
                def translate_line(tline):
                    translation_matches = re.findall("~{~.+~}~", tline)
                    if (len(translation_matches) != 0):
                        translation_match = translation_matches[0]
                        translation_key = re.findall(
                            "(?<=~{~).+(?=~}~)", translation_match)[0]
                        translation_value = translation_map[translation_key][locale_idx]
                        return tline.replace(
                            translation_match, translation_value)
                    return tline

                new_line = translate_line(line)

                component_matches = re.findall("={=.+=}=", line)
                if len(component_matches) != 0:
                    component_match = component_matches[0]
                    component_path = re.findall(
                        "(?<=={=).+(?=\(.*\)=}=)", component_match)[0]
                    component_props_string = re.findall(
                        "(?<=\().+(?=\))", component_match)

                    with open(component_path, encoding="utf-8") as f:
                        component_code = f.read()

                        if len(component_props_string):
                            component_props = component_props_string[0].split(
                                ';')

                            for component_prop in component_props:
                                prop_key, prop_value = component_prop.split(
                                    '=')
                                component_code = re.sub(
                                    "-{-" + prop_key + "-}-", prop_value, component_code)

                        for prop in re.findall("-{-.+-}-", component_code):
                            component_code = re.sub(prop, "", component_code)

                        before_component = re.findall("[ \t]+(?=={=)", line)
                        if len(before_component):
                            component_code = re.sub(
                                "\n", "\n" + before_component[0], component_code)

                        new_component_lines = []
                        for component_line in component_code.split("\n"):
                            new_component_lines.append(
                                translate_line(component_line))
                        component_code = "".join(new_component_lines)

                        new_line = line.replace(
                            component_match, component_code)

                new_line = re.sub("\%locale\%", locale, new_line)

                new_lines.append(new_line)

            with open(output_path, "w", encoding="utf-8") as buildf:
                buildf.writelines(new_lines)

        files_processed += 1
        print("✅ [", locale, "] Done with " +
              str(ordinal(files_processed)) + " file.")
