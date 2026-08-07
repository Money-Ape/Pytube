from pythonforandroid.recipe import Recipe
import os, shutil

class FFmpegRecipe(Recipe):
    version = "1.0"
    url = None
    built_libraries = {
        "libffmpegbin.so": "."
    }

    def build_arch(self, arch):
        src = os.path.join(self.recipe_dir, arch.arch, "libffmpegbin.so")

        build_dir = self.get_build_dir(arch.arch)
        os.makedirs(build_dir, exist_ok=True)

        dst = os.path.join(build_dir, "libffmpegbin.so")
        shutil.copy2(src, dst)

recipe = FFmpegRecipe()