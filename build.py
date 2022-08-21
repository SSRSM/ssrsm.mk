import os, glob, re, shutil

BUILD_FOLDER = "./build"
COMPONENTS_FOLDER = "./components"

def build_path(path):
	return os.path.join(BUILD_FOLDER + ("" if BUILD_FOLDER[-1] == "/" else "/"), path)

for filename in os.listdir(BUILD_FOLDER):
	file_path = build_path(filename)
	if os.path.isfile(file_path) or os.path.islink(file_path):
		os.unlink(file_path)
	elif os.path.isdir(file_path):
		shutil.rmtree(file_path)

print("🗑️  Deleted old build structure in " + BUILD_FOLDER + ".")

files_processed = 0
for idx, file in enumerate(glob.glob('**/*', recursive = True)):
	filename, file_extension = os.path.splitext(file)

	if file_extension == ".py" or file.startswith((BUILD_FOLDER, COMPONENTS_FOLDER)):
		continue

	if os.path.isdir(file):
		dir_name = build_path(file)
		os.mkdir(dir_name)
		print("📂 Made directory " + dir_name + ".")
		continue

	if file_extension != '.html':
		shutil.copyfile(file, build_path(file))
		continue

	with open(file, "r") as f:
		lines = f.readlines()
		new_lines = []

		for line in lines:
			component_matches = re.findall("={=.+=}=", line)

			if len(component_matches) != 0:
				component_match = component_matches[0]
				component_path = re.findall("(?<=={=).+(?=\(.*\)=}=)", component_match)[0]
				component_props_string = re.findall("(?<=\().+(?=\))", component_match)

				with open(component_path) as f:
					component_code = f.read()

					if len(component_props_string):
						component_props = component_props_string[0].split(';')

						for component_prop in component_props:
							prop_key, prop_value = component_prop.split('=')
							component_code = re.sub("-{-" + prop_key + "-}-", prop_value, component_code)
					
					for prop in re.findall("-{-.+-}-", component_code):
						component_code = re.sub(prop, "", component_code)

					before_component = re.findall("[ \t]+(?=={=)", line)
					if len(before_component):
						component_code = re.sub("\n", "\n" + before_component[0], component_code)
					new_line = line.replace(component_match, component_code)
					new_lines.append(new_line)

			else:
				new_lines.append(line)

		with open(build_path(file), "w") as buildf:
			buildf.writelines(new_lines)

	files_processed += 1
	print("✅ Done with " + str(files_processed) + "th file.")